# Prerequsites
1. A cluster used for development on GCP
2. Optional: A production cluster which is a copy of the development cluster.
3. Open development kluster firewall to accept tcp connections
4. Allow full access to all Cloud APIs on development kluster
5. Mabye allow legacy authorization, you might need to. 
6. Open a gcr.io registry.

# Setup
## Overview
To get the system working you have to deploy and expose the Bambi manager to you development kluster.
You also have to define a config describing your system and cluster.

## Manager.
This will describe the setup of Bambi manager.

### Deployment
You have to deploy the manager image to your cluster.
A example depolyment config:
``` YAML
apiVersion: apps/v1
kind: Deployment
metadata:
 labels:
   app: manager
 name: manager
spec:
 replicas: 1
 selector:
   matchLabels:
     app: manager
 template:
   metadata:
     labels:
       app: manager
   spec:
     containers:
     - image: dockerhub.io/skira-bambi/manager:latest
       name: manager
       ports:
       - containerPort: 5000
       resources: {}
       imagePullPolicy: IfNotPresent
     hostname: manager
     restartPolicy: Always
```
Don't forget to expose the service, either add it to you ingress och just start a loadbalancer.

### Config
When you first open the manager you should first enter a config file, it should have the following format.
``` Yaml
services:
  #below list the names of your micro services
  service_name_1: 
    path:           #the path to folder which you service is located
    mountPath:      #!optional! The folder you want to mount to your Docker container while developing using a specific hot reload option
  service_name_2:
    path:           #the path to folder which you service is located
    mountPath:      #!optional! The folder you want to mount to your Docker container while developing using a specific hot reload option
config:
  project:
    git_url:        #git repo url on the form: "github.com/user/project.git"
    id:             # "GCP project id"
    zone:           # "compute zone of cluster"
    dev_cluster:
      name:         #name of your cluster.
      git_branch:   #the git branch assosiated with the development cluster
    prod_cluster:
      name:         #!optional! name of your cluster.
      git_branch:   #the git branch assosiated with the production kluster
```
### Gcloud config
Before using the manager you have to use the google login on the Manager main page to authorise 
manager to use your gcp credentials


## Code-server
Manager will use the base image located in dockerhub.io/skira-bambi/code-server:latest.
This can be modified to install other libraies to be standard for all users.
Make a dockerfile in the following form
```dockerfile
FROM dockerhub.io/skira-bambi/code-server:latest
RUN sudo apt install -y "some library that you need"
#other setup that you might need 
```
You can then build and push this to you gcr under the tag custom_code_server:base and that will be used as base instead.

## Testing
During a git commit the system will run two test files, a file called unit test and one called integration test.
They should be located in most outer layer of you git folder. In these, specify what tests to run.
In the unit test; no system will have been built. In the integration test; the system will be up to date with your changes. Make integration tests against the dev cluster.

## Deployment
Deployment will be made to the cluster which matches the branch you are on. default will be the one used for the development cluster
### Limitations
Changes in a yaml file, like a service or deployment, will not be automatically updated. Please apply those to the relevant clusters. To add a service, you must first deploy it to your cluster and add it to the config yaml in the manager.
### Spinnaker
To use another library like spinnaker, leave the git_branch part of you manager config empty and no deployment will be made with the code-server. 

## Developing services.
To develop a service using Hot Reload you need to run the bambi-dev command. This will swap out one chosen deployment from the current cluster for a proxy created using Telepresence. There exists 3 varieties of this command, shown below:

```
bambi-dev <SERVICENAME>         (Hot reload from inside the container. Requires reload program e.g. Nodemon)
bambi-dev -a <SERVICENAME>      (Hot reload with the entire Docker container)
bambi-dev -h                    (Prints out information on how to use the bambi-dev command)
```

-a) Running the command with the -a flag reloads the entire Docker container for the chosen service at any code
changes to files within that services directory. Using this command you will be prompted to enter a local code-server port
you want the Docker container to run on and also the port of the service that currently exists on the specified cluster.

-h) Running the command with the -h flag prints out information about the bambi-dev command.

*) Running the command without any flag will make use of the mountPath in the config.yaml file for the project and it's then
up to the developer to use a reload framework inside the container (e.g. Nodemon) to reload and restart the program.
This can become very useful if rebuilding the entire container would take up too much time. Restarting the application
from within the container only takes a couple seconds at max.

To exit development, press Ctrl+c.
