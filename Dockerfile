FROM python:3.8
WORKDIR /Blue-Devil-RideshareDockerTest/Flask
ENV FLASK_APP /Flask/duke_ride_share 
#^doesn't work no matter what I try- can I just keep it in the other flask directory
ENV FLASK_RUN_HOST 0.0.0.0
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN apt-get install libpq-dev -y
RUN pip install -r requirements.txt
COPY . .
WORKDIR /Blue-Devil-RideshareDockerTest/Flask
#CMD ["flask", "run"]
#CMD ["./start.sh"]
CMD gunicorn --bind 0.0.0.0:8080 "duke_ride_share:create_app()"