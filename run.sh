#/bin/bash

mkdir -p ./mongo_data
DUID=${UID} DGID=${GID} docker-compose up
