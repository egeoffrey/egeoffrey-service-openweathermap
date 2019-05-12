### MYHOUSE ###

### define base image
ARG MYHOUSE_SDK_VERSION
ARG ARCHITECTURE
FROM myhouseproject/myhouse-sdk-python:${ARCHITECTURE}-${MYHOUSE_SDK_VERSION}

### copy files into the image
COPY . $WORKDIR

### define the modules provided which needs to be started
ENV MYHOUSE_MODULES="service/openweathermap"

