FROM python:3.8
WORKDIR /Blue-Devil-RideshareDockerTest
ENV FLASK_APP Flask/controllers/rides.py
ENV FLASK_RUN_HOST 0.0.0.0
#RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN apt-get install libpq-dev -y
RUN pip install -r requirements.txt
COPY . .
WORKDIR /Blue-Devil-RideshareDockerTest/Flask
CMD ["flask", "run"]