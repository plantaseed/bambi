import os
import subprocess
from typing import List
import json

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class Bambi:
    """ Will manage user environments. """

    def __init__(self):
        """ Will set up fetch credentials and configs """

        self._setup_gcloud()
        self.client = client.CoreV1Api()
        self.api_client = client.CoreV1Api(client.ApiClient())
        self.app_api_client = client.AppsV1Api(client.ApiClient())
        self.name = "user"
        self.namespace = "default"
        self.app = "code-server"  # Name of app
        self.image = "bambiliu/code-server:latest"

    def _setup_gcloud(self, local_dev=False):
        """ Will do the necessary terminal commands to setup gcloud. """

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + \
            "/certs_and_configs/key.json"
        self.user_config = yaml.safe_load(open('config.yaml'))

        p = subprocess.Popen(['gcloud', 'config', 'set', 'project', self.user_config["config"]
                              ["project"]["id"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        p = subprocess.Popen(['gcloud', 'config', 'set', 'compute/zone', self.user_config["config"]
                              ["project"]["zone"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        p = subprocess.Popen(['gcloud', 'auth', 'activate-service-account',
                              '--key-file=certs_and_configs/key.json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        p = subprocess.Popen(['gcloud', 'container', 'clusters', 'get-credentials', self.user_config["config"]
                              ["project"]["dev_cluster"]["name"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if not local_dev:
            config.load_incluster_config()
        else:
            config.load_kube_config()

    def _generate_workspace_name(self) -> str:
        """ Will return the new name for the workspace. """

        return self.app

    def _get_address_from_service(self, service) -> str:
        """ Will retrive the port and ip-address from the V1ServiceList object """
        port = ""
        ip = ""

        for item in self.client.list_namespaced_service("default").items:
            if self.name in item.metadata.name:
                port = str(item.spec.ports[0].node_port)

        ip = self.client.list_node().items[0].status.addresses[1].address
        print("ip= " + ip + ", port = " + port)
        return ip + ":" + port

    def upload_image_to_gcp(self) -> None:
        """ Will call scripts/upload_image.sh to upload the custom
        dockerfile to gcr. """

        subprocess.call("scripts/upload_image.sh")

    def get_password_to_workspace(self) -> str:
        """ Will print the password to the users workspace. """

        workspaces = self.list_all_workspaces()
        deployment_name = self._generate_workspace_name()
        name = None
        for workspace in workspaces:
            if deployment_name in workspace:
                name = workspace

        if name is None:
            raise f"Cannot find workspace {deployment_name}"

        resp = self.client.read_namespaced_pod_log(name, self.namespace)
        logs = resp.split("\n")
        for log in logs:
            if "Password:" in log:
                password = log.split("INFO  ", 1)[1]
                print(password)
                return password

        raise("Cannot find password for chosen workspace")

    def get_address_to_workspace(self) -> str:
        """ Will return the url to access the users workspace. """
        addr = ""
        try:
            resp = self.api_client.list_namespaced_service(
                self.namespace, pretty=True)
            addr = self._get_address_from_service(resp)
            print(f"This is the address to {self.name}'s workspace: {addr}")

        except ApiException as e:
            print(f"Exception when calling list_namespaced_pod: {e}\n")
        return addr

    def list_all_workspaces(self) -> List[str]:
        """ Will list all running workspaces in the dev cluster. """
        names = []
        try:
            resp = self.api_client.list_namespaced_pod(
                self.namespace, pretty=True)
            for item in resp.items:
                names.append(item.metadata.name)

        except ApiException as e:
            print(f"Exception when calling list_namespaced_pod: {e}\n")

        return names

    def _create_workspace_metadata(self) -> client.V1ObjectMeta:
        """ Create metadata needed to create a new workspace. """

        new_name = self._generate_workspace_name()

        meta = client.V1ObjectMeta()
        meta.name = new_name
        meta.namespace = self.namespace

        return meta

    def _create_workspace_service(self, metadata: client.V1ObjectMeta) -> None:
        """ Will create the load balancer service to serve the workspace. """

        body = client.V1Service()
        body.metadata = metadata

        spec = client.V1ServiceSpec()
        port = client.V1ServicePort(port=8443, protocol='TCP')
        spec.ports = [port]
        spec.selector = {"app": self.app}
        spec.type = "NodePort"

        body.spec = spec

        try:
            self.api_client.create_namespaced_service(
                self.namespace, body, pretty=True)

        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

    def _create_spec_template_code_server(self, username, password) -> client.V1PodTemplateSpec:
        """ Will create a template-spec for code-server. """

        template = client.V1PodTemplateSpec()
        template.metadata = client.V1ObjectMeta(labels={"app": self.app})

        name = self._generate_workspace_name()
        container = client.V1Container(name=name)
        container.name = self.app
        container.image = self.image
        container.image_pull_policy = "Always"
        container.security_context = {"privileged": True}
        port = client.V1ContainerPort(container_port=8443, name="https")
        container.ports = [port]

        container.command = ["/bin/sh"]
        container.args = ["./../.startup/startup.sh", username, password, str(
            yaml.safe_load(open('config.yaml'))), str(open("certs_and_configs/key.json").read())]

        containers = [container]

        spec = client.V1PodSpec(containers=containers)
        spec.security_context = {"privileged": True}
        template.spec = spec

        return template

    def _create_workspace_deployment(self, metadata: client.V1ObjectMeta, username, password) -> None:
        """ Will create the deployment for the code-server so each user
        gets it's own work environment. """

        body = client.V1Deployment()
        body.metadata = metadata

        template = self._create_spec_template_code_server(username, password)
        selector = client.V1LabelSelector(match_labels={"app": self.app})
        spec = client.V1DeploymentSpec(
            replicas=1, selector=selector, template=template)

        body.spec = spec

        try:
            resp = self.app_api_client.create_namespaced_deployment(
                self.namespace, body, pretty=True)
            print(f"Created workspace: {resp}")
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)

    def _check_if_workspace_exist(self) -> str:
        for item in self.client.list_namespaced_service("default").items:
            if self.name in item.metadata.name:
                ip = self.client.list_node(
                ).items[0].status.addresses[1].address
                port = str(item.spec.ports[0].node_port)
                return ip + ":" + port
        return ""

    def create_workspace(self, username, password):
        """ Will create a new workspace for a user and return the password
        and address to the workspace.

        Will scale up the kubernetes cluster to meet the demand of the new
        workspace."""

        workname = self.user_config["config"]["project"]["id"]
        p = subprocess.Popen(['gcloud', 'container', 'images', 'list-tags', 'gcr.io/' + workname +
                              '/custom_code_server', '--format=json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        tag_list = json.loads(stdout.decode("utf-8"))

        for i in range(len(tag_list)):
            if username in tag_list[i]["tags"]:
                self.image = 'gcr.io/' + \
                    self.user_config["config"]["project"]["id"] + \
                    '/custom_code_server:' + username
                break
            elif "base" in tag_list[i]["tags"]:
                self.image = "gcr.io/" + \
                    self.user_config["config"]["project"]["id"] + \
                    "/custom_code_server:base"

        print("image = ", self.image)

        addr = self._check_if_workspace_exist()
        if addr != "":
            return addr

        metadata = self._create_workspace_metadata()
        self._create_workspace_deployment(metadata, username, password)
        self._create_workspace_service(metadata)
        return ""

    def delete_workspace(self, user="") -> None:
        """ Will delete the users workspace """

        body = client.V1DeleteOptions()
        name = self._generate_workspace_name()
        body.grace_period_seconds = 1

        # Delete deployment
        resp = self.app_api_client.delete_namespaced_deployment(
            name, self.namespace, body=body)
        print(resp)
        print("Workspace deployment deleted")

        # Delete service
        resp = self.api_client.delete_namespaced_service(
            name, self.namespace, body=body)
        print(resp)
        print("Workspace service deleted")


if __name__ == '__main__':
    bambi = Bambi()
