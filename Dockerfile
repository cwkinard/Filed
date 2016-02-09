############################################################
# Dockerfile to build Filed
# Based on debian
############################################################

FROM debian

MAINTAINER Will Kinard "wilsonkinard@gmail.com"

RUN apt-get update && apt-get install -y \
	python \
	python-dev \
	python-distribute \
	python-pip \
	git-core

# Clone Filed repo
RUN git clone https://github.com/cwkinard/Filed.git

WORKDIR /Filed

# Create necessary directories
RUN mkdir tmp && mkdir logs

# Copy in sensitive files and directories
COPY accounts.json accounts.json
COPY .credentials .credentials

# Install our requirements
RUN pip install -r requirements.txt

# Do the magic
ENTRYPOINT ["python", "Filed.py"]
CMD --logging_level DEBUG

