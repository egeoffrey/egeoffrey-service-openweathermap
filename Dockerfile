### EGEOFFREY ###

### define base image
ARG SDK_VERSION
ARG ARCHITECTURE
FROM egeoffrey/egeoffrey-sdk-alpine:${SDK_VERSION}-${ARCHITECTURE}

### copy files into the image
COPY . $WORKDIR
