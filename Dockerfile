FROM python:3.10.8
RUN apt update && apt install -y ffmpeg
WORKDIR .
COPY main.py /main.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD python3 /main.py

ARG RADARR_API=unset!
ARG RADARR_HOST=unset!
ARG SONARR_API=unset!
ARG SONARR_HOST=unset!
ARG TMDB_API=unset!
ARG OUTPUT_DIRS=unset!
ARG SLEEP_TIME=unset!
ARG LENGTH_RANGE=unset!
ARG FILETYPE=unset!
ARG SKIP_INTROS=unset!
ARG THREAD_COUNT=unset!
ARG SUBS=unset!
ARG MOVIEPATH=unset!
ARG TVPATH=unset!

ENV RADARR_API=${RADARR_API} \
    RADARR_HOST=${RADARR_HOST} \
    SONARR_API=${SONARR_API} \
    SONARR_HOST=${SONARR_HOST} \
    TMDB_API=${TMDB_API} \
    OUTPUT_DIRS=${OUTPUT_DIRS} \
    SLEEP_TIME=${SLEEP_TIME} \
    LENGTH_RANGE=${LENGTH_RANGE} \
    FILETYPE=${FILETYPE} \
    SKIP_INTROS=${SKIP_INTROS} \
    THREAD_COUNT=${THREAD_COUNT} \
    SUBS=${SUBS} \
    MOVIEPATH=${MOVIEPATH} \
    TVPATH=${TVPATH}