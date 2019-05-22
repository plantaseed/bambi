FROM ubuntu:18.04

#RUN mkdir /root/certs
#RUN openssl req -x509 -nodes -days 365 -subj "/C=SE/ST=Ostergotland/L=Linkoping/O=Skira AB/OU=Bambi" -newkey rsa:2048 -keyout /root/certs/MyKey.key -out /root/certs/MyCertificate.crt



RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt install -y curl
RUN apt-get install -y git-core
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz

# Installing the package
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh

# Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

RUN pip3 install flask && \
  pip3 install kubernetes && \
  pip3 install kubernetes-py && \
  pip3 install google-cloud-storage && \
  pip3 install pyopenssl

EXPOSE 5000

COPY ./startup.py ./
COPY ./cli_std_lib.py ./
COPY ./templates ./templates
COPY ./static ./static
COPY ./certs_and_configs ./certs_and_configs
COPY ./config.yaml ./


ENTRYPOINT ["python3","startup.py"]

# NOTE: Start
