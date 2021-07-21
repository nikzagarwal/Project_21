import os
import pickle
import shutil
import yaml
from fastapi import FastAPI, Form, Request
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
from Backend.app.schemas import AutoFormData, TimeseriesFormData, PreprocessJSONFormData
from Backend.utils import generate_project_folder, generate_project_auto_config_file, generate_project_manual_config_file, generate_project_timeseries_config_file, convertFile, deleteTempFiles
from Files.auto import Auto
from Files.autoreg import AutoReg
from Files.auto_clustering import Autoclu
from Files.plot import plot
from Files.inference import Inference
from Files.preprocess import Preprocess
from Files.training import training
from Files.timeseries_preprocess import TimeseriesPreprocess
from Files.timeseries import timeseries

from sse_starlette.sse import EventSourceResponse
# from sh import tail
# import time
import asyncio

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
        resultsCache.set_auto_mode_status(False)
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
                "projectFolderPath":Operation["ProjectFolderPath"],
                "belongsToUserID": currentIDs.get_current_user_id(),
                "listOfDataIDs":[],
                "configFileLocation": None,
                "plotsPath": None,
                "projectType": mtype,
                "target":None
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
    resultsCache.set_auto_mode_status(False)
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
            Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
                "dataID": dataID,
                "cleanDataPath": Operation["cleanDataPath"],
                "target": autoFormData["target"],
                "belongsToUserID": currentIDs.get_current_user_id(),
                "belongsToProjectID": autoFormData["projectID"]
            })
            currentIDs.set_current_data_id(dataID)
            Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
                "modelID": dataID,
                "modelName": "Default Name",
                "modelType": problem_type,
                "pickleFolderPath": Operation["pickleFolderPath"],
                "pickleFilePath": Operation["pickleFilePath"],
                "belongsToUserID": autoFormData["userID"],
                "belongsToProjectID": autoFormData["projectID"],
                "belongsToDataID": dataID
            })
            Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                "belongsToUserID": autoFormData["userID"],
                "belongsToProjectID": autoFormData["projectID"],
                "belongsToModelID": dataID,
                "addressOfMetricsFile": Operation["metricsLocation"]
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
            return JSONResponse({"Auto": "Success", "Database Insertion":"Failure", "Project Collection Updation": "Unsuccessful"})
        
        resultsCache.set_clean_data_path(Operation["cleanDataPath"])
        resultsCache.set_metrics_path(Operation["metricsLocation"])
        resultsCache.set_pickle_file_path(Operation["pickleFilePath"])
        resultsCache.set_pickle_folder_path(Operation["pickleFolderPath"])
        resultsCache.set_auto_mode_status(True)
        return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": autoFormData["projectID"], "dataID":dataID, "modelID": dataID})
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


@app.get('/getPlots/{projectID}',tags=["Auto Mode"])        #To-DO: make the plots appear in each sub directory and see the config file according to the userID, projectID and dataID given
def get_plots(projectID:int):       #check if it already exists - change location address
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result is not None:
            result=serialiseDict(result)
            if (result["projectType"]=='clustering'):
                return FileResponse(result["clusterPlotLocation"],media_type="text/html",filename="plot.html")
            if(result["projectType"]=='timeseries'):
                return FileResponse(result["plotLocation"],media_type="text/html",filename="plot.html")
            
            if result["configFileLocation"] is not None:
                plotFilePath=plot(result["configFileLocation"]) #plot function requires the auto config file
                try:
                    Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{
                        "$set": {
                            "plotsPath": plotFilePath
                        }
                    })
                except Exception as e:
                    print("An Error occured while storing the plot path into the project collection")
                return FileResponse(plotFilePath,media_type='text/html',filename='plot.html')
    except Exception as e:
        print("An Error Occured: ",e)
        return JSONResponse({"Plots": "Not generated"})


@app.get('/getAllProjects',tags=["Auto Mode"])
def get_all_project_details(userID:int):
    listOfProjects=[]
    try:   
        results=Project21Database.find(settings.DB_COLLECTION_PROJECT,{"belongsToUserID":userID})
        for result in results:
            result=serialiseDict(result)
            if result["target"] is not None:
                projectTemplate={
                    "projectID": result["projectID"],
                    "projectName": result["projectName"],
                    "target": result["target"],
                    "modelType": result["projectType"],
                    "listOfDataIDs": result["listOfDataIDs"],
                    "isAuto": result["isAuto"]
                }
                listOfProjects.append(projectTemplate)
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

