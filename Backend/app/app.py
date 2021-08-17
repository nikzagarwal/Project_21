from operator import index
import os
import re
import shutil
from typing import List, Optional
import yaml
import numpy as np
from fastapi import FastAPI, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.datastructures import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import File
from fastapi.responses import JSONResponse, FileResponse
from yaml.loader import SafeLoader
from Backend.app.dbclass import Database
from Backend.app.config import settings
from Backend.app.routers.user import user_router
from Backend.app.routers.project import project_router
from Backend.app.routers.data import data_router
from Backend.app.routers.model import model_router
from Backend.app.routers.metrics import metrics_router
from Backend.app.routers.inference import inference_router
from Backend.app.helpers.allhelpers import CurrentIDs, ResultsCache, serialiseDict, serialiseList
from Backend.app.helpers.project_helper import create_project_id
from Backend.app.helpers.data_helper import get_clean_data_path
from Backend.app.helpers.metrics_helper import get_metrics
from Backend.app.helpers.model_helper import create_model_id, get_pickle_file_path
from Backend.app.schemas import AutoFormData, Project, TimeseriesFormData, PreprocessJSONFormData, ModelHyperParametersJSON
from Backend.utils import generate_project_folder, generate_project_auto_config_file, generate_project_manual_config_file, generate_project_timeseries_config_file, convertFile, deleteTempFiles, generate_random_id, encodeDictionary
from Files.auto import Auto
from Files.autoreg import AutoReg
from Files.auto_clustering import Autoclu
from Files.plot import plot
from Files.inference import Inference
from Files.preprocess import Preprocess
from Files.inference_preprocess import InferencePreprocess
from Files.training import training
from Files.timeseries_preprocess import TimeseriesPreprocess
from Files.timeseries import timeseries

origins=settings.CORS_ORIGIN

app=FastAPI()

