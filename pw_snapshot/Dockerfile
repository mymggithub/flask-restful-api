FROM mcr.microsoft.com/playwright/python:v1.21.0-focal
RUN apt-get update && apt-get install tesseract-ocr -y

COPY . /home/pwuser
WORKDIR /home/pwuser
RUN pip install -r requirements.txt

# CMD ["sleep", "216000"]
CMD [ "python3", "app.py" ]