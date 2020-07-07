Welcome to Blue Devil Rideshare, a convenient way for Duke students to carpool and help reduce the costs of gas money! 
These apps are delivered using docker containers. The flask app and the postgres database communicated with the docker 
network via a docker-compose.yml.

In order to launch this web app, you must first download Docker.
Download Docker here: https://www.docker.com/get-started

Then, git clone from the git directory at this link: https://github.com/gllewellyn19/Blue-Devil-Rideshare.git

Now use your terminal to cd into that directory and run docker-compose build then docker-compose up

Lastly, go to localhost:8080/rides/ and have fun exploring!