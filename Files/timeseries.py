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
        diction={"D":1,"W":7,"M":30,"Q":90,"Y":365,}
        freq=12  ##hard coded as of now
        with StepwiseContext(max_dur=15):
            model = auto_arima(data, stepwise=True, error_action='ignore', seasonal=True,m=freq,trace=True)
        #metrics=met.calculate_metrics("fbprophet","Regression",testpred,testactual)
        order=model.get_params(deep=False)['order']
        seasonal=model.get_params(deep=False)['seasonal_order']

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
        fig.write_html(os.path.join(plotlocation,"plot.html"))
        plotlocation=os.path.join(plotlocation,"plot.html")

        modelfinal=auto_arima(data['y'], trace=True,suppress_warnings=True, seasonal=True)
        location=os.path.join(dataconfigfile["location"],str(dataconfigfile["id"])+"_model")
        os.makedirs(location)
        name=str(dataconfigfile["experimentname"])+str(dataconfigfile["id"])+"_model"
        # modelfinal.save(name)
        with open(name, 'wb') as pkl:
            pickle.dump(modelfinal, pkl)

        shutil.move(name,location)

        pickleFilePath =os.path.join(location,name)
        
        return {"Successful": True, "cleanDataPath": dataconfigfile["clean_data_address"], "metricsLocation":metricsLocation, "pickleFolderPath":location, "pickleFilePath":pickleFilePath}
        
    def arimainference(self,pickleFileLocation,storeLocation,daysintothefuture):
        model=ARIMAResults.load(pickleFileLocation)
        predictions=model.forecast(daysintothefuture)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=predictions.index,y=predictions,name="predictions"))
        
        fig.write_html(os.path.join(storeLocation,"inference.html"))
        ran=random.randint(100,999)
        csvresults=predictions.to_csv()
        inferenceDataResultsPath=os.path.join(storeLocation,"inference"+str(ran)+".csv")
        inference=open(inferenceDataResultsPath,"w+")
        inference.write(csvresults)
        inference.close()

        return inferenceDataResultsPath,os.path.join(storeLocation,"inference.html")
