import yaml
import os
from yaml.loader import FullLoader
import numpy as np
import pandas as pd
import json
import pickle
import pandas as pd
from .libraries import *
import sys
from Files.metrics import Metrics as met
class hyperparameter:
    def optimize(model_str,modelname,userinputconfig,datapath,dataconfig,target_column,hyperparams,test_ratio):
        """
        This function in takes the string consisting of the name and the hyperparameters of the model and uses eval function to create the model.
        Keylist is the dictionary consisting of the infomation about the user input ('subject to further changes')
        Name is the name of the model selected (subject to future changes)
        """

        data=pd.read_csv(datapath)
        ydata=data[target_column]
        data.drop([target_column],inplace=True,axis=1)
        xdata=data

        with open(userinputconfig) as f:
            userinputconfig= yaml.load(f,Loader=FullLoader)

        with open(dataconfig) as c:
            dataconfig=yaml.load(c,Loader=FullLoader)

        params={}
        for model in userinputconfig:
            if model["name"]==modelname:
                
                modelname=model["name"]
                print(modelname)
                model_type=model["type"]
                for hyper in model["hyper"]:
                    if hyper["ischanged"]==False:
                        if hyper["vary"]:
                            if hyper["type"]=="options":
                                params[hyper["name"]]=hyper["options"]
                            elif hyper["type"]=="bool":
                                params[hyper["name"]]=[True,False]
                            elif hyper["type"]=="float" or hyper["type"]=="int":
                                if hyper["range"]["type"]=="linear":
                                    if hyper["type"]=="int":
                                        params[hyper["name"]]=(np.linspace(hyper["range"]["min"],hyper["range"]["max"],hyper["range"]["num_samp"])).astype(int)
                                    else:
                                        print(hyper)
                                        params[hyper["name"]]=np.linspace(hyper["range"]["min"],hyper["range"]["max"],hyper["range"]["num_samp"])
                                if hyper["range"]["type"]=="log":
                                    if hyper["type"]=="int":
                                        params[hyper["name"]]=(np.logspace(np.log10(hyper["range"]["min"]),np.log10(hyper["range"]["max"]),hyper["range"]["num_samp"])).astype(int)
                                    else:
                                        params[hyper["name"]]=(np.logspace(np.log10(hyper["range"]["min"]),np.log10(hyper["range"]["max"]),hyper["range"]["num_samp"]))
                        else:
                            if hyper["type"]=="option":
                                params[hyper["name"]]=hyper["options"]
        model=eval(model_str)
        sys.stdout=open("logs.log","a+")
        with open("logs.log","a+") as f:
            f.write(modelname)
    
        clf=RandomizedSearchCV(model, params,verbose=51,n_jobs=-1)
        
        x_train,x_test,y_train,y_test=train_test_split(xdata,ydata,test_size=test_ratio)
        print("working on "+ modelname)
        clf.fit(x_train,y_train)
        hyperparams[modelname]=clf.best_params_
        
        print("model completed for " + modelname)
        
        location=os.path.join(dataconfig["location"],str(dataconfig["id"])+"_model")
        picklepath=os.path.join(location,(str(modelname) +".pkl"))
        with open(picklepath,"wb") as f:
            pickle.dump(clf,f)
            
        prediction=clf.predict(x_test)
        metricsrow=met.calculate_metrics(modelname,model_type,prediction,y_test)
        print("hyper params are : ",hyperparams[modelname]," for ",modelname)
        return metricsrow, hyperparams