FROM python:3.8.10

LABEL version="2.0"
LABEL description="This is the docker image of the FastAPI Backend Server for Project21"
LABEL maintainers=["Curl Tech"]

COPY /Backend/ /Backend/Backend/
COPY /Files/ /Backend/Files/
COPY ["__init__.py","api.py","requirements.txt","./Backend/"]

WORKDIR /Backend/ 

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3","api.py"]