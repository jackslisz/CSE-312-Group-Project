#Taken from lecture:
FROM python:3.11
ENV HOME /root
WORKDIR /root
COPY . .
#Download dependancies
RUN pip3 install -r requirements.txt
#Exposing the correct port
EXPOSE 8080
#Waiting for DB to start before running server.py
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
#Running server.py unbuffered
CMD /wait && python3 -u app.py