from pydantic import BaseSettings
import os

class CommonSettings(BaseSettings):
    APP_NAME: str = "Project 21"
    DEBUG_MODE: bool= True           #Debug Mode

class ServerSettings(BaseSettings):
    if 'FRONTEND_CONTAINER_NAME' in os.environ:         #FRONTEND_CONTAINER_NAME is set in the environment section of the docker-compose file
        FRONTEND_CONTAINER_NAME=os.getenv('FRONTEND_CONTAINER_NAME')
        print('FRONTEND_CONTAINER_NAME',FRONTEND_CONTAINER_NAME)
    else:
        FRONTEND_CONTAINER_NAME="localhost"
        print('FRONTEND_CONTAINER_NAME',FRONTEND_CONTAINER_NAME)
    # if 'BACKEND_CONTAINER_NAME' in os.environ:
    #     BACKEND_CONTAINER_NAME=os.getenv('BACKEND_CONTAINER_NAME')
    #     print('BACKEND_CONTAINER_NAME',BACKEND_CONTAINER_NAME)
    # else:
    #     BACKEND_CONTAINER_NAME="localhost"
    #     print("BACKEND_CONTAINER_NAME",BACKEND_CONTAINER_NAME)
    HOST: str = "0.0.0.0"        #Backend server running on host
    PORT: int = 8000
    CORS_ORIGIN=[
    "http://"+FRONTEND_CONTAINER_NAME+":3000",        #For Cross Origin Requests to be allowed as React runs on port 3000
    "https://"+FRONTEND_CONTAINER_NAME+":3000",
    "http://"+FRONTEND_CONTAINER_NAME+":5000",
    "https://"+FRONTEND_CONTAINER_NAME+":5000"
    ]

class DatabaseSettings(BaseSettings):
    if 'MONGO_CONTAINER_NAME' in os.environ:     #MONGO_CONTAINER_NAME is set in the environment section of the docker-compose file
        MONGO_CONTAINER_NAME=os.getenv('MONGO_CONTAINER_NAME')
        print('MONGO_CONTAINER_NAME',MONGO_CONTAINER_NAME)
    else:
        MONGO_CONTAINER_NAME="localhost"
        print('MONGO_CONTAINER_NAME',MONGO_CONTAINER_NAME)
    DB_URI: str = "mongodb://"+MONGO_CONTAINER_NAME+":27017"       #MongoDB running by default at localhost port 27017
    DB_NAME : str = "Project21Database"                #Name of DB
    DB_COLLECTION_USER: str = "user_collection"         #Collection Names
    DB_COLLECTION_PROJECT: str = "project_collection"
    DB_COLLECTION_DATA: str = "data_collection"
    DB_COLLECTION_MODEL: str = "model_collection"
    DB_COLLECTION_METRICS: str = "metrics_collection"
    DB_COLLECTION_INFERENCE: str = "inference_collection"

class Settings(CommonSettings,ServerSettings,DatabaseSettings):
    DATA_DATABASE_FOLDER: str = os.path.abspath(os.path.join(os.getcwd(),'Database'))           #All user project files will be stored in this location
    CONFIG_AUTO_YAML_FILE: str = os.path.abspath(os.path.join(os.getcwd(),'Files','config','autoConfig.yaml'))          #Config file template locations - used during training
    CONFIG_YAML_FOLDER: str = os.path.abspath(os.path.join(os.getcwd(),'Files','config'))
    CONFIG_PREPROCESS_YAML_FILE: str =os.path.abspath(os.path.join(os.getcwd(),'Files','config','preprocess_config.yaml'))
    CONFIG_MODEL_YAML_FILE: str=os.path.abspath(os.path.join(os.getcwd(),'Files','config','model.yaml'))
    CONFIG_TIMESERIES_MANUAL_FILE: str=os.path.abspath(os.path.join(os.getcwd(),'Files','config','timeseriesmanualconfig.yaml'))
    DATA_TEMP_FOLDER: str = os.path.abspath(os.path.join(os.getcwd(),'Database','TempFiles'))

    SAMPLE_DATASET_FOLDER: str = os.path.abspath(os.path.join(os.getcwd(),'Files','testDataset'))
    SAMPLE_DATASET_TIMESERIES: str = os.path.join(SAMPLE_DATASET_FOLDER,'ice_cream.csv')
    SAMPLE_DATASET_CLUSTERING: str = os.path.join(SAMPLE_DATASET_FOLDER,'jewellery.csv')
    SAMPLE_DATASET_CLASSIFICATION: str = os.path.join(SAMPLE_DATASET_FOLDER,'Iris.csv')
    SAMPLE_DATASET_REGRESSION: str = os.path.join(SAMPLE_DATASET_FOLDER,'cardata.csv')
    pass

settings=Settings()