@app.post('/getHyperparams',tags=["Manual Mode"])
def get_hyper_parameters(preprocessJSONFormData:dict):
    preprocessJSONFormData=dict(preprocessJSONFormData)
    # projectManualConfigFileLocation, dataID, problem_type, folderLocation = generate_project_manual_config_file(preprocessJSONFormData["projectID"],preprocessJSONFormData,Project21Database)
    # # TODO: Call function manual preprocess generate the clean data and save it in DB
    # preprocessObj=Preprocess()
    # cleanDataPath=preprocessObj.manual_preprocess(projectManualConfigFileLocation, folderLocation)
    # print(cleanDataPath)
    
    # if os.path.exists(cleanDataPath):
    #     try:
    #         Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
    #             "dataID": dataID,
    #             "cleanDataPath": cleanDataPath,
    #             "target": preprocessJSONFormData["target_column_name"],
    #             "belongsToUserID": currentIDs.get_current_user_id(),
    #             "belongsToProjectID": preprocessJSONFormData["projectID"]
    #         })
    #     except Exception as e:
    #         print("An Error Occured: ",e)
    #         print("Could not Insert into Data Collection")
    yaml_json=yaml.load(open(settings.CONFIG_MODEL_YAML_FILE),Loader=SafeLoader)
    return yaml_json

@app.post('/manual',tags=["Manual Mode"])
def start_manual_training():
    # trainingObj=training()
    # trainingObj.train() #Have to add the arguments here

    #         Project21Database.insert_one(settings.DB_COLLECTION_MODEL,{
    #             "modelID": dataID,
    #             "modelName": "Default Name",
    #             "modelType": problem_type,
    #             "pickleFolderPath": Operation["pickleFolderPath"],
    #             "pickleFilePath": Operation["pickleFilePath"],
    #             "belongsToUserID": formData["userID"],
    #             "belongsToProjectID": formData["projectID"],
    #             "belongsToDataID": dataID
    #         })
    #         Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
    #             "belongsToUserID": formData["userID"],
    #             "belongsToProjectID": formData["projectID"],
    #             "belongsToModelID": dataID,
    #             "addressOfMetricsFile": Operation["metricsLocation"]
    #         })
    #         result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":formData["projectID"]})
    #         result=serialiseDict(result)
    #         if result is not None:
    #             if result["listOfDataIDs"] is not None:
    #                 newListOfDataIDs=result["listOfDataIDs"]
    #                 newListOfDataIDs.append(dataID)
    #                 Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
    #                     "$set":{
    #                         "listOfDataIDs":newListOfDataIDs,
    #                         "configFileLocation": projectAutoConfigFileLocation,
    #                         "isAuto": formData["isauto"],
    #                         "target": formData["target"]
    #                         }
    #                     })
    #             else:
    #                 Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
    #                     "$set":{
    #                         "listOfDataIDs":[dataID],
    #                         "configFileLocation": projectAutoConfigFileLocation,
    #                         "isAuto": formData["isauto"],
    #                         "target": formData["target"]
    #                         }
    #                     })
    #             if (problem_type=='clustering'):
    #                 Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":result["projectID"]},{
    #                     "$set":{
    #                         "clusterPlotLocation":Operation["clusterPlotLocation"]
    #                     }
    #                 })
    #     except Exception as e:
    #         print("An Error occured: ",e)
    #         return JSONResponse({"Auto": "Success", "Database Insertion":"Failure", "Project Collection Updation": "Unsuccessful"})
    #     return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": preprocessJSONFormData["projectID"], "dataID":dataID, "modelID": dataID})
    # else:
    #     return JSONResponse({"Successful":"False"})
    return JSONResponse({"Working":"True"})

