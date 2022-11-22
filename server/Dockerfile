FROM python:3.9.14-alpine3.16

WORKDIR /bottle_neck

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && mkdir data

COPY scripts src ./

ENTRYPOINT [ "./entrypoint.sh" ]
