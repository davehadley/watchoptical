FROM centos:centos7

# Move source to app directory
RUN mkdir -p /app
COPY . /app


# Install build requirements
RUN yum -y check-update && yum -y install wget

# Build application
RUN source /app/setup-environment.sh && /app/build.py && /app/test-environment.py

VOLUME /data
WORKDIR /data

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["watchopticalmc", "--help"]