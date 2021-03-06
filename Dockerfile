# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER @P3Geek

# Add the application resources URL
# RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

ADD . /ltc-twitter-sentiment-demo

# Update the soruces list and install basic applications
RUN apt-get update && apt-get install -y tar git curl nano wget dialog net-tools \
        build-essential python python-dev python-distribute python3-pip \ 
        &&  pip3 install -r /ltc-twitter-sentiment-demo/requirements.txt

#Environment (Keys are fake and are replaced at runtime)
# Bot keys
ENV APP_KEY  LwInchdbrgzrfxOAerglOt5GieCgqsdsfdYE3U
ENV APP_SECRET FJDjergerg5G8FergergLQViobcbergergSbBPdKvCwxU93JmOnIprtoeAimVLUXmyiM
ENV OAUTH_TOKEN 292erge771e-kxy3bhFTergergl2Kktyzu8ukzyikPScaesrfbuayqgq7gGW
ENV OAUTH_TOKEN_SECRET JFEaeFGGDeSHg3VQcccdI8Pfj7ghvnj67dh

# Size of bubble chart before reset
ENV MAX_CHART_SIZE 5000

# What to look for
ENV INCLUDE_TWITTER_HASH bigdata, devops, microservices

#Weighted Vector Tweet Handling
ENV PROBABLE_RETWEET 0
ENV PROBABLE_FOLLOW 0
ENV PROBABLE_FAVORITE 0
ENV PROBABLE_DO_NOTHING 100

# The web ports for Cloud Foundry
ENV PORT 8080

# Expose ports (same as PORT)
EXPOSE 8080

# Set the default directory where CMD will execute
WORKDIR /ltc-twitter-sentiment-demo

# Set the default command to execute
# when creating a new container
CMD python3 -u bot.py
