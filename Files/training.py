from pycaret.classification import *
from pycaret.regression import *
 

class training:
    def training(self,model_array,config,Xdata,Ydata):
        for i in model_array:
            i=0