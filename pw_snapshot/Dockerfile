# Build Environment: Playwright
FROM mcr.microsoft.com/playwright/python:v1.21.0-focal
RUN pip install mysql-connector
RUN pip install requests
RUN pip install Pillow
RUN pip install lxml


COPY . /home/pwuser
WORKDIR /home/pwuser

# CMD ["sleep", "216000"]
CMD [ "python", "app.py" ]