@app.post('/timeseries',tags=["Timeseries"])
def timeseries_training(timeseriesFormData: TimeseriesFormData):
    print(timeseriesFormData)
    timeseriesFormData=dict(timeseriesFormData)
    projectConfigFileLocation, projectFolderPath, dataID, projectType = generate_project_timeseries_config_file(timeseriesFormData["projectID"],currentIDs,timeseriesFormData,Project21Database)
    timeseriesPreprocessObj=TimeseriesPreprocess()
    cleanDataPath=timeseriesPreprocessObj.preprocess(projectConfigFileLocation,projectFolderPath)
    try:
        Project21Database.insert_one(settings.DB_COLLECTION_DATA,{
            "dataID": dataID,
            "cleanDataPath": cleanDataPath,
            "target": timeseriesFormData["target"],
            "belongsToUserID": timeseriesFormData["userID"],
            "belongsToProjectID": timeseriesFormData["projectID"]
        })
    except Exception as e:
        print("Could not insert into Data Collection. An Error Occured: ",e)

    timeseriesObj=timeseries()
    Operation=timeseriesObj.createarima(projectConfigFileLocation)
    
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
                "belongsToDataID": dataID
            })
        except Exception as e:
            print("Could not insert into Model Collection. An Error Occurred: ",e)

        
        try:
            Project21Database.insert_one(settings.DB_COLLECTION_METRICS,{
                "belongsToUserID": timeseriesFormData["userID"],
                "belongsToProjectID": timeseriesFormData["projectID"],
                "belongsToModelID": dataID,
                "addressOfMetricsFile": Operation["metricsLocation"]
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
    return JSONResponse({"Successful":"True", "userID": currentIDs.get_current_user_id(), "projectID": timeseriesFormData["projectID"], "dataID":dataID, "modelID": dataID})


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
        
        inference=timeseries()
        inferenceDataResultsPath=inference.arimainference(pickleFilePath,path,inferenceTime)
        
        Project21Database.insert_one(settings.DB_COLLECTION_INFERENCE,{
            "inferenceTime": inferenceTime,
            "results": inferenceDataResultsPath,
            "inferenceFolderPath": path,
            "belongsToUserID": currentIDs.get_current_user_id(),
            "belongsToProjectID": projectID,
            "belongsToModelID": modelID
        })
        if os.path.exists(inferenceDataResultsPath):
            print({"Metrics Generation":"Successful"})
            return FileResponse(inferenceDataResultsPath,media_type="text/csv",filename="inference.csv")
    # except Exception as e:
    #     print("An error occured: ", e)
    #     print("Unable to find model from model Collection")
    return JSONResponse({"Metrics Generation":"Failed"})


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


# @app.get('/stream-logs2')
# async def run(request: Request):
#     async def autologs(request):
#         for line in tail_F('logs.log'):
#             if await request.is_disconnected():
#                 print("Client Disconnected!")
#                 break
#             yield line
            
#     event_generator = autologs(request)
#     return EventSourceResponse(event_generator)


# MESSAGE_STREAM_DELAY = 1  # second
# MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond


# @app.get('/stream')
# async def message_stream(request: Request):     
#     async def event_generator():
#         while True:
#             # If client was closed the connection
#             if await request.is_disconnected():
#                 print("Client Disconnected!")
#                 break

#             # Checks for new messages and return them to client if any
#             for line in tail("-f", 'logs.log', _iter=True):
#                 yield {
#                     "event": line,
#                     "id": "message_id",
#                     "retry": MESSAGE_STREAM_RETRY_TIMEOUT,
#                     "data": "message_content"
#                 }
#             await asyncio.sleep(MESSAGE_STREAM_DELAY)

#     return EventSourceResponse(event_generator())

# @app.websocket("/ws")
# async def training_status(websocket: WebSocket):
#     print("Connecting to the Frontend...")
#     await websocket.accept()
#     # while (not resultsCache.get_auto_mode_status()):
#     try:
#         data={
#             "Successful":"False",
#             "Status": "Model Running"
#         }
#         if (resultsCache.get_auto_mode_status()):
#             data={
#             "Successful":"True",
#             "Status": "Model Successfully Created",
#             "userID": currentIDs.get_current_user_id(),
#             "projectID": currentIDs.get_current_project_id(),
#             "dataID":currentIDs.get_current_data_id(),
#             "modelID": currentIDs.get_current_model_id()
#             }
#             await websocket.send_json(data)
#         data2= await websocket.receive_text()  #Can be used to receive data from frontend
#         print(data2)
#         await websocket.send_json(data) #Can be used to return data to the frontend
#     except Exception as e:
#         print("Error: ",e)
#         # break
#     print("Websocket connection closing...")

# def tail_F(some_file):
#     first_call = True
#     while True:
#         try:
#             with open(some_file) as input:
#                 if first_call:
#                     input.seek(0, 2)
#                     first_call = False
#                 latest_data = input.read()
#                 while True:
#                     if '\n' not in latest_data:
#                         latest_data += input.read()
#                         if '\n' not in latest_data:
#                             yield ''
#                             if not os.path.isfile(some_file):
#                                 break
#                             continue
#                     latest_lines = latest_data.split('\n')
#                     if latest_data[-1] != '\n':
#                         latest_data = latest_lines[-1]
#                     else:
#                         latest_data = input.read()
#                     for line in latest_lines[:-1]:
#                         yield line + '\n'
#         except IOError:
#             yield ''



# @app.get('/stream-logs')
# def streaming_logs_auto(request:Request):
#     def autoLogs():
#         for line in tail_F("logs.log"):
#             if not resultsCache.get_auto_mode_status():
#                 print("Client Disconnected!")
#                 break
#             yield line
#     event_generator = autoLogs()
#     return EventSourceResponse(event_generator)

@app.get('/autoStatus')
def change_status_of_auto_mode(status:bool):
    resultsCache.set_auto_mode_status(status)
    return JSONResponse({"Status Changed":"Successfully","Status Changed To":status})



'''
Get status as an event generator
'''
status_stream_delay = 5  # second
status_stream_retry_timeout = 30000  # milisecond

async def status_event_generator(request):
    previous_status = None
    while True:
        if await request.is_disconnected():
            print('Request disconnected')
            break

        if previous_status and resultsCache.get_auto_mode_status():
            print('Request completed. Disconnecting now')
            yield {
                "event": "end",
                "data" : ''
            }
            break

        current_status = resultsCache.get_auto_mode_status()
        if previous_status != current_status:
            yield {
                "event": "update",
                "retry": status_stream_retry_timeout,
                "data": current_status
            }
            previous_status = current_status
            print('Current status :%s', current_status)
        else:
            print('No change in status...')

        await asyncio.sleep(status_stream_delay)

@app.get('/status/stream')
async def runStatus(request: Request):
    event_generator = status_event_generator(request)
    return EventSourceResponse(event_generator)