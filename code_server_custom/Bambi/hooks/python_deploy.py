from git import Repo
import copy,os, time
from subprocess import call
services = ["server2", "server", "client2"]

class bambiDeploy:
    def __init__(self, repo_path, services):
        self.repo = Repo(repo_path)
        self.services = services

    def list_changed_services(self, fullpath=False):
        """returns list of all services staged in commit"""
        changed_files =  [ item.a_path for item in self.repo.index.diff("HEAD") ]
        services = copy.copy(self.services)
        changed_services = []
        for path in changed_files:
            for service in services:
                if service+"/" in path:
                    if fullpath:
                        changed_services.append(path.split(service+"/")[0]+service)
                    else:
                        changed_services.append(service)
                    services.remove(service)
        return changed_services

    def get_service_changes(self):
        """returns dict that contains information on when last a file in the service whas changed"""
        changed_files = [ item.a_path for item in self.repo.index.diff("HEAD") ]     
        changed_services = {serv:0 for serv in self.services}
        for path in changed_files:
            for service in services:
                if service+"/" in path:
                    try:
                        t = os.path.getmtime(path)
                    except:
                        break
                    if t > changed_services[service]:
                        changed_services[service] = t
                    break
        for service in list(changed_services.keys()):
            if changed_services[service] == 0:
                del changed_services[service]
            else:
                changed_services[service] = time.ctime(changed_services[service])
        return changed_services
       
    def list_changed_yamls(self):
        """returns list of all yaml files staged for commit"""
        changed_files =  [ item.a_path for item in self.repo.index.diff("HEAD") ]
        yamls = []
        for path in changed_files:
                if ".yaml" in path or ".yml" in path:
                    yamls.append(path)
        return yamls