app.include_router(user_router, tags=["User Collection CRUD Operations"])
app.include_router(project_router, tags=["Project Collection CRUD Operations"])
app.include_router(data_router, tags=["Data Collection CRUD Operations"])
app.include_router(model_router,tags=["Model Collection CRUD Operations"])
app.include_router(metrics_router,tags=["Metrics Collection CRUD Operations"])
app.include_router(inference_router,tags=["Inference Collection CRUD Operations"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Project21Database=Database()
currentIDs=CurrentIDs()
resultsCache=ResultsCache()
currentIDs.set_current_user_id(101)


@app.get('/')
def home(): 
    return JSONResponse({"Hello": "World","serverStatus":"Working"})

@app.on_event("startup")
def startup_mongodb_client():
    Project21Database.initialise(settings.DB_NAME)
    try:
        currentIDs.set_current_user_id(101)
        Project21Database.insert_one(settings.DB_COLLECTION_USER,{
                "userID":101,
                "name": "John Doe",
                "email": "johndoe@email.com",
                "username": "TheJohnDoe",
                "password": "password@Super@Secure",
                "listOfProjects": []
            })
        resultsCache.set_training_status(False)
    except Exception as e:
        print("An Error Occured: ",e)
        print("Duplicate Key Error can be ignored safely")
    pass

@app.on_event("shutdown")
def shutdown_mongodb_client():
    Project21Database.close()


@app.post('/convertFile')
def converting_uploaded_file(train:UploadFile=File(...)):
    convertedFilePath, originalFilePath=convertFile(train)
    return FileResponse(convertedFilePath,media_type="text/csv", filename="convertedFile.csv")

@app.post('/create',tags=["Auto Mode"])
def create_project(projectName:str=Form(...),mtype:str=Form(...),train: UploadFile=File(...)):
    inserted_projectID=0
    Operation=generate_project_folder(projectName,train)
    if Operation["Success"]:
        try:
            inserted_projectID=create_project_id(Project21Database)
            # inserted_modelID=create_model_id(Project21Database)
            currentIDs.set_current_project_id(inserted_projectID)
            # currentIDs.set_current_model_id(inserted_modelID)
            resultsCache.set_project_folder_path(Operation["ProjectFolderPath"])
            Project21Database.insert_one(settings.DB_COLLECTION_PROJECT,{
                "projectID":inserted_projectID,
                "projectName":projectName,
                "rawDataPath":Operation["RawDataPath"],
                "yDataAddress":None,
                "projectFolderPath":Operation["ProjectFolderPath"],
                "belongsToUserID": currentIDs.get_current_user_id(),
                "listOfDataIDs":[],
                "configFileLocation": None,
                "plotsPath": None,
                "edaPlotPath": None,
                "projectType": mtype,
                "target":None,
                "isAuto": None,
                "preprocessConfigFileLocation":None,
                "modelsConfigFileLocation": None
                })
            # Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
            #     "modelID": inserted_modelID,
            #     "modelName": "Default Model",
            #     "modelType": mtype,
            #     "belongsToUserID": currentIDs.get_current_user_id(),
            #     "belongsToProjectID": inserted_projectID
            # })
            try:
                result=Project21Database.find_one(settings.DB_COLLECTION_USER,{"userID":currentIDs.get_current_user_id()})
                if result is not None:
                    result=serialiseDict(result)
                    if result["listOfProjects"] is not None:
                        newListOfProjects=result["listOfProjects"]
                        newListOfProjects.append(inserted_projectID)
                        Project21Database.update_one(settings.DB_COLLECTION_USER,{"userID":result["userID"]},{"$set":{"listOfProjects":newListOfProjects}})
                    else:
                        Project21Database.update_one(settings.DB_COLLECTION_USER,{"userID":result["userID"]},{"$set":{"listOfProjects":[inserted_projectID]}})
            except Exception as e:
                print("An Error occured: ",e)
                return JSONResponse({"File Received": "Success", "Project Folder":"Success", "Database Update":"Partially Successful"})
        except Exception as e:
            print("An Error occured: ",e)
            return JSONResponse({"File Received": "Success","Project Folder":"Success","Database Update":"Failure"})
        return JSONResponse({"userID":currentIDs.get_current_user_id(),"projectID":inserted_projectID})
    else:
        return JSONResponse(Operation["Error"])

@app.post('/auto',tags=["Auto Mode"])
def start_auto_preprocessing_and_training(autoFormData:AutoFormData):
    autoFormData=dict(autoFormData)
    projectAutoConfigFileLocation, dataID, problem_type = generate_project_auto_config_file(autoFormData["projectID"],currentIDs,autoFormData,Project21Database)
    with open("logs.log","w") as f:
        f.close()
    resultsCache.set_training_status(False)
    if(problem_type=='regression'):
        automatic_model_training=AutoReg()
        Operation=automatic_model_training.auto(projectAutoConfigFileLocation)
    elif (problem_type=='classification'):
        automatic_model_training=Auto()
        Operation=automatic_model_training.auto(projectAutoConfigFileLocation)
    elif (problem_type=='clustering'):
        automatic_model_training=Autoclu()
        Operation=automatic_model_training.auto(projectAutoConfigFileLocation)

    if Operation["Successful"]:
        try:
            print("Hyperparams: ",Operation["hyperparams"])
            newHyperparams=encodeDictionary(Operation["hyperparams"])
            print("New Hyperparams: ",newHyperparams)
            print("Y Data Address: ", Operation["y_data"])
        except Exception as e:
            print("Some error above: ",e)
        try:
            if problem_type=="clustering":
                Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
                    "dataID": dataID,
                    "cleanDataPath": Operation["cleanDataPath"],
                    "target": autoFormData["target"],
                    "belongsToUserID": currentIDs.get_current_user_id(),
                    "belongsToProjectID": autoFormData["projectID"]
                })
                currentIDs.set_current_data_id(dataID)
            else:
                Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
                    "dataID": dataID,
                    "cleanDataPath": Operation["cleanDataPath"],
                    "yDataAddress": Operation["y_data"],
                    "target": autoFormData["target"],
                    "belongsToUserID": currentIDs.get_current_user_id(),
                    "belongsToProjectID": autoFormData["projectID"]
                })
                currentIDs.set_current_data_id(dataID)
        except Exception as e:
            print("An Error Occured: ",e)
            print("Could not insert into Data Collection")
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
                "modelID": dataID,
                "modelName": "Default Name",
                "modelType": problem_type,
                "pickleFolderPath": Operation["pickleFolderPath"],
                "pickleFilePath": Operation["pickleFilePath"],
                "hyperparams": newHyperparams,
                "belongsToUserID": autoFormData["userID"],
                "belongsToProjectID": autoFormData["projectID"],
                "belongsToDataID": dataID
            })
        except Exception as e:
            print("An Error Occured: ",e)
            print("Could not insert into Model DB")
        try:
            if problem_type!='clustering':                
                Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                    "belongsToUserID": autoFormData["userID"],
                    "belongsToProjectID": autoFormData["projectID"],
                    "belongsToModelID": dataID,
                    "addressOfMetricsFile": Operation["metricsLocation"],
                    "accuracy": Operation["accuracy"]
                })
            else:
                Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                    "belongsToUserID": autoFormData["userID"],
                    "belongsToProjectID": autoFormData["projectID"],
                    "belongsToModelID": dataID,
                    "addressOfMetricsFile": Operation["metricsLocation"],
                })
            result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":autoFormData["projectID"]})
            result=serialiseDict(result)
            if result is not None:
                if result["listOfDataIDs"] is not None:
                    newListOfDataIDs=result["listOfDataIDs"]
                    newListOfDataIDs.append(dataID)
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "listOfDataIDs":newListOfDataIDs,
                            "configFileLocation": projectAutoConfigFileLocation,
                            "isAuto": autoFormData["isauto"],
                            "target": autoFormData["target"]
                            }
                        })
                else:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "listOfDataIDs":[dataID],
                            "configFileLocation": projectAutoConfigFileLocation,
                            "isAuto": autoFormData["isauto"],
                            "target": autoFormData["target"]
                            }
                        })
                if (problem_type=='clustering'):
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "clusterPlotLocation":Operation["clusterPlotLocation"]
                        }
                    })
        except Exception as e:
            print("An Error occured: ",e)
            print({"Auto": "Success", "Database Insertion":"Failure", "Project Collection Updation": "Unsuccessful"})
            return JSONResponse({"Auto": "Success", "Database Insertion":"Failure", "Project Collection Updation": "Unsuccessful"})
        currentIDs.set_current_data_id(dataID)
        currentIDs.set_current_model_id(dataID)
        currentIDs.set_current_project_id(autoFormData["projectID"])

        resultsCache.set_clean_data_path(Operation["cleanDataPath"])
        resultsCache.set_metrics_path(Operation["metricsLocation"])
        resultsCache.set_pickle_file_path(Operation["pickleFilePath"])
        resultsCache.set_pickle_folder_path(Operation["pickleFolderPath"])
        resultsCache.set_training_status(True)
        with open("logs.log","a+") as f:
            f.write("\nPROJECT21_TRAINING_ENDED\n")
            f.write("\nPROJECT21_TRAINING_ENDED\n")
        return JSONResponse({
            "Successful":"True",
            "userID": currentIDs.get_current_user_id(),
            "projectID": autoFormData["projectID"],
            "dataID":dataID,
            "modelID": dataID,
            "hyperparams":newHyperparams
        })
    else:
        return JSONResponse({"Successful":"False"})


@app.get('/getMetrics/{projectID}/{modelID}',tags=["Auto Mode"])
def get_auto_generated_metrics(projectID:int,modelID:int):
    metricsFilePath=get_metrics(projectID,modelID,Project21Database)
    if (os.path.exists(metricsFilePath)):
        return FileResponse(metricsFilePath,media_type="text/csv", filename="metrics.csv")
    return {"Error": "Metrics File not found at path"}


@app.get('/downloadClean/{dataID}',tags=["Auto Mode"])
def download_clean_data(dataID:int):
    path=get_clean_data_path(dataID,Project21Database)       #Have to put dataID here
    if(os.path.exists(path)):
        return FileResponse(path,media_type="text/csv",filename="clean_data.csv")     #for this we need aiofiles to be installed. Use pip install aiofiles
    return {"Error":"Clean Data File not found at path"}


