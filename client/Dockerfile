FROM node:alpine3.16

WORKDIR /bottle_neck_client

COPY package.json .

RUN npm install

COPY ./public ./public
COPY ./src ./src

ENTRYPOINT [ "npm", "run", "start" ]
