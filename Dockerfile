FROM python:3.12.0a6-slim-buster
WORKDIR /code
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ ./
CMD [ "python", "./app.py" ]