@app.get('/downloadPickle/{modelID}',tags=["Auto Mode"])
def download_pickle_file(modelID:int):
    path=get_pickle_file_path(modelID,Project21Database)       #Have to put modelID here
    if(os.path.exists(path+'.pkl')):
        print("Path: ",path)
        return FileResponse(path+'.pkl',media_type="application/octet-stream",filename="model.pkl")   #for this we need aiofiles to be installed. Use pip install aiofiles
    return {"Error":"File not found at path"}
# #     myfile=open(path,mode='rb')
#     return StreamingResponse(myfile,media_type="text/csv")    #for streaming files instead of uploading them


@app.get('/getPlots/{projectID}',tags=["Auto Mode"])
def get_plots(projectID:int):
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result is not None:
            result=serialiseDict(result)
            if (result["projectType"]=='clustering'):
                    return FileResponse(result["clusterPlotLocation"],media_type="text/html",filename="plot.html")
            if (result["projectType"]=='timeseries'):
                return FileResponse(result["plotLocation"],media_type="text/html",filename="plot.html")
            
            if result["isAuto"]:
                result_model=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"belongsToProjectID":projectID})
                if result_model is not None:
                    result_model=serialiseDict(result_model)
                    pickleFilePath=result_model["pickleFilePath"]

                result_data=Project21Database.find_one(settings.DB_COLLECTION_DATA,{"belongsToProjectID":projectID})
                if result_data is not None:
                    result_data=serialiseDict(result_data)
                    cleanDataPath=result_data["cleanDataPath"]
                    yDataAddress=result_data["yDataAddress"]
                    
                if result["projectType"]=='classification':
                    auto_mode=Auto()
                    plotFilePath=auto_mode.model_plot_classification(pickleFilePath,result['rawDataPath'],yDataAddress,result["projectFolderPath"])
                elif result["projectType"]=='regression':
                    auto_mode=AutoReg()
                    plotFilePath=auto_mode.model_plot_regression(pickleFilePath,result["rawDataPath"],yDataAddress,result["projectFolderPath"])
                try:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                        "$set": {
                            "plotsPath": plotFilePath
                        }
                    })
                except Exception as e:
                    print("An Error occured while storing the plot path into the project collection")
                return FileResponse(plotFilePath,media_type='text/html',filename='plot.html')
            else:
                result_model=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"belongsToProjectID":projectID})
                if result_model is not None:
                    result_model=serialiseDict(result_model)
                    pickleFilePath=result_model["pickleFilePath"]

                result_data=Project21Database.find_one(settings.DB_COLLECTION_DATA,{"belongsToProjectID":projectID})
                if result_data is not None:
                    result_data=serialiseDict(result_data)
                    cleanDataPath=result_data["cleanDataPath"]

                manual_mode=training()
                plotFilePath=manual_mode.model_plot(pickleFilePath,cleanDataPath,result["target"],result["projectFolderPath"])
                
                try:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                        "$set": {
                            "plotsPath": plotFilePath
                        }
                    })
                    return FileResponse(plotFilePath,media_type="text/html",filename="plot.html")
                except Exception as e:
                    print("An Error occured while storing the plot path into the project collection")
                return FileResponse(plotFilePath,media_type='text/html',filename='plot.html')
    except Exception as e:
        print("An Error Occured: ",e)
        return JSONResponse({"Plots": "Not generated"})

@app.get('/getEDAPlot/{projectID}')
def get_EDA_plot(projectID:int):
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result is not None:
            result=serialiseDict(result)
            if result["edaPlotPath"] is not None:
                return FileResponse(result["edaPlotPath"],media_type="text/html",filename="plot.html")
            else:
                plotFilePath=plot(result["rawDataPath"],result["projectFolderPath"])
                try:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                        "$set": {
                            "edaPlotPath": plotFilePath
                        }
                    })
                    return FileResponse(plotFilePath,media_type="text/html",filename="plot.html")
                except Exception as e:
                    print("An Error Occured: ",e)
    except Exception as e:
        print("An Error Occured: ",e)
        return JSONResponse({"Plots": "Not generated"})


@app.get('/getAllProjects',tags=["Auto Mode"])
def get_all_project_details(userID:int):
    listOfProjects=[]
    listOfAccuracies=[]
    listOfHyperparams=[]
    try:   
        print("project traversal")
        userProjects=Project21Database.find(settings.DB_COLLECTION_PROJECT,{"belongsToUserID":userID})
        for project in userProjects:
            project=serialiseDict(project)
            print("Project: ",project)
            if project["projectType"]=='clustering':
                listOfDataIDs=project["listOfDataIDs"]
                print("This project's listOfDataIDs: ",listOfDataIDs)
                if project["target"] is not None:
                    for dataID in listOfDataIDs:
                        project_model=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"belongsToUserID":userID,"belongsToProjectID":project["projectID"],"belongsToDataID":dataID})
                        project_model=serialiseDict(project_model)
                        print("project_model: ", project_model)
                        if project_model["hyperparams"] is not None:
                            hyperparams=project_model["hyperparams"]
                            listOfHyperparams.append(hyperparams)
                            print("listOfHyperparams",listOfHyperparams)
                    projectTemplate={
                        "projectID": project["projectID"],
                        "projectName": project["projectName"],
                        "target": project["target"],
                        "modelType": project["projectType"],
                        "listOfDataIDs": project["listOfDataIDs"],
                        "isAuto": project["isAuto"],
                        "accuracies":listOfAccuracies,
                        "listofHyperparams":listOfHyperparams
                    }
                    listOfProjects.append(projectTemplate)
                    listOfAccuracies=[]
                    listOfHyperparams=[]
            else:
                listOfDataIDs=project["listOfDataIDs"]
                print("This project's listOfDataIDs: ",listOfDataIDs)
                if project["target"] is not None:
                    for dataID in listOfDataIDs:
                        project_model=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"belongsToUserID":userID,"belongsToProjectID":project["projectID"],"belongsToDataID":dataID})
                        if project_model is not None:
                            project_model=serialiseDict(project_model)
                            print("project_model: ", project_model)
                            if project_model["hyperparams"] is not None:
                                listOfHyperparams.append(project_model["hyperparams"])
                                print("listOfHyperparams",listOfHyperparams)
                        projectMetrics=Project21Database.find_one(settings.DB_COLLECTION_METRICS,{"belongsToModelID":dataID})
                        if projectMetrics is not None:
                            projectMetrics=serialiseDict(projectMetrics)
                            if projectMetrics["accuracy"] is not None:
                                listOfAccuracies.append(projectMetrics["accuracy"])
                                print("listOfAccuracies",listOfAccuracies)
                    projectTemplate={
                        "projectID": project["projectID"],
                        "projectName": project["projectName"].title(),
                        "target": project["target"],
                        "modelType": project["projectType"],
                        "listOfDataIDs": project["listOfDataIDs"],
                        "isAuto": project["isAuto"],
                        "accuracies":listOfAccuracies,
                        "listOfHyperparams":listOfHyperparams
                    }
                    listOfProjects.append(projectTemplate)
                    listOfAccuracies=[]
                    listOfHyperparams=[]
    except Exception as e:
        print("An Error Occured: ",e)
        print("Unable to get all projects")
        return JSONResponse({"GetAllProjects":"Failed"})
    return listOfProjects


