from Backend.app.helpers.allhelpers import serialiseDict
from Backend.app.config import settings

def get_metrics(projectID,modelID,Project21Database):
    try:
        result=Project21Database.find_one(settings.DB_COLLECTION_METRICS,{"belongsToProjectID":projectID,"belongsToModelID":modelID})
        if result is not None:
            result=serialiseDict(result)
            if result["addressOfMetricsFile"] is not None:
                return str(result["addressOfMetricsFile"])
    except Exception as e:
        print("An Error Occured: ", e)
    return 'Metrics not found'