from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from Backend.app.dbclass import Database
from Backend.app.config import settings
from Backend.app.schemas import Project, UpdateProject
from Backend.app.helpers.allhelpers import ErrorResponseModel, ResponseModel, serialiseDict, serialiseList

Project21Database=Database()
Project21Database.initialise(settings.DB_NAME)

project_router=APIRouter()

@project_router.get('/projects')
def get_all_projects():
    projects=[]
    all_projects=serialiseList(Project21Database.find(settings.DB_COLLECTION_PROJECT,{}))
    for project in all_projects:
        projects.append(project)
    return projects

@project_router.get('/project/{projectID}')
def get_one_project(projectID:int):
    try:
        project=serialiseDict(Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID}))
    except:
        return ErrorResponseModel("An Error Occured",404,"Project could not be found")
    return project

@project_router.post('/project')
def insert_one_project(project: Project=Body(...)):
    project=jsonable_encoder(project)
    try:
        Project21Database.insert_one(settings.DB_COLLECTION_PROJECT,project)
    except:
        return ErrorResponseModel("An Error Occured",404,"Could not insert Project into the Collection")
    return ResponseModel(project["projectID"],"Succesfully Inserted")

@project_router.put('/project/{projectID}')
def update_one_project(projectID:int,updateProject: UpdateProject=Body(...)):
    updateProject={k:v for k,v in updateProject.dict().items() if v is not None}
    result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
    if result:
        try:
            result=Project21Database.update_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID},{"$set":updateProject})
            return ResponseModel(projectID,"Successfully Updated")
        except:
            return ErrorResponseModel("An Error Occured",404,"Project could not be updated")
    return ErrorResponseModel("An Error Occured",404,"Project could not be updated")

@project_router.delete('/deleteproject/{projectID}')
def delete_one_project(projectID:int):
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        if result:
            Project21Database.delete_one(settings.DB_COLLECTION_PROJECT,{"projectID":projectID})
        else:
            return ErrorResponseModel("An Error Occured",404,"project could not be found")
    except:
        return ErrorResponseModel("An Error Occured",404,"project could not be deleted")
    return ResponseModel(projectID,"Successfully Deleted")