@app.post('/doInference',tags=["Auto Mode"])
def get_inference_results(projectID:int=Form(...),modelID:int=Form(...),inferenceDataFile: UploadFile=File(...)):
    newDataPath='/'
    pickleFilePath='/'
    path='/'
    inferenceDataResultsPath='/'
    isAuto=False
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result is not None:
            result=serialiseDict(result)
            isAuto=result["isAuto"]
    except Exception as e:
        print("An Error Occured: ",e)
        print("Could not find the project in the Project Collection")
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"modelID":modelID,"belongsToProjectID":projectID})
        if result is not None:
            result=serialiseDict(result)
            if result["pickleFilePath"] is not None:
                pickleFilePath=result["pickleFilePath"]
            if result["pickleFolderPath"] is not None:
                projectRunPath=os.path.join(result["pickleFolderPath"],os.pardir)
                path=os.path.join(projectRunPath,"inference_data")
                if(not os.path.exists(path)):
                    os.makedirs(path)
                newDataPath=os.path.join(path,'inference_data.csv')
            
            with open(newDataPath,"wb") as buffer:
                shutil.copyfileobj(inferenceDataFile.file,buffer)

            inference=Inference()
            inferenceDataResultsPath=inference.inference(pickleFilePath,newDataPath,path,isAuto)
            Project21Database.insert_one(settings.DB_COLLECTION_INFERENCE,{
                "newData": newDataPath,
                "results": inferenceDataResultsPath,
                "belongsToUserID": currentIDs.get_current_user_id(),
                "belongsToProjectID": projectID,
                "belongsToModelID": modelID
            })
            if os.path.exists(inferenceDataResultsPath):
                print({"Metrics Generation":"Successful"})
                return FileResponse(inferenceDataResultsPath,media_type="text/csv",filename="inference.csv")
    except Exception as e:
        print("An error occured: ", e)
        print("Unable to find model from model Collection")
        return JSONResponse({"Metrics Generation":"Failed"})
    

@app.get('/getPreprocessParam',tags=["Manual Mode"])
def get_preprocessing_parameters():
    yaml_json=yaml.load(open(settings.CONFIG_PREPROCESS_YAML_FILE),Loader=SafeLoader)
    return JSONResponse(yaml_json)

@app.post('/getHyperparams/{userID}/{projectID}',tags=["Manual Mode"])
def get_hyper_parameters(preprocessJSONFormData:dict, userID:int, projectID:int):
    preprocessJSONFormData=dict(preprocessJSONFormData)
    print(preprocessJSONFormData)
    preprocessConfigFileLocation, manualConfigFileLocation, dataID, problem_type, folderLocation = generate_project_manual_config_file(projectID,preprocessJSONFormData,Project21Database)
    preprocessObj=Preprocess()
    cleanDataPath=preprocessObj.manual_preprocess(preprocessConfigFileLocation, folderLocation)
    print(cleanDataPath)
    if os.path.exists(cleanDataPath):
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
                "dataID": dataID,
                "cleanDataPath": cleanDataPath,
                "target": preprocessJSONFormData["target_column_name"],
                "belongsToUserID": currentIDs.get_current_user_id(),
                "belongsToProjectID": projectID
            })
        except Exception as e:
            print("An Error Occured: ",e)
            print("Could not Insert into Data Collection")
        try:
            Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                "$set":{
                    "preprocessConfigFileLocation":preprocessConfigFileLocation,
                    "configFileLocation":manualConfigFileLocation,
                    "target":preprocessJSONFormData["target_column_name"]
                }
            })
        except Exception as e:
            print("An Error Occured: ",e)
            print("Could not Update the Project Collection")

        yaml_json=yaml.load(open(settings.CONFIG_MODEL_YAML_FILE),Loader=SafeLoader)
        return yaml_json

