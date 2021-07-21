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
        diction={"D":30,"W":52,"M":12,"Q":4,"Y":2,}
        freq=24
        if choice in diction:
            freq=diction[choice]
        else:
            freq=12
        print("frequency",freq)
        # warnings.filterwarnings("ignore")
        with StepwiseContext(max_dur=15):
            model = pm.auto_arima(data, stepwise=True, error_action='ignore', seasonal=True,m=freq,trace=True)
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

        
        
        return {"Successful": True, "cleanDataPath": dataconfigfile["clean_data_address"], "metricsLocation":metricsLocation, "pickleFolderPath":location, "pickleFilePath":pickleFilePath,"plotLocation":plotlocation}
        
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