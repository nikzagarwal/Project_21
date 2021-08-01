import yaml
from yaml.loader import FullLoader
import numpy as np
import pandas as pd
import json
import pandas as pd
from .libraries import *
import yaml
from Files.hyperparameter import hyperparameter as hp
import os 

class training:

    def train(self,userinputconfig,dataconfig,preprocessconfig,cleanDataPath):
        
        with open(preprocessconfig) as f:
            preprocessconfigfile= yaml.load(f,Loader=FullLoader) #for split ratio


        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader) #has info about where the data is stored and where the model must be stored

        with open(userinputconfig) as file:
            userinputconfigfile=yaml.load(file,Loader=FullLoader) #modified version of model universe for each run
        models=[]
        ans=[]

        test_ratio=preprocessconfigfile["split_ratio_test"] #input given the the user usually 0.3 by default

        # data=dataconfigfile["clean_data"] 
        data=cleanDataPath

        target_column=preprocessconfigfile["target_column_name"]
        
        
        if dataconfigfile["problem_type"]=='classification':
            metrics=pd.DataFrame(columns = ['modelname','Accuracy','Recall','Prec.','F1','Kappa'])

        elif dataconfigfile["problem_type"]=='regression':
            metrics=pd.DataFrame(columns=['modelname','MAE','MSE',"RMSE",'R2','RMSLE',"AUC"])
        #create location of pickle file
        picklelocation=os.path.join(dataconfigfile["location"],str(dataconfigfile["id"])+"_model")
        os.makedirs(picklelocation)
        #creates a pandas dataframe to store the metrics of the created model
        for model in userinputconfigfile:
            if model["isSelected"]:

                hypers=[]
                keylist=[]
                for feature in model["hyper"]:
                    if feature["ischanged"]:
                        keylist.append(feature["name"])
                        hypers.append(feature["name"]+"="+ str(feature["value"]))
                model_str=model["name"] + "(" + ", ".join(hypers) + ")"

                metricsnewrow=hp.optimize(model_str,model["name"],userinputconfig,data,dataconfig,target_column)
                print(metricsnewrow)
                metrics.loc[len(metrics.index)]=metricsnewrow
                
        #stores the metrics in the assigned folder
        accuracy=''
        if dataconfigfile["problem_type"]=='classification':
            metrics=metrics.sort_values(['accuracy_score', 'f1_score'], ascending=[False, False]).reset_index()
            accuracy=metrics['accuracy_score'][0]*100
        else:
            metrics=metrics.sort_values(['r2_score', 'mean_absolute_error'], ascending=[False, False]).reset_index()      
            accuracy=metrics['r2_score'][0]
            
        metrics=metrics.rename(columns={"modelname":"Model"}) 
        metricsLocation=os.path.join(dataconfigfile["location"],"metrics.csv")
        metrics.to_csv(metricsLocation, index=False)
        
        # bestmodel
        best_model=metrics['Model'][0]
        best_model_location=os.path.join(picklelocation,(str(best_model) +".pkl"))
        
        
        return {
            "Successful":True,
            "metricsLocation":metricsLocation,
            "pickleFolderPath": picklelocation,         #Generate a folder where all pickle files are residing
            "pickleFilePath": best_model_location,             #Best model pickle file path
            "accuracy":accuracy,                          #Accuracy of best model
            "clusterPlotLocation": "clusterPlotLocation"    #Only if it is clustering
        }
