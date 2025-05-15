FROM python:3.10-slim

RUN apt-get update && apt-get install -y default-jdk unzip wget

RUN wget https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-5.4.0.zip && \
    unzip apache-jena-fuseki-5.4.0.zip && \
    mv apache-jena-fuseki-5.4.0 /fuseki

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ontology/Graduation.ttl /fuseki/data/Graduation.ttl

CMD bash -c "/fuseki/fuseki-server --update --mem /ontology & sleep 5 && python app.py"