#Taken from lecture:
FROM python:3.8
ENV HOME /root
WORKDIR /root
COPY . .
#Download dependancies
RUN pip3 install -r requirements.txt
#Exposing the correct port
EXPOSE 8080
#Opening app.py unbuffered
CMD python3 -u app.py