FROM python:3.8-buster

WORKDIR /app

COPY . /app

EXPOSE 8888

RUN pip install -r requirements.txt

CMD ["python3", "-u", "./cliente.py"]