# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-buster

# https://vsupalov.com/docker-shared-permissions/
ARG USER_ID
ARG GROUP_ID
RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user


# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
RUN apt-get update && apt-get install -y ffmpeg mkvtoolnix
# Copy local code to the container image.
ENV APP_HOME /home/app
WORKDIR $APP_HOME
COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/home/app"
# COPY run.py /app/.
RUN mkdir /home/app/tmp
RUN mkdir /home/videos

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
COPY entrypoint.sh /entrypoint.sh
# can't do open(file, "w") here... 
USER user
ENTRYPOINT ["/entrypoint.sh"]

# CMD exec 