@app.post('/manual/{userID}/{projectID}',tags=["Manual Mode"])
def start_manual_training(userID:int,projectID:int,configModelJSONData:Optional[List]):
    print(configModelJSONData)
    with open("logs.log","w") as f:
        f.close()
    resultsCache.set_training_status(False)
    result_project=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
    if result_project is not None:
        configFileLocation=result_project["configFileLocation"]
        preprocessConfigFileLocation=result_project["preprocessConfigFileLocation"]

        modelsConfigFileLocation=os.path.join(os.path.dirname(result_project["preprocessConfigFileLocation"]),"userinputconfig.yaml")
    
    with open(modelsConfigFileLocation,"w") as f:
        yaml.dump(configModelJSONData,f)
        f.close()

    result_data=Project21Database.find_one(settings.DB_COLLECTION_DATA,{"belongsToProjectID":result_project["projectID"]})
    if result_data is not None:
        cleanDataPath=result_data["cleanDataPath"]
        dataID=result_data["dataID"]

    trainingObj=training()
    Operation = trainingObj.train(modelsConfigFileLocation,configFileLocation,preprocessConfigFileLocation,cleanDataPath) 
    modelID=generate_random_id()
    print("Hyperparameters: ",Operation["hyperparams"])
    print("Recieved Opertions: ",Operation)
    newHyperparams=encodeDictionary(Operation["hyperparams"])
    if Operation["Successful"]:
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
                "modelID": modelID,
                "modelName": "Default Name",
                "modelType": result_project["projectType"],
                "pickleFolderPath": Operation["pickleFolderPath"],
                "pickleFilePath": Operation["pickleFilePath"],
                "belongsToUserID": userID,
                "belongsToProjectID": projectID,
                "belongsToDataID": dataID,
                "hyperparams": newHyperparams
            })
        except Exception as e:
            print(e)
        print("insertion succesfull")
        if result_project["projectType"]!='clustering':                
            Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                "belongsToUserID": userID,
                "belongsToProjectID": projectID,
                "belongsToModelID": modelID,
                "addressOfMetricsFile": Operation["metricsLocation"],
                "accuracy": Operation["accuracy"]
            })
        else:
            Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                "belongsToUserID": userID,
                "belongsToProjectID": projectID,
                "belongsToModelID": modelID,
                "addressOfMetricsFile": Operation["metricsLocation"]
            })
        if result_project["listOfDataIDs"] is not None:
            if dataID not in result_project["listOfDataIDs"]:
                newListOfDataIDs=result_project["listOfDataIDs"]
                newListOfDataIDs.append(dataID)
                Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                    "$set":{
                        "listOfDataIDs":newListOfDataIDs,
                        "modelsConfigFileLocation":modelsConfigFileLocation,
                        "isAuto": False,
                        }
                    })
        else:
            Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                "$set":{
                    "listOfDataIDs":[dataID],
                    "modelsConfigFileLocation": modelsConfigFileLocation,
                    "isAuto": False
                    }
                })
        if (result_project["projectType"]=='clustering'):
            Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                "$set":{
                    "clusterPlotLocation":Operation["clusterPlotLocation"]
                }
            })
    print("if condtition executed")
    with open("logs.log","a+") as f:
        f.write("\nPROJECT21_TRAINING_ENDED\n")
        f.write("\nPROJECT21_TRAINING_ENDED\n")
    resultsCache.set_training_status(True)
    return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": projectID, "dataID":dataID, "modelID": modelID, "hyperparams":newHyperparams})


@app.post('/doManualInference',tags=["Manual Mode"])
def do_manual_inference(projectID:int=Form(...), modelID:int=Form(...), inferenceDataFile:UploadFile=File(...)):
    preprocessConfigFileLocation='/'
    isAuto=False
    pickleFilePath='/'
    projectRunPath='/'
    inferenceCleanDataLocation='/'
    path='/'
    newDataPath='/'
    inferenceDataResultsPath='/'
    # try:
    result_project=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
    if result_project is not None:
        result_project=serialiseDict(result_project)
        preprocessConfigFileLocation=result_project["preprocessConfigFileLocation"]
        isAuto=result_project["isAuto"]

    result_model=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"modelID":modelID,"belongsToProjectID":projectID})
    if result_model is not None:
        result_model=serialiseDict(result_model)
        if result_model["pickleFilePath"] is not None:
            pickleFilePath=result_model["pickleFilePath"]
        if result_model["pickleFolderPath"] is not None:
            projectRunPath=os.path.join(result_model["pickleFolderPath"],os.pardir)
            path=os.path.join(projectRunPath,"inference_data")
            if(not os.path.exists(path)):
                os.makedirs(path)
            newDataPath=os.path.join(path,'inference_data_original.csv')
        
        with open(newDataPath,"wb") as buffer:
            shutil.copyfileobj(inferenceDataFile.file,buffer)

        print("Performing Preprocessing of the data given")
        inferencePreprocessObj=InferencePreprocess()
        inferenceCleanDataLocation=inferencePreprocessObj.inference_preprocess(preprocessConfigFileLocation,path,newDataPath)
        print("Preprocessing of data is done")
        print("Performing Inference on the preprocessed inference data")
        inference=Inference()
        inferenceDataResultsPath=inference.inference(pickleFilePath,inferenceCleanDataLocation,path,isAuto)
        print("Inferencing completed")


        Project21Database.insert_one(settings.DB_COLLECTION_INFERENCE,{
            "newData": inferenceCleanDataLocation,
            "results": inferenceDataResultsPath,
            "belongsToUserID": currentIDs.get_current_user_id(),
            "belongsToProjectID": projectID,
            "belongsToModelID": modelID
        })
        if os.path.exists(inferenceDataResultsPath):
            print({"Metrics Generation":"Successful"})
            return FileResponse(inferenceDataResultsPath,media_type="text/csv",filename="inference.csv")
    # except Exception as e:
    #     print("An Error Occured: ",e)
    #     print("Could not do any of the above")

# Old Timeseries API - working
# @app.post('/timeseries',tags=["Timeseries"])
# def timeseries_training(timeseriesFormData: TimeseriesFormData):
#     print(timeseriesFormData)
#     timeseriesFormData=dict(timeseriesFormData)
#     projectConfigFileLocation, projectFolderPath, dataID, projectType = generate_project_timeseries_config_file(timeseriesFormData["projectID"],currentIDs,timeseriesFormData,Project21Database)
#     with open("logs.log","w") as f:
#         f.write("Time series Initiated\n")
#         f.write("Please wait setting up...\n")
#         f.write("Setting up Completed...\n")
#         f.write("Preprocessing the given data\n")
#         f.write("Preprocessing is done\n")
#         f.close()
#     timeseriesPreprocessObj=TimeseriesPreprocess()
#     cleanDataPath=timeseriesPreprocessObj.preprocess(projectConfigFileLocation,projectFolderPath)
#     try:
#         Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
#             "dataID": dataID,
#             "cleanDataPath": cleanDataPath,
#             "target": timeseriesFormData["target"],
#             "belongsToUserID": timeseriesFormData["userID"],
#             "belongsToProjectID": timeseriesFormData["projectID"]
#         })
#     except Exception as e:
#         print("Could not insert into Data Collection. An Error Occured: ",e)
    
#     with open("logs.log","a+") as f:
#         f.write("Starting training on different models\n")
#         f.write("Please wait setting up...\n")
#         f.write("Setting up Completed...\n")
#         f.close()
#     resultsCache.set_training_status(False)
#     timeseriesObj=timeseries()
#     Operation=timeseriesObj.createarima(projectConfigFileLocation)
    
