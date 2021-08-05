FROM python:3.8.10

LABEL version="2.0"
LABEL description="This is the docker image of the FastAPI Backend Server for Project21"
LABEL maintainers=["Curl Tech"]

COPY /Backend/ /Backend/Backend/
COPY /Files/ /Backend/Files/
COPY ["__init__.py","api.py","requirements.txt","./Backend/"]

# Tell Python to not generate .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Turn off buffering => This ensures that python output is sent straight to the terminal 
ENV PYTHONUNBUFFERED 1

WORKDIR /Backend/ 
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3","api.py"]