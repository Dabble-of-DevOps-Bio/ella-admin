FROM continuumio/miniconda3:latest

# This image is just to get the various cli tools I need for the aws eks service
# AWS CLI - Whatever the latest version is
# AWS IAM Authenticator - 1.12.7
# Kubectl - 1.12.7

ARG TERRAFORM_VERSION="0.12.28"
ARG AWS_IAM_AUTHENTICATION_VERSION="1.12.7"
ARG KUBECTL_VERSION="1.12.7"

RUN apt-get update -y; apt-get upgrade -y; \
    apt-get install -y curl vim-tiny vim-athena jq

WORKDIR /tmp

ENV PATH=/root/bin:$PATH
RUN echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
RUN echo 'alias l="ls -lah"' >> ~/.bashrc

RUN pip install --upgrade ipython awscli troposphere typing boto3 paramiko

# Install clis needed for kubernetes + eks

RUN curl -o aws-iam-authenticator \
    https://amazon-eks.s3-us-west-2.amazonaws.com/${AWS_IAM_AUTHENTICATOR_VERSION}/2019-03-27/bin/linux/amd64/aws-iam-authenticator
RUN chmod +x ./aws-iam-authenticator

RUN mkdir -p ~/bin && cp ./aws-iam-authenticator ~/bin/aws-iam-authenticator

RUN curl -o kubectl \
    https://amazon-eks.s3-us-west-2.amazonaws.com/${KUBECTL_VERSION}/2019-03-27/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl ~/bin/kubectl

WORKDIR /tmp

## Helm V3

RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
 && chmod 700 get_helm.sh \
 && ./get_helm.sh

## Terraform

RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
 && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
 && mv terraform /usr/local/bin \
 && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

WORKDIR /root

