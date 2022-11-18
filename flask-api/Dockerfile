From ubuntu
RUN apt-get update && apt-get install -y python3 python3-pip

COPY . /opt/source-code
WORKDIR /opt/source-code
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]