from pmdarima import auto_arima
#from fbprophet import Prophet
import json
#from fbprophet.serialize import model_to_json, model_from_json
import os
import yaml
from yaml.loader import FullLoader
import plotly
import pandas as pd
import plotly.express as ex
import shutil
#import kaleido
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima.arima import StepwiseContext
from statsmodels.tsa.arima_model import ARIMAResults
import random
from Files.metrics import Metrics as met
import warnings
import pickle 
from statsmodels.graphics.tsaplots import acf,pacf
import pmdarima as pm
import sys
import numpy as np
from Files.hyperparameter import hyperparameter as hp
from Files.training import training as train
import plotly.express as px
import plotly.graph_objects as go
import random
from Files.autoreg import AutoReg as auto
from pycaret.regression import *
class timeseries:
    def createprophet(self,dataconfig):
        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader)
        data=dataconfig["data"]
        location=dataconfig["location"]
        model=Prophet()
        testsize=int(len(data)*0.2)
        train=data.iloc[:-testsize]
        test=data.iloc[-testsize:]
        model.fit(train)
        pred=model.predict(test)
        pred=pred.yhat
        actual=test.y

        metrics=met.calculate_metrics("fbprophet","Regression",pred,actual)
        metricsLocation=os.path.join(dataconfigfile["location"],"metrics.csv")
        metrics.to_csv(metricsLocation, index=True)

        compare=pd.DataFrame(pred.values,columns=['predictions'])
        compare['actual']=actual.values
        print(compare)
        fig=compare.plot(legend=True)
        plotly.offline.plot(fig,filename=os.path.join(location,"fbtestvspred.html"))

        modelfinal=Prophet()
        modelfinal.fit(data)
        location="serialized_model.json"
        location=os.path.join(dataconfigfile['location'],str(dataconfigfile['projectname'])+str('fb'))
        with open(location, 'w') as fout: #save the model
            json.dump(model_to_json(modelfinal), fout)
        return location

    def fbinference(self,location,number):
        with open(location, 'r') as fin:
            model = model_from_json(json.load(fin))
        future=model.make_future_dataframe(periods=number)
        pred=model.predict(future)
        return pred

    def createarima(self,dataconfig):
        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader)
        metrics=pd.DataFrame(columns=['modelname','mean_absolute_error','mean_squared_error','r2_score','mean_squared_log_error'])
        
        data=pd.read_csv(dataconfigfile["clean_data_address"])
        location=dataconfigfile["location"]
        choice=dataconfigfile['frequency']
        diction={"D":7,"W":52,"M":12,"Q":4,"Y":2,}
        freq=24
        if choice in diction:
            freq=diction[choice]
        else:
            freq=12
        print("frequency",freq)
        with open("logs.log","a+") as f:
            f.write("Frequency="+str(freq)+"\n")
            f.write("Creating Arima models\n")
            f.write("Please wait trying different models...\n")
            f.write("Trained on several models\n")
            f.write("Selecting best model\n")
            f.close()
        # warnings.filterwarnings("ignore")
        # sys.stdout=open("logs.log","a+")
        with StepwiseContext(max_dur=15):
            model = pm.auto_arima(data, stepwise=True, error_action='ignore', seasonal=True,m=freq,trace=True)
        # sys.stdout.close()
        #metrics=met.calculate_metrics("fbprophet","Regression",testpred,testactual)
        order=model.get_params(deep=False)['order']
        seasonal=model.get_params(deep=False)['seasonal_order']
        print("order=",order)
        print("seasonal",seasonal)
        print("frequency",freq)
        modelfinal=SARIMAX(data,order=order,seasonal_order=seasonal).fit()
        
        start=1
        end=len(data)
        compare=modelfinal.predict(start=start,end=end,typ='levels')
       
        compare.index=data.index

        metrics_new_row=met.calculate_metrics("arima","Regression",data['y'],compare)
        metricsLocation=os.path.join(dataconfigfile["location"],"metrics.csv")
        metrics.loc[len(metrics.index)]=metrics_new_row
        metrics.to_csv(metricsLocation, index=True)
        r2score=metrics_new_row[3]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index,y=data.y,name="actual"))

        fig.add_trace(go.Scatter(x=compare.index,y=compare,name="predictions"))
  
 
        plotlocation=dataconfigfile['location']
        plotlocation=os.path.join(plotlocation,"plot.html")
        acf_=acf(data['y'])
        acf_=pd.DataFrame(acf_,columns=['data'])
        pacf_=pacf(data['y'])
        pacf_=pd.DataFrame(pacf_,columns=['data'])
        fig2=self.plot_graphs(acf_,"Auto correlative function")
        fig3=self.plot_graphs(pacf_,"Partial-Auto correlative funtion")
        with open(plotlocation, 'a') as f:
            f.write(fig.to_html(include_plotlyjs='cdn',full_html=False))
            f.write(fig2.to_html(include_plotlyjs='cdn',full_html=False))
            f.write(fig3.to_html(include_plotlyjs='cdn',full_html=False))
        f.close()

        # modelfinal=auto_arima(data['y'], trace=True,suppress_warnings=True, seasonal=True)
        location=os.path.join(dataconfigfile["location"],str(dataconfigfile["id"])+"_model")
        os.makedirs(location)
        name=str(dataconfigfile["experimentname"])+str(dataconfigfile["id"])+"_model"
        # modelfinal.save(name)
        pickleFilePath =os.path.join(location,name)
        with open(pickleFilePath, 'wb') as pkl:
            pickle.dump(modelfinal, pkl)

        # shutil.move(name,location)

        
        
        return {"Successful": True, "cleanDataPath": dataconfigfile["clean_data_address"], "metricsLocation":metricsLocation, "pickleFolderPath":location, "pickleFilePath":pickleFilePath,"plotLocation":plotlocation, "accuracy":r2score}
        
    def arimainference(self,pickleFileLocation,storeLocation,daysintothefuture):
        print(pickleFileLocation)
        model=ARIMAResults.load(pickleFileLocation)
        predictions=model.forecast(daysintothefuture)
        predictions=pd.DataFrame({"predictions":predictions})
        print(predictions)
        # ran=random.randint(100,999)
        csvresults=predictions.to_csv()
        inferenceDataResultsPath=os.path.join(storeLocation,"inference.csv")
        inference=open(inferenceDataResultsPath,"w+")
        inference.write(csvresults)
        inference.close()

        return inferenceDataResultsPath

    def plot_graphs(self,acf,name):
    
        acfig = px.bar(acf, x=acf.index, y="data",title=name)
        # acfig.show()
        return acfig

    def plotinference(self,predictionsPath,storeLocation,cleanDataPath,daysIntoFuture,frequency):
        
        data=pd.read_csv(cleanDataPath)
        predictions=pd.read_csv(predictionsPath)
        index_of_fc = pd.date_range(data.index[-1], periods = daysIntoFuture,freq=frequency)
        fig = go.Figure()
        ran=random.randint(100,999)
        fig.add_trace(go.Scatter(x=data.index,y=data.y,name="actual"))
        fig.add_trace(go.Scatter(x=index_of_fc,y=predictions.predictions,name="predictions"))
        # fig=go.Figure(data=go.Scatter(x=predictions.index,y=predictions.predictions))
        fig.write_html(os.path.join(storeLocation,"inference.html"))

        return os.path.join(storeLocation,"inference.html")

    def rftimeseriespreprocess(self,data):  
        length=len(data)
        y=data['y']
        trend_1=[0]*length
        trend_2=[0]*length
        period7_seasonality=[0]*length
        period12_seasonality=[0]*length
        period30_seasonality=[0]*length
        period52_seasonality=[0]*length
        period365_seasonality=[0]*length
        for i in range(2,length):
            trend_1[i]=y[i-1]-y[i-2]
            if i > 3:
                trend_2[i]=(trend_1[i-1]-trend_1[i-2])
            if i > 6:
                period7_seasonality[i]=(y[i-7])
            if i > 11:
                period12_seasonality[i]=(y[i-12])
            if i > 29:
                period30_seasonality[i]=(y[i-30])
            if i > 51:
                period52_seasonality[i]=(y[i-52])
            if i > 364:
                period365_seasonality[i]=(y[i-365])
        data['trend_1']=trend_1
        data['trend_2']=trend_2
        data['period7_seasonality']=period7_seasonality
        data['period12_seasonality']=period12_seasonality
        data['period30_seasonality']=period30_seasonality
        data['period52_seasonality']=period52_seasonality
        data['period365_seasonality']=period365_seasonality
        indexes=data.ds[0]
        data.reset_index(drop=True, inplace=True)
        try:
            data.drop(['ds'],inplace=True,axis=1)
        except:
            pass
        print(data)
        data.to_csv('timeseries.csv',index_label=False)
        return indexes

    def rfinference(self,days,modelpath,indexes,freq,dataconfig):

        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader)
        df=pd.read_csv('timeseries.csv')
        #df2=df.drop(['y'],inplace=True,axis=1)
        for i in range(days):
            index=len(df)
            trend_1=df.iloc[-1]['y']-df.iloc[-2]['y']
            trend_2=df.iloc[-1]['trend_1']-df.iloc[-2]['trend_1']
            try:
                period7_seasonality=df.iloc[-7]['y']
            except:
                period7_seasonality=0
            try:
                period12_seasonality=df.iloc[-12]['y']
            except:
                period12_seasonality=0
            try:
                period30_seasonality=df.iloc[-30]['y']
            except:
                period30_seasonality=0
            try:
                period52_seasonality=df.iloc[-52]['y']
            except:
                period52_seasonality=0
            try:
                period365_seasonality=df.iloc[-365]['y']
            except:
                period365_seasonality=0
            x=np.array([ trend_1, trend_2, period7_seasonality,
            period12_seasonality, period30_seasonality, period52_seasonality,
            period365_seasonality])
            model=pickle.load(open(modelpath,"rb"))
            x=x.reshape(1,8)
            print('x_shape',x.shape)
            x=pd.DataFrame(x)
            y=model.predict(x)
            print('y is ',y)
            x=[y[0], trend_1, trend_2, period7_seasonality,
            period12_seasonality, period30_seasonality, period52_seasonality,
            period365_seasonality]
            
            df.loc[len(df.index)] =x
            print('last row',df.iloc[-1])
        
        
        new_index=pd.date_range(start=indexes,periods=len(df.index),freq=freq)
        df.index=new_index
        inferencelocation=os.path.join(str(dataconfigfile['location']),'inference.csv')
        df.to_csv(inferencelocation,index_label=False)
        return inferencelocation
        
    def plotinferencerf(self,inferencelocation,storeLocation,):
        data_original=pd.read_csv('timeseries.csv')
        data=pd.read_csv(inferencelocation)
        fig = go.Figure()
        ran=random.randint(100,999)
        fig.add_trace(go.Scatter(x=data_original.index,y=data_original.y,name="actual"))
        fig.add_trace(go.Scatter(x=data.index,y=data.y,name="predictions"))
        # fig=go.Figure(data=go.Scatter(x=predictions.index,y=predictions.predictions))
        fig.write_html(os.path.join(storeLocation,"inference.html"))

        return os.path.join(storeLocation,"inference.html")


    def timeseriesmanual(self,userinputconfig,dataconfig,preprocessconfig):
        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader)

        location=dataconfigfile["location"]
        freq=dataconfigfile['frequency']
        data=pd.read_csv(location)
        indexes=self.rftimeseriespreprocess(self,dataconfig)
        train.train(self,userinputconfig,dataconfig,preprocessconfig,'timeseries.csv')

        return indexes,freq

    def rftimeseriespreprocess(self,data):  
        length=len(data)
        y=data['y']
        trend_1=[0]*length
        trend_2=[0]*length
        period7_seasonality=[0]*length
        period12_seasonality=[0]*length
        period30_seasonality=[0]*length
        period52_seasonality=[0]*length
        period365_seasonality=[0]*length
        for i in range(2,length):
            trend_1[i]=y[i-1]-y[i-2]
            if i > 3:
                trend_2[i]=(trend_1[i-1]-trend_1[i-2])
            if i > 6:
                period7_seasonality[i]=(y[i-7])
            if i > 11:
                period12_seasonality[i]=(y[i-12])
            if i > 29:
                period30_seasonality[i]=(y[i-30])
            if i > 51:
                period52_seasonality[i]=(y[i-52])
            if i > 364:
                period365_seasonality[i]=(y[i-365])
        data['trend_1']=trend_1
        data['trend_2']=trend_2
        data['period7_seasonality']=period7_seasonality
        data['period12_seasonality']=period12_seasonality
        data['period30_seasonality']=period30_seasonality
        data['period52_seasonality']=period52_seasonality
        data['period365_seasonality']=period365_seasonality
        indexes=data['ds'][0]
        data.reset_index(drop=True, inplace=True)
        try:
            data.drop(['ds'],inplace=True,axis=1)
        except:
            pass
        print(data)
        data.to_csv('timeseries.csv',index=0)

        return indexes
        
    def rfinference(self,days,pickleFileLocation,dataPathLocation,indexes,freq):

        df=pd.read_csv(dataPathLocation)
        #df2=df.drop(['y'],inplace=True,axis=1)
        for i in range(days):
            index=len(df)
            trend_1=df.iloc[-1]['y']-df.iloc[-2]['y']
            trend_2=df.iloc[-1]['trend_1']-df.iloc[-2]['trend_1']
            try:
                period7_seasonality=df.iloc[-7]['y']
            except:
                period7_seasonality=0
            try:
                period12_seasonality=df.iloc[-12]['y']
            except:
                period12_seasonality=0
            try:
                period30_seasonality=df.iloc[-30]['y']
            except:
                period30_seasonality=0
            try:
                period52_seasonality=df.iloc[-52]['y']
            except:
                period52_seasonality=0
            try:
                period365_seasonality=df.iloc[-365]['y']
            except:
                period365_seasonality=0
            x=np.array([trend_1, trend_2, period7_seasonality,
            period12_seasonality, period30_seasonality, period52_seasonality,
            period365_seasonality])
            print('x shape preev',x.shape)
            model=load_model(pickleFileLocation)
            x=x.reshape(1,7)
            print('x_shape',x.shape)
            
            x=pd.DataFrame(x,columns=list(df.columns)[1:])
            
            y=model.predict(x)
            print('y is ',y)
            x=[y[0], trend_1, trend_2, period7_seasonality,
            period12_seasonality, period30_seasonality, period52_seasonality,
            period365_seasonality]

            df.loc[len(df.index)] =x
            print('last row',df.iloc[-1])


        new_index=pd.date_range(start=indexes,periods=len(df.index),freq=freq)
        df.index=new_index

        return df

    def timeseriesmanualrf(self,dataconfig):
        with open(dataconfig) as f:
            dataconfigfile= yaml.load(f,Loader=FullLoader)

        datalocation=dataconfigfile['data']

        freq=dataconfigfile['frequency']
        data=pd.read_csv(datalocation)
        print(data)
        indexes=self.rftimeseriespreprocess(self,data)
        print(indexes)
        dataconfigfile['raw_data_address']='timeseries.csv'
        dataconfigfile['indexes']=indexes
        print('creating new yaml')

        newpath=os.path.join(dataconfigfile['location'],"newconfig.yaml")
        print(newpath)
        with open(newpath, 'w') as f:
            f.write(yaml.safe_dump(dataconfigfile))
        print('starting training')
        auto(newpath)

        return indexes,freq
    def plotinferencerf(self,df,storeLocation,days,freq):
        data_original=pd.read_csv('timeseries.csv')
        data=df
        fig = go.Figure()
        index_of_fc = pd.date_range(start =df.index[0], periods = len(data_original),freq=freq)
        ran=random.randint(100,999)
        fig.add_trace(go.Scatter(x=df.index,y=df.y,name="predictions"))
        fig.add_trace(go.Scatter(x=index_of_fc,y=data_original.y,name="actual"))
        
        # fig=go.Figure(data=go.Scatter(x=predictions.index,y=predictions.predictions))
        fig.write_html(os.path.join(storeLocation,"inference.html"))

        return os.path.join(storeLocation,"inference.html")
        