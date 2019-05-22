
#Overview
Below will be a overview of the system and it's modules.
## Manager
This module handels the starting and stopping of code-server instances. located under the k8-cli map
## Code server
Code-server is a built on verison of the codercom coder image. It has a custom startup that setsup the enviroment.
### Deployment
Deployment is a part of the code-server, is resides in git hooks that are set in the starup of the code-server.
Precommit tests and build the images that has been changes.
pre-push pushes images to gcr and deploys them to the approriate cluster
### Testing
Testing is done in a pre-commit. Services are teleprecensed and the integrationtest
# Manager
????
## Future/needed fetures

# Code server

## Startup

### Future

## Deployment

### Future

## Testing

### Future


### Hot Reload - Today
The Hot Reload module is currently using the bambi-dev script. This script allows the developer
to chose between two options. To automatically rebuild the docker container at code changes to
the developing services folder or to use a reload program from inside the container. The latter of
these options requires the developer to themselves install a reload program like Nodemon inside the container.
The script then mounts the services folder into the container so the reload program can watch for live changes
and restart the service inside the container at code changes, saving a considerable amount of time in the process.
The script is currently dependent on the library Telepresence. This library allows
one to swap out a deployment from the specified cluster with a local proxy. This allows
one to run a local service as though if it's part of the cluster. Testing for the developing
service is thus easier as the developer can observe if the service they are developing
would disturb the rest of the cluster.

## Hot Reload - Future
For the future development of the Hot Reload module it's recommended to phase out
the use of Telepresence. The framework is currently a bit unstable when it comes to
switching back the original deployment. In some instances, if Telepresence isn't shut
down properly, it will remove the proxy deployment but not swap back to the original.
The original deployment isn't gone but just not assigned to any pod for the related service.
Example of when this might occur is when you are running Telepresence in a terminal and want
to quit using Ctrl+c. If Ctrl+c is pressed once the program will usually shut down
correctly and the service will be swapped back. If Ctrl+c is hold down however, Telepresence
might not have time to swap back the original deployment. Another reason to phase out
Telepresence is because the the code-server that uses the Hot Reload function is already
inside the cluster. Using telepresence to connect to the cluser is therefore not really necessary.
It does however, allow for easy delployment swaps. If one could skip having to start Telepresence
every single time one would run the Hot Reload script, alot of time would be saved. The script
currently used for the Hot Reload module, "bambi-dev", could also be improved. There is
room to easily integrate more flags which allows developers more freedom in the way they want to use
the Hot Reload mechanic. Another thing that could be improved with the current script is to automatically
assign ports for the "bambi-dev -a" command. In the current version you have to manually
lookup what port the service that runs the deployment you want to swap is using in order to
be able to use "bambi-dev -a".
