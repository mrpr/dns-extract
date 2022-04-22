FROM python:3
ADD getdomdata.py /
RUN pip install ultra_rest_client

ENTRYPOINT ["python", "./getdomdata.py"]



