from numpy.core.numeric import NaN
from sklearn.metrics import accuracy_score , recall_score, precision_score, f1_score, cohen_kappa_score, matthews_corrcoef
from sklearn.metrics import mean_absolute_error,auc,mean_squared_error,r2_score,mean_squared_log_error,roc_auc_score


class Metrics:

    def calculate_metrics(modelname,model_type,prediction,y): # nested list


        if model_type=="Classification":
            criterias=["accuracy_score","recall_score","precision_score","f1_score","cohen_kappa_score","roc_auc_score"]
        #metrics.loc[len(metrics.index)]=[modelname,accuracy_score(y,prediction),recall_score(y,prediction),precision_score(y,prediction),f1_score(y,prediction),cohen_kappa_score(y,prediction),matthews_corrcoef(y,prediction)]

        elif model_type=="Regression":
            criterias=["mean_absolute_error","mean_squared_error","r2_score","mean_squared_log_error"]

        metricsnewrow=[modelname]
        for criteria in criterias:
            try:
                if criteria=="mean_squared_log_error":
                    metricsnewrow.append((round(eval(criteria+"(y,prediction)"),2))**0.5)

                elif criteria == "mean_squared_error":
                    mse=round(eval(criteria+"(y,prediction)"),2)
                    metricsnewrow.append(mse)
                    metricsnewrow.append(mse**(1/2))
                    
                else:
                    metricsnewrow.append(round(eval(criteria+"(y,prediction)"),2))
            except Exception as e:
                
                try:
                    if model_type=="Classification":
                        metricsnewrow.append(round(eval(criteria+"(y,prediction,average='micro')"),2))
                    

                except:
                    print("unsolvable error")
                    metricsnewrow.append("Not Available")

            # else:
            #     metricsnewrow.append("Not Available")
            
        
        print(metricsnewrow)
        return metricsnewrow