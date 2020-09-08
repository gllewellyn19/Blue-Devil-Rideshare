FROM python:3.8
RUN mkdir /srv/app
WORKDIR /srv/app
ADD requirements.txt .
RUN pip install -r requirements.txt
#ADD create.sql .
#RUN execute create.sql
ADD . . 
EXPOSE 8080
#CMD ["./start.sh"]