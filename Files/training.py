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
import pickle
import random
import plotly.express as px
import plotly.graph_objects as go

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
        hyperparams={}
        if preprocessconfigfile["split_ratio_test"]:
            test_ratio=preprocessconfigfile["split_ratio_test"] #input given the the user usually 0.3 by default
        else:
            test_ratio=0.2
        # data=dataconfigfile["clean_data"] 
        datapath=cleanDataPath

        target_column=preprocessconfigfile["target_column_name"]
        
        
        if dataconfigfile["problem_type"]=='classification':
            metrics=pd.DataFrame(columns = ['modelname','Accuracy','Recall','Prec.','F1','Kappa',"AUC"])

        elif dataconfigfile["problem_type"]=='regression':
            metrics=pd.DataFrame(columns=['modelname','MAE','MSE',"RMSE",'R2','RMSLE'])
        elif dataconfigfile["problem_type"]=='timeseries':
            metrics=pd.DataFrame(columns=['modelname','MAE','MSE',"RMSE",'R2','RMSLE'])
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

                metricsnewrow, hyperparams=hp.optimize(model_str,model["name"],userinputconfig,datapath,dataconfig,target_column,hyperparams,test_ratio)
                try:
                    metrics.loc[len(metrics.index)] = metricsnewrow 
                except Exception as e:
                    print(metrics)
                    print(metricsnewrow)
                    print(" an exception occured :",e)
                print(metrics)
        print(1)
        
        #stores the metrics in the assigned folder
        accuracy=''
        if dataconfigfile["problem_type"]=='classification':
            metrics=metrics.sort_values(['Accuracy', 'F1'], ascending=[False, False]).reset_index()
            accuracy=metrics['Accuracy'][0]*100
        else:
            metrics=metrics.sort_values(['R2', 'MSE'], ascending=[False, False]).reset_index()      
            accuracy=metrics['R2'][0]
        print(2)
        metrics=metrics.rename(columns={"modelname":"Model"}) 
        metricsLocation=os.path.join(dataconfigfile["location"],"metrics.csv")
        metrics.to_csv(metricsLocation, index=False)
        print(3)
        # bestmodel
        best_model=metrics['Model'][0]
        best_model_location=os.path.join(picklelocation,(str(best_model) +".pkl"))
        print(4)
        hyper=hyperparams[best_model]

        print({
            "Successful":True,
            "metricsLocation":metricsLocation,
            "pickleFolderPath": picklelocation,         #Generate a folder where all pickle files are residing
            "pickleFilePath": best_model_location,             #Best model pickle file path
            "accuracy":accuracy,                         #Accuracy of best model
            "cleanDataPath":cleanDataPath,
            "clusterPlotLocation": "clusterPlotLocation",    #Only if it is clustering
            "hyperparams":hyper
        })
        return {
            "Successful":True,
            "metricsLocation":metricsLocation,
            "pickleFolderPath": picklelocation,         #Generate a folder where all pickle files are residing
            "pickleFilePath": best_model_location,             #Best model pickle file path
            "accuracy":accuracy,                         #Accuracy of best model
            "cleanDataPath":cleanDataPath,
            "clusterPlotLocation": "clusterPlotLocation",    #Only if it is clustering
            "hyperparams":hyper
        }

    def model_plot(self,pickleFileLocation,cleandatapath,target_column,plotLocation,modeltype):
        print("reached here,",modeltype)
        if modeltype=="regression":
            print("Model Type expected: regression received: ",modeltype)
            clf=pickle.load(open(pickleFileLocation,"rb"))
            data=pd.read_csv(cleandatapath)
            y=data[target_column]
            data.drop([target_column],inplace=True,axis=1)
            x=data
            y_pred=clf.predict(x)
            fig = go.Figure()
            ran=random.randint(100,999)
            fig.add_trace(go.Scatter(x=x.index,y=y,name="actual"))
            fig.add_trace(go.Scatter(x=x.index,y=y_pred,name="predictions"))
            
            plotlocation=os.path.join(plotLocation,"plot.html")
            print("about to save plot")
            fig.write_html(plotlocation)
            print("done, plotlocation",plotlocation)
            return plotlocation
        else:
            print("Model Type expected: classification received: ",modeltype)
            clf=pickle.load(open(pickleFileLocation,"rb"))
            data=pd.read_csv(cleandatapath)
            print(1)
            y=data[[target_column]]
            print(2)
            data.drop([target_column],inplace=True,axis=1)
            
            x=data
            print(3)
            y_pred=clf.predict(x)
            print(4)
            fig = go.Figure()
            ran=random.randint(100,999)
            
            fig.add_trace(go.Scatter(x=list(x.index),y=y.iloc[:,-1],name="actual",mode='markers',marker=dict(
                    color='LightSkyBlue',
                    size=20,
                    line=dict(
                        color='MediumPurple',
                        width=12
                    ))))
            fig.add_trace(go.Scatter(x=list(x.index),y=y_pred,name="predictions",mode='markers',marker=dict(
                    color='Orange',
                    size=5,
                    line=dict(
                        color='Orange',
                        width=12
                    ))))
            plotlocation=os.path.join(plotLocation,"plotclas.html")
            print("about to save plot")

            fig.write_html(plotlocation)
            print("done, plotlocation",plotlocation)
            return plotlocation
