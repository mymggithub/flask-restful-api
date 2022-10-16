From ubuntu
RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install flask && pip3 install flask-restful && pip3 install mysql-connector


COPY . /opt/source-code
WORKDIR /opt/source-code

CMD ["python3", "app.py"]