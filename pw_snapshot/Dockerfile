# Build Environment: Playwright
FROM mcr.microsoft.com/playwright/python:v1.21.0-focal
RUN pip install mysql-connector
RUN pip install notebook


COPY . /home/pwuser
WORKDIR /home/pwuser

# CMD ["sleep", "216000"]
CMD [ "python", "app.py" ]