#     if Operation["Successful"]:
#         try:
#             Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
#                 "modelID": dataID,
#                 "modelName": "Default Name",
#                 "modelType": "timeseries",
#                 "pickleFolderPath": Operation["pickleFolderPath"],    
#                 "pickleFilePath": Operation["pickleFilePath"],       
#                 "belongsToUserID": timeseriesFormData["userID"],
#                 "belongsToProjectID": timeseriesFormData["projectID"],
#                 "belongsToDataID": dataID
#             })
#         except Exception as e:
#             print("Could not insert into Model Collection. An Error Occurred: ",e)

        
#         try:
#             Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
#                 "belongsToUserID": timeseriesFormData["userID"],
#                 "belongsToProjectID": timeseriesFormData["projectID"],
#                 "belongsToModelID": dataID,
#                 "addressOfMetricsFile": Operation["metricsLocation"],
#                 "accuracy":Operation["accuracy"]
#             })
#         except Exception as e:
#             print("Could not insert into Metrics Collection. An Error Occured: ",e)

#         try:
#             result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":timeseriesFormData["projectID"]})
#             result=serialiseDict(result)
#             if result is not None:
#                 if result["listOfDataIDs"] is not None:
#                     newListOfDataIDs=result["listOfDataIDs"]
#                     newListOfDataIDs.append(dataID)
#                     Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
#                         "$set":{
#                             "listOfDataIDs":newListOfDataIDs,
#                             "configFileLocation": projectConfigFileLocation,
#                             "isAuto": False,
#                             "target": timeseriesFormData["target"]
#                             }
#                         })
#                 else:
#                     Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
#                         "$set":{
#                             "listOfDataIDs":[dataID],
#                             "configFileLocation": projectConfigFileLocation,
#                             "isAuto": False,
#                             "target": timeseriesFormData["target"]
#                             }
#                         })
#                 if (projectType=='timeseries'):
#                     Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
#                         "$set":{
#                             "plotLocation":Operation["plotLocation"]
#                         }
#                     })
#         except Exception as e:
#             print("An Error Occured: ",e)
#     resultsCache.set_training_status(True)
#     with open("logs.log","a+") as f:
#         f.write("\nPROJECT21_TRAINING_ENDED\n")
#         f.write("\nPROJECT21_TRAINING_ENDED\n")
#     return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": timeseriesFormData["projectID"], "dataID":dataID, "modelID": dataID})


@app.post('/timeseries',tags=["Timeseries"])
def timeseries_training(timeseriesFormData: TimeseriesFormData):
    print(timeseriesFormData)
    timeseriesFormData=dict(timeseriesFormData)
    projectConfigFileLocation, projectFolderPath, dataID, projectType = generate_project_timeseries_config_file(timeseriesFormData["projectID"],currentIDs,timeseriesFormData,Project21Database)
    
    resultsCache.set_training_status(False)
    with open("logs.log","w") as f:
        f.write("Time series Initiated\n")
        f.write("Please wait setting up...\n")
        f.write("Setting up Completed...\n")
        f.write("Preprocessing and Training...\n")
        f.close()
    timeseriesPreprocessObj=TimeseriesPreprocess()
    cleanDataPath=timeseriesPreprocessObj.preprocess(projectConfigFileLocation,projectFolderPath)
    
    with open(projectConfigFileLocation) as f:
            projectConfigFileData= yaml.load(f,Loader=SafeLoader)
    projectConfigFileData["clean_data_address"]=cleanDataPath
    with open(projectConfigFileLocation, 'w') as f:
        f.write(yaml.safe_dump(projectConfigFileData))
    
    timeseriesObj=timeseries()
    indexes,freq, Operation, newCleanDataPath=timeseriesObj.timeseriesmanualrf(projectConfigFileLocation)
    try:
        Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
            "dataID": dataID,
            "cleanDataPath": newCleanDataPath,
            "yDataAddress": Operation["y_data"],
            "indexes": indexes,
            "frequency": freq,
            "target": timeseriesFormData["target"],
            "belongsToUserID": timeseriesFormData["userID"],
            "belongsToProjectID": timeseriesFormData["projectID"]
        })
    except Exception as e:
        print("Could not insert into Data Collection. An Error Occured: ",e)
    
    
    
    # Operation returns{"Successful": True, 
    # "cleanDataPath": cleanDataPath, 
    # "metricsLocation":metricsLocation, 
    # "pickleFolderPath":pickleFolderPath, "pickleFilePath":pickleFilePath, 
    # "accuracy":accuracy,
    # "hyperparams":params,
    # "y_data":y_data}
    if Operation["Successful"]:
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
                "modelID": dataID,
                "modelName": "Default Name",
                "modelType": "timeseries",
                "pickleFolderPath": Operation["pickleFolderPath"],    
                "pickleFilePath": Operation["pickleFilePath"],       
                "belongsToUserID": timeseriesFormData["userID"],
                "belongsToProjectID": timeseriesFormData["projectID"],
                "belongsToDataID": dataID,
                "hyperparms": Operation["hyperparams"]
            })
        except Exception as e:
            print("Could not insert into Model Collection. An Error Occurred: ",e)

        
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                "belongsToUserID": timeseriesFormData["userID"],
                "belongsToProjectID": timeseriesFormData["projectID"],
                "belongsToModelID": dataID,
                "addressOfMetricsFile": Operation["metricsLocation"],
                "accuracy":Operation["accuracy"]
            })
        except Exception as e:
            print("Could not insert into Metrics Collection. An Error Occured: ",e)

        try:
            result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":timeseriesFormData["projectID"]})
            result=serialiseDict(result)
            if result is not None:
                if result["listOfDataIDs"] is not None:
                    newListOfDataIDs=result["listOfDataIDs"]
                    newListOfDataIDs.append(dataID)
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "listOfDataIDs":newListOfDataIDs,
                            "configFileLocation": projectConfigFileLocation,
                            "isAuto": False,
                            "target": timeseriesFormData["target"]
                            }
                        })
                else:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "listOfDataIDs":[dataID],
                            "configFileLocation": projectConfigFileLocation,
                            "isAuto": False,
                            "target": timeseriesFormData["target"]
                            }
                        })
                if (projectType=='timeseries'):
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
                        "$set":{
                            "plotLocation":Operation["plotLocation"]
                        }
                    })
        except Exception as e:
            print("An Error Occured: ",e)
    resultsCache.set_training_status(True)
    with open("logs.log","a+") as f:
        f.write("\nPROJECT21_TRAINING_ENDED\n")
        f.write("\nPROJECT21_TRAINING_ENDED\n")
    return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": timeseriesFormData["projectID"], "dataID":dataID, "modelID": dataID, "hyperparams":Operation["hyperparams"]})

