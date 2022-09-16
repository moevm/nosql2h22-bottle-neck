FROM mongo:6.0.1

RUN apt-get update && \
    apt-get install -y python3 \
                       python3-pip

WORKDIR /bottle_neck

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && mkdir data

COPY scripts src ./

ENTRYPOINT [ "./entrypoint.sh" ]
