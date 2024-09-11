FROM python:3.10

WORKDIR /app

COPY setup/requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY setup /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver_plus", "--cert-file", "cert.crt", "0.0.0.0:8000"]
