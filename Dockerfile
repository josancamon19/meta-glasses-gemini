FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install wkhtmltopdf --yes
RUN apt-get install -y ffmpeg

COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]