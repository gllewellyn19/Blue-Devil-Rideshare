FROM python:3.8
RUN mkdir /srv/app
WORKDIR /srv/app
RUN apt-get update -y
RUN apt-get install postgresql-client -y
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD load.sql .
RUN load.sql
ADD . . 
EXPOSE 8080
#CMD ["./start.sh"]