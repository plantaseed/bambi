FROM codercom/code-server:1.939
RUN sudo apt update
RUN sudo apt install -y curl
RUN curl -s https://packagecloud.io/install/repositories/datawireio/telepresence/script.deb.sh | sudo bash
RUN sudo apt install --no-install-recommends -y telepresence


RUN sudo apt-get update && sudo apt-get install -y apt-transport-https
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
RUN sudo apt-get update
RUN sudo apt-get install -y kubectl

RUN sudo sudo apt-get install -y nodejs
RUN sudo apt-get install -y npm
RUN npm install express
RUN sudo apt-get install -y sudo
RUN sudo apt-get install -y lsb-release
# Downloading gcloud package
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz

# Installing the package
RUN sudo mkdir -p /usr/local/gcloud \
  && sudo tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && sudo /usr/local/gcloud/google-cloud-sdk/install.sh

# Install headless browsers for selenium testing

# Chrome
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
#RUN sudo sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
#RUN sudo apt-get update
#RUN sudo apt-get install google-chrome-stable -y
#RUN sudo apt-get install unzip -y

# RUN sudo apt-get install chromium-chromedriver
#RUN wget https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_linux64.zip && \
 # unzip chromedriver_linux64.zip && \
 # sudo mv chromedriver /usr/bin/chromedriver && \
 # sudo chown root:root /usr/bin/chromedriver && \
 # sudo chmod +x /usr/bin/chromedriver

# Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin
RUN sudo sudo apt-get -y install docker.io
RUN sudo apt-get install -y python3-pip

RUN pip3 install gitpython
RUN pip3 install pyyaml

 # pip3 install requests #& \
 # pip3 install selenium

#RUN sudo npm install -g mocha

# Certs
RUN sudo mkdir ~/certs && \
    sudo openssl req -batch -x509 -nodes -days 365 -newkey rsa:2048 -keyout ~/certs/MyKey.key -out ~/certs/MyCertificate.crt

RUN sudo apt-get install -y inotify-tools

RUN mkdir ../.startup
COPY ./startup.sh ../.startup/
COPY ./skira-bambi-0001-6b96709b20c1.json ../.startup/
COPY ./Bambi ../.Bambi
COPY ./bambi-dev ../.startup/
COPY ./extr_bambi ../.startup/
RUN sudo chmod +x /home/coder/.startup/bambi-dev
RUN sudo chmod +x /home/coder/.startup/extr_bambi
RUN sudo ln -s /home/coder/.startup/bambi-dev /usr/bin
RUN sudo ln -s /home/coder/.startup/bambi-dev /usr/local/bin
RUN sudo ln -s /home/coder/.startup/extr_bambi /usr/bin
RUN sudo ln -s /home/coder/.startup/extr_bambi /usr/local/bin

RUN sudo chmod  -R ugo+rwx /root
RUN sudo chmod  -R ugo+rwx /home
RUN sudo chmod  -R ugo+rwx /var
RUN sudo usermod -aG docker coder
RUN sudo gpasswd -a coder docker

# NOTE: Start with `sudo docker run -it -p 127.0.0.1:8443:8443 code-server-manual --cert=/root/certs/MyCertificate.crt --cert-key=/root/certs/MyKey.key --allow-http --no-auth`
# To use the generated certs
