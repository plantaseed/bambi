#!bin/bash
#TODO check validity
username=$1
password=$2
config=$3
key=$4
touch ../.startup/key.json
echo "$key" > ../.startup/key.json
gitrepo=`python3 -c "print($config['config']['project']['git_url'])"`
project_id=`python3 -c "print($config['config']['project']['id'])"`

git clone "https://$username:$password@$gitrepo"
dir_=`python3 -c "print('$gitrepo'.split('/')[-1].split('.git')[0])"`
rm -rf $dir_/.git/hooks/
cp -a ../.Bambi/hooks BambiTest/.git/
branch=`python3 -c "print($config['config']['project']['dev_cluster']['git_branch'])"`
python3 -c "import yaml; yaml.dump($config, open('../.startup/config.yaml', 'w'), default_flow_style=False)"
d=`pwd`
git -C $d/$dir_ checkout $branch
#Configures project and zone for deployment
gcloud config set project $project_id
gcloud config set compute/zone europe-north1-a

#Variables--------------------------------------------------------
CLUST=`python3 -c "print($config['config']['project']['dev_cluster']['name'])"`
KEYPATH="./../.startup/key.json"
#-----------------------------------------------------------------

# Authenticates the service account with .JSON key
gcloud auth activate-service-account --key-file=$KEYPATH
gcloud auth configure-docker


# Set the configuration file for kubectl (selecting correct cluster)
gcloud container clusters get-credentials $CLUST

#docker auth configure-docker

chmod +x $dir_/.git/hooks/pre-commit
chmod +x $dir_/.git/hooks/pre-push

case $username in 
  *@* )
    git config --global user.email $username
    ;;
   * )
    git config --global user.name $username
    git config --global user.email '<>'
esac

export PASSWORD=$password
sudo dockerd &


/usr/local/bin/code-server --cert=../certs/MyCertificate.crt --cert-key=../certs/MyKey.key --allow-http $dir_