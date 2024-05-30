FROM orthancteam/orthanc
COPY python /python/

RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r /python/requirements.txt --break-system-packages
