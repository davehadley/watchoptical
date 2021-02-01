FROM ubuntu:20.04

# Move source to app directory
RUN mkdir -p /app
COPY . /app


# Install build requirements
RUN apt update && apt install wget

# Build application
RUN source /app/setup-environment.py && /app/build.py

VOLUME /data
WORKDIR /data

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["watchopticalmc", "--help"]