# Timeseries Inference Old API - Working
# @app.post('/doTimeseriesInference',tags=["Timeseries"])
# def get_timeseries_inference_results(projectID:int=Form(...),modelID:int=Form(...),inferenceTime:int=Form(...),frequency:str=Form(...)):
    
#     pickleFilePath='/'
#     path='/'
#     inferenceDataResultsPath='/'
#     # try:
#     result=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"modelID":modelID,"belongsToProjectID":projectID})
#     if result is not None:
#         result=serialiseDict(result)
#         if result["pickleFilePath"] is not None:
#             pickleFilePath=result["pickleFilePath"]
#         if result["pickleFolderPath"] is not None:
#             projectRunPath=os.path.join(result["pickleFolderPath"],os.pardir)
#             path=os.path.join(projectRunPath,"inference_data")
#             if(not os.path.exists(path)):
#                 os.makedirs(path)
        
#         inference=timeseries()
#         inferenceDataResultsPath=inference.arimainference(pickleFilePath,path,inferenceTime)
        
#         Project21Database.insert_one(settings.DB_COLLECTION_INFERENCE,{
#             "inferenceTime": inferenceTime,
#             "results": inferenceDataResultsPath,
#             "inferenceFolderPath": path,
#             "belongsToUserID": currentIDs.get_current_user_id(),
#             "belongsToProjectID": projectID,
#             "belongsToModelID": modelID
#         })
#         if os.path.exists(inferenceDataResultsPath):
#             print({"Timeseries Inference Generation":"Successful"})
#             return FileResponse(inferenceDataResultsPath,media_type="text/csv",filename="inference.csv")
#     # except Exception as e:
#     #     print("An error occured: ", e)
#     #     print("Unable to find model from model Collection")
#     return JSONResponse({"Timeseries Inference Generation":"Failed"})


@app.post('/doTimeseriesInference',tags=["Timeseries"])
def get_timeseries_inference_results(projectID:int=Form(...),modelID:int=Form(...),inferenceTime:int=Form(...),frequency:str=Form(...)):
    
    pickleFilePath='/'
    path='/'
    inferenceDataResultsPath='/'
    # try:
    result=Project21Database.find_one(settings.DB_COLLECTION_MODEL,{"modelID":modelID,"belongsToProjectID":projectID})
    if result is not None:
        result=serialiseDict(result)
        if result["pickleFilePath"] is not None:
            pickleFilePath=result["pickleFilePath"]
        if result["pickleFolderPath"] is not None:
            projectRunPath=os.path.join(result["pickleFolderPath"],os.pardir)
            path=os.path.join(projectRunPath,"inference_data")
            if(not os.path.exists(path)):
                os.makedirs(path)
        
        result_project=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result_project is not None:
            configFileLocation=result_project["configFileLocation"]
        
        result_data=Project21Database.find_one(settings.DB_COLLECTION_DATA,{"belongsToProjectID":projectID,"dataID":modelID})
        if result_data is not None:
            indexes=result_data["indexes"]
            frequency=result_data["frequency"]
        inference=timeseries()
        _, inferenceDataResultsPath=inference.rfinference(inferenceTime,pickleFilePath,result_project["rawDataPath"],indexes,frequency)
        # inferenceDataResultsPath=inference.arimainference(pickleFilePath,path,inferenceTime)
        
        Project21Database.insert_one(settings.DB_COLLECTION_INFERENCE,{
            "inferenceTime": inferenceTime,
            "results": inferenceDataResultsPath,
            "inferenceFolderPath": path,
            "belongsToUserID": currentIDs.get_current_user_id(),
            "belongsToProjectID": projectID,
            "belongsToModelID": modelID
        })
        if os.path.exists(inferenceDataResultsPath):
            print({"Timeseries Inference Generation":"Successful"})
            return FileResponse(inferenceDataResultsPath,media_type="text/csv",filename="inference.csv")
    # except Exception as e:
    #     print("An error occured: ", e)
    #     print("Unable to find model from model Collection")
    return JSONResponse({"Timeseries Inference Generation":"Failed"})


@app.post('/doTimeseriesInferencePlot',tags=["Timeseries"])
def get_timeseries_inference_plot(projectID:int=Form(...),modelID:int=Form(...),inferenceTime:int=Form(...),frequency:str=Form(...)):
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_INFERENCE,{"belongsToProjectID":projectID,"belongsToModelID":modelID})
        result_Data=Project21Database.find_one(settings.DB_COLLECTION_DATA,{"belongsToProjectID":projectID,"dataID":modelID})
        result_Data=serialiseDict(result_Data)
        if result is not None:
            result=serialiseDict(result)
            inferenceFilePath=result["results"]
            if (os.path.exists(inferenceFilePath)):
                timeseriesObj=timeseries()
                plotFilepath=timeseriesObj.plotinference(inferenceFilePath,result["inferenceFolderPath"],result_Data["cleanDataPath"],inferenceTime,frequency)
                return FileResponse(plotFilepath,media_type="text/html",filename="inference.html")
            else:
                return JSONResponse({"Success":"False","Inference Plot":"Not Generated"})
    except Exception as e:
        print("An Error Occured: ",e)
        return JSONResponse({"Success":"False","Inference Plot":"Not Generated"})



@app.websocket("/websocketStream")
async def training_status(websocket: WebSocket):
    def generatorLineLogs(file):
        """ Yield each line from a file as they are written. """
        line = ''
        while True:
            tmp = file.readline()
            if tmp is not None:
                line += tmp
                if line.endswith("\n"):
                    yield line
                    line = ''
            else:
                yield ''
    
    print("Connecting to the Frontend...")
    await websocket.accept()

    try:
        for line in generatorLineLogs(open("logs.log", 'r')):
            if resultsCache.get_training_status()==True or line=="PROJECT21_TRAINING_ENDED\n":
                websocket.close("Logs Generating Finished")
                break
            await websocket.send_json({"logs":line})
            # replyFromFrontend=await websocket.receive_text()
        print("File Reading ended")
        resultsCache.set_training_status(False)
        # open("logs.log","w").close()    #Truncating the contents of the log file after the websocket disconnects
        print("Websocket connection closing...")
    except WebSocketDisconnect:
        print("Websocket connection has been disconnected...")

