FROM centos:centos7

# Install build requirements
RUN yum -y update && yum -y install wget make

# Move source to app directory
RUN mkdir -p /app
COPY . /app

# Build application
RUN source /app/setup-environment.sh && /app/build.py && /app/test-environment.py

VOLUME /data
WORKDIR /data

ENTRYPOINT ["/app/docker-entry-point.sh"]
CMD ["watchopticalmc", "--help"]