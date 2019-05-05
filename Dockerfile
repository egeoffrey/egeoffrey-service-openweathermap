### MYHOUSE ###

### define your base image
## Use the small python alpine image if you don't have OS dependencies
FROM python:2.7-alpine
## Use the raspbian image if you have OS dependencies
#FROM resin/rpi-raspbian
#RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && apt-get update && apt-get install -y python-pip wget && apt-get clean && rm -rf /var/lib/apt/lists/*

### define variables and workdir
ENV WORKDIR=/myHouse \
    MYHOUSE_SDK_BRANCH=development
WORKDIR $WORKDIR

### install myHouse SDK
RUN pip install paho-mqtt requests tinynumpy && wget https://github.com/myhouse-project/myhouse-sdk/archive/$MYHOUSE_SDK_BRANCH.zip -O myhouse-sdk.zip && unzip myhouse-sdk.zip && mv myhouse-sdk-*/python $WORKDIR/sdk && rm -rf myhouse-sdk*

### install your module's dependencies
## python dependencies
#RUN pip install <package>
## OS dependencies (for python:2.7-alpine)
#RUN apk update && apk add <package> && rm -rf /var/cache/apk/*
## OS dependencies (for resin/rpi-raspbian)
#RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && apt-get update && apt-get install -y <package> && apt-get clean && rm -rf /var/lib/apt/lists/*

### copy your files into the image
COPY . $WORKDIR

### define the modules provided which needs to be started
ENV MYHOUSE_MODULES="service/openweathermap"

### run the module
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
