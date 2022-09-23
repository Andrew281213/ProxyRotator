FROM python:3.10

WORKDIR /proxy_web
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /proxy_web/requirements.txt
#RUN apk add --update python3-pip
RUN apt-get update && apt-get install python3-pip -y
RUN python3.10 -m pip install --upgrade -r /proxy_web/requirements.txt
COPY ./app /proxy_web
EXPOSE 9001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9001"]
