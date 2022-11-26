#/bin/bash

mkdir -p ./mongo_data
docker-compose -f ./load-data-docker-compose.yml build
DUID=${UID} DGID=${GID} docker-compose -f ./load-data-docker-compose.yml up --abort-on-container-exit