@app.delete('/deleteThisProject/{userID}/{projectID}')
def delete_entire_project(userID:int,projectID:int):
    result_user=Project21Database.find_one(settings.DB_COLLECTION_USER,{"userID":userID})
    if result_user is not None:
        listOfProjects=result_user["listOfProjects"]
        try:
            listOfProjects.remove(projectID)
            Project21Database.update_one(settings.DB_COLLECTION_USER,{"userID":userID},{"$set":{"listOfProjects":listOfProjects}})
            print("Successfully removed project from list of user projects")
        except ValueError:
            print("ProjectID is not in user's project list.")
            return JSONResponse({"Success":True,"Project Deletion":"Not Successful","Error":"Project Not In Projects List"})
    
    result_project=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID,"belongsToUserID":userID})
    if result_project is not None:
        try:
            projectFolderPath=result_project["projectFolderPath"]
            # listOfDataIDs=result_project["listOfDataIDs"]

            deletedProjectDatasCount=Project21Database.delete_many(settings.DB_COLLECTION_DATA,{"belongsToUserID":userID,"belongsToProjectID":projectID})
            print("Deleted Datas from Data Collection Count: ",deletedProjectDatasCount)
            
            deletedProjectModelsCount=Project21Database.delete_many(settings.DB_COLLECTION_MODEL,{"belongsToUserID":userID,"belongsToProjectID":projectID})
            print("Deleted Models from Model Collection Count: ",deletedProjectModelsCount)

            deletedProjectMetricsCount=Project21Database.delete_many(settings.DB_COLLECTION_METRICS,{"belongsToUserID":userID,"belongsToProjectID":projectID})
            print("Deleted Metrics from Metrics Collection Count: ",deletedProjectMetricsCount)

            deletedProjectInferencesCount=Project21Database.delete_many(settings.DB_COLLECTION_INFERENCE,{"belongsToUserID":userID,"belongsToProjectID":projectID})
            print("Deleted Inferences from Inference Collection Count: ",deletedProjectInferencesCount)

            Project21Database.delete_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})

        except Exception as e:
            print("An Error Occuered: ",e)
            print("Could not delete the project related collections from DB")
        
        try:
            shutil.rmtree(projectFolderPath)
        except OSError as e:
            print("An Error Occured: ", e)
            JSONResponse({"Success":True,"DB Deletion":"Successful","Directory Deletion":"Not Successful"})
    return JSONResponse({"Success":True,"DB Deletion":"Successful","Directory Deletion":"Successful"})


@app.delete('/deleteThisRun/{userID}/{projectID}/{dataID}')
def delete_run_data(userID:int,projectID:int,dataID:int):
    result_project=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID,"belongsToUserID":userID})
    if result_project is not None:
        result_project=serialiseDict(result_project)
        listOfDataIDs=result_project["listOfDataIDs"]
        if dataID in listOfDataIDs:
            try:
                Project21Database.delete_one(settings.DB_COLLECTION_DATA,{"dataID":dataID})
                Project21Database.delete_one(settings.DB_COLLECTION_MODEL,{"dataID":dataID})    #because dataID and modelID are the same
                Project21Database.delete_one(settings.DB_COLLECTION_METRICS,{"belongsToModelID":dataID})    #modelID and dataID are the same
                Project21Database.delete_one(settings.DB_COLLECTION_INFERENCE,{"belongsToModelID":dataID})  #modelID and dataID are the same
                listOfDataIDs.remove(dataID)
                Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{"$set":{"listOfDataIDs":listOfDataIDs}})
                print("Deleted Data, Model, Metrics, Inference associated with this run successfully.")
                return JSONResponse({"Success":True,"Run Deleted":"Successfully"})
            except Exception as e:
                print("An Error Occured: ",e)
                print("Unable to delete the associated data, model, metrics and inference of this project's run")
                JSONResponse({"Success":False,"Run Deleted":"Unsuccessfully","Error":e})
        else:
            print("This run could not be found in the list of dataIDs of the project")
            print("Removal of run unsuccessful")
            return JSONResponse({"Success":False,"Run Deleted":"Unsuccessfully","Error":"No such run exists in the project's list of dataIDs"})
        print("Project not found in DB")
        return(JSONResponse({"Success":False,"Run Deleted":"Unsuccessfully","Error":"No such project exists in the DB"}))

    
# @app.get('/sampleDatas')
# def get_sample_data():
#     def getListOfTestDataFiles(dirName):
#         listOfFiles = os.listdir(dirName)
#         allFiles = []
#         for path in listOfFiles:
#             fullPath = os.path.join(dirName, path)
#             if os.path.isdir(fullPath):
#                 allFiles = allFiles + getListOfTestDataFiles(fullPath)
#             else:
#                 allFiles.append(fullPath)
#         return allFiles

#     sampleDatas=[]
#     for item in getListOfTestDataFiles(settings.SAMPLE_DATASET_FOLDER):
#         sampleDataTemplate={
#             "filename": os.path.basename(item),
#             "filepath": item
#         }
#         sampleDatas.append(sampleDataTemplate)

#     return sampleDatas

@app.get('/sampleData')
def get_sample_data_file(filename:str):
    switcher = {
        'Iris': settings.SAMPLE_DATASET_CLASSIFICATION,
        'Cardata': settings.SAMPLE_DATASET_REGRESSION,
        'Icecream': settings.SAMPLE_DATASET_TIMESERIES,
        'Jewellery': settings.SAMPLE_DATASET_CLUSTERING
    }
    filepath=switcher.get(filename,"nofile")
    if os.path.isfile(filepath):
        try:
            return FileResponse(filepath,media_type="text/csv", filename="sampleDataset.csv")
        except Exception as e:
            print("An Error Occured: ",e)
            return JSONResponse({"Success": False})
    else:
        return JSONResponse({"Success":False})