from pycaret.classification import *
from pycaret.regression import *
# from pycaret.clustering import *
# from pycaret.nlp import *
import os
import pandas as pd
import joblib
import shutil
import yaml
from yaml.loader import SafeLoader

class auto:
    #df = raw_data_address
    #target_col_name = target_col_name
    #problem_type = problem_type
    #na_value = na_value
    #encoding_type=encoding_type
    #encode_col_name=encode_col_name
    #scaling_type = scaling_type
    #scaling_col_name=scaling_col_name
    
    def auto_setup(self,config):   
        """
        This function is for preprocessing the data when the user selects auto.
    
        Extended description of function:-
        Parameters:
            problem_type (string):          (The selection of the user for the model_type eg-classification/regression/clustering etc.)
            raw_data_address (string):    (As the user uploads the raw dataset it will be saved in the database, this is the address of that saved dataset.)
            target_col_name (string):     (The user will select the target cloumn/variable and that target variable name have to be passed to the setup() in pycaret as patameter.)
            
        """
<<<<<<< HEAD
        with open(config) as f:
            config = yaml.load(f, Loader=SafeLoader)
=======
        df = pd.read_csv(config.raw_data_address)
        
>>>>>>> 7922206cfa46a76e31bcc561d015da41e75a7a6b
        if config.problem_type == "classification":
            clf1 = setup(data = df, target = config.target_col_name,silent=True, profile= True)
        elif config.problem_type== "regression":
            reg1 = setup(data = df, target = config.target_col_name,silent=True, profile= True)
        elif config.problem_type == "clustering":
            clu1 = setup(data = df,silent=True, profile= True)
        elif config.problem_type == "nlp":
            nlp1 = setup(data = df, target = config.target_col_name,silent=True, profile= True)
        X_train = get_config('X_train')    
        X_train.to_csv('clean_data.csv', index=False)
        clean_data_address = os.getcwd()+"/clean_data.csv"

        return clean_data_address     


    def top_models_auto(self,config,n=3):
        with open(config) as f:
            config = yaml.load(f, Loader=SafeLoader)

        """
        This funtion takes the user input n in integer format and feeds it to the pycaret function and pycaret in turn returns the top n funtion in an array format 
        The array containing classifiers is returned at the end of the function 
        """
        best = compare_models(n_select=n)
        request=pull()

        with open(os.path.join(config.loation,"metrics.csv"),"w+") as f:
            f.write(request.to_csv())
            f.close()
        return best

    
    def model_tune(self,model_array):
        tuned_best=[]
        for i in model_array:
            tuned_best.append(tune_model(i))

        return tuned_best


    def model_save(self,model_array,config):
        """
        Saves the pkl file at the specified location 
        Ex:
        myfirstexp01_model01.pkl

        here myfirstexp is the name of the experiment started by the user.
        01 is the id or the run number of the test this is inplace made to avoid repetition of names in subsequent runs on the same data set within the experiment
        """
        with open(config) as f:
            config = yaml.load(f, Loader=SafeLoader)
        for i in range(len(model_array)):
            name=str(config.experimentname)+"_"+str(config.id)+"_model"+str(i)
            save_model(model_array[i],name) ## file name will be experimentname_id_model(number)
            shutil.move(name+".pkl",str(config.location)+str(config.id)+"_model"+str(i)) ##moves  the pkl to the respective folders at the specified location 
            ## folder name is of the form ex:"01_model1" 

    
    def model_plot(self,model_array,config):

        with open(config) as f:
            config = yaml.load(f, Loader=SafeLoader)
        if config.problem_type=="classification":
            feature_list=["feature","auc","pr","confusion_matrix","error","learning"]
            for i in range(len(model_array)):
                plot_list=[]
                location=str(config.location)+str(config.id)+"_model"+str(i) ##
                os.mkdir(location) ## creates a folder by the name configid_model(number) at the specified location
                os.mkdir(os.path.join(location,"plots").replace("\\","/")) ## creates a subfolder named plots to store all the plots inside it
                for feature in feature_list:
                    try:
                        plot_list.append(plot_model(model_array[i],feature,save=True))
                    except TypeError:
                        pass
                for f in plot_list:
                    shutil.move(f, os.path.join(location,"plots"))

        if config.problem_type=="regression":
            feature_list=["feature","residuals","cooks","vc","error","learning"]
            for i in range(len(model_array)):
                location=str(config.location)+str(config.id)+"_model"+str(i)
                os.mkdir(location)
                os.mkdir(os.path.join(location,"plots").replace("\\","/"))
                plot_list=list(plot_model(model_array[i],feature,save=True) for feature in feature_list)
                for f in plot_list:
                    shutil.move(f, os.path.join(location,"plots"))

   
        
        
    def auto(self,config):
    
        clean_data=self.auto_setup(config)
        model_list=self.top_models_auto(config.n)
        tuned_list=self.model_tune(model_list)
        #self.model_plot(tuned_list,config) "as of now deemed unwanted feature anywhere"
        self.model_save(tuned_list)
        