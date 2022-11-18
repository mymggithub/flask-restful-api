FROM mcr.microsoft.com/playwright/python:v1.21.0-focal
#RUN apt-get update && apt-get install python3-pip tesseract-ocr screen -y
#RUN python3 -m pip install --upgrade pip

COPY . /home/pwuser
WORKDIR /home/pwuser
RUN pip install -r requirements.txt

CMD ["bash", "note.sh"]