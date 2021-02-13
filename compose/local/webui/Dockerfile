FROM node:14.10.1-buster

RUN npm install -g @angular/cli@10.0.4

WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

RUN npm install

## If you are building your code for production
## RUN npm ci --only=production
