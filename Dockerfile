FROM python:3.10

WORKDIR /proxy_web
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN apk add --update python3-pip
RUN apt-get update && apt-get install python3-pip -y

COPY . /proxy_web
RUN python3.10 -m pip install --upgrade -r /proxy_web/requirements.txt
EXPOSE 9001

#CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9001", "--reload"]
