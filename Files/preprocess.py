import shutil
import numpy as np
import pandas as pd

# Handling missing data using-
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
 
# Handling non-numeric data using-
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder 

import os
import yaml
from yaml.loader import FullLoader
from scipy import stats

class Preprocess:     
    def manual_preprocess(self,config, folderLocation):
        """
        This function is for preprocessing the data when the user selects manual preprocessing.                     
        """
        with open(config) as f:
            config_data= yaml.load(f,Loader=FullLoader) 
        # config_data = yaml.safe_load(open("preprocess_config.yaml",'r'))
        df = pd.read_csv(config_data["raw_data_address"])
        
        df.dropna(how='all', axis=1, inplace=True)

        
        if config_data["is_auto_preprocess"] == False:
    
            if config_data['imputation_column_name'][0] != []:
                del config_data['imputation_column_name'][0]
                del config_data['impution_type'][0]
                strategy_values_list=[]

                for index, column in enumerate(config_data["imputation_column_name"]):
                    if df[column].dtype == object:
                        type = "most_frequent"
                    else:
                        type = config_data["impution_type"][index] 
                    if type == "mean":
                        df_value = df[[column]].values
                        imputer = SimpleImputer(missing_values = np.nan, strategy = "mean")
                        strategy_values_list.append(df[column].mean())
                        df[[column]] = imputer.fit_transform(df_value)
                    elif type == "median":
                        df_value = df[[column]].values
                        imputer = SimpleImputer(missing_values =  np.nan, strategy = "median")
                        strategy_values_list.append(df[column].median())
                        df[[column]] = imputer.fit_transform(df_value)
                    elif type == "most_frequent":
                        df.fillna(df.select_dtypes(include='object').mode().iloc[0], inplace=True)
                        strategy_values_list.append(df[column].mode())
                    elif type=='knn':
                        df_value = df[[column]].values
                        imputer = KNNImputer(n_neighbors = 4, weights = "uniform",missing_values =  np.nan)
                        df[[column]] = imputer.fit_transform(df_value)

                if strategy_values_list != [] :
                    config_data['mean_median_mode_values'] = strategy_values_list

            if config_data['scaling_column_name'][0] != []:
                del config_data['scaling_column_name'][0]
                del config_data['scaling_type'][0]

                for index, column in enumerate(config_data["scaling_column_name"]):
                    if df[column].dtype == object and config_data["target_column_name"] == column:
                        pass
                    else:  
                        type = config_data["scaling_type"][index]
                        config_data['scaling_values'] = {}
                        df_value = df[[column]].values

                        if type == "normalization":
                            df_std = (df_value - df_value.min(axis=0)) / (df_value.max(axis=0) - df_value.min(axis=0))
                            scaled_value = df_std * (1 - 0)

                            config_data['scaling_values'][index]={"min":df_value.min(axis=0),"max":df_value.max(axis=0)}

                        elif type == 'standarization':
                            df_std = (df_value - df_value.min(axis=0)) / (df_value.max(axis=0) - df_value.min(axis=0))
                            scaled_value = (df_value - df_value.mean()) / df_std 

                            config_data['scaling_values'][index]={"std":df_std,"mean":df_value.mean()}

                        df[[column]] = scaled_value
            
            if config_data['drop_column_name'] != []:
                del config_data['drop_column_name'][0]
                for index, column in enumerate(config_data["drop_column_name"]):
                    if(config_data["target_column_name"] != column):
                        df=df.drop(column, axis = 1)
            
            if config_data['encode_column_name'][0] != []:
                del config_data['encode_column_name'][0]
                del config_data['encoding_type'][0]
                for index, column in enumerate(config_data["encode_column_name"]):
                    if column not in config_data["drop_column_name"]:
                        
                        type = config_data["encoding_type"][index]
                        
                        if config_data["target_column_name"] == column or df[column].nunique() > 30:
                            encoder = LabelEncoder()
                            df[column] = encoder.fit_transform(df[column])
                            label_encoding_dict = dict(zip(encoder.classes_, range(len(encoder.classes_))))
                            config_data['labels'] = {}
                            config_data['labels']= [label_encoding_dict]
                        
                        elif df[column].dtype == 'object'and df[column].nunique() > 30:
                            df=df.drop(column, axis = 1)
                        
                        elif type == "Label Encoding" :
                            encoder = LabelEncoder()
                            df[column] = encoder.fit_transform(df[column])
                            label_encoding_dict = dict(zip(encoder.classes_, range(len(encoder.classes_))))
                            config_data['labels'] = {}
                            config_data['labels']= [label_encoding_dict]

                        elif type == "One-Hot Encoding":
                            encoder = OneHotEncoder(drop='first', sparse=False)
                            df_encoded = pd.DataFrame (encoder.fit_transform(df[[column]]))
                            df_encoded.columns = encoder.get_feature_names([column])
                            df.drop([column] ,axis=1, inplace=True)
                            df= pd.concat([df, df_encoded ], axis=1)
            
            
        ### Default
        for col_name in df.columns:
            if df[col_name].dtype == 'object'and df[col_name].nunique() > 30:
                df=df.drop(col_name, axis = 1)
                
        objest_type_column_list = []
        for col_name in df.columns:
            if df[col_name].dtype == 'object':
                objest_type_column_list.append(col_name)
                config_data['encode_column_name'].extend([col_name])
                config_data['encoding_type'].extend(['One-Hot Encoding'])

        if objest_type_column_list != []:
            for column in objest_type_column_list:
                encoder = OneHotEncoder(drop = 'first', sparse=False)
                df_encoded = pd.DataFrame (encoder.fit_transform(df[[column]]))
                df_encoded.columns = encoder.get_feature_names([column])
                df.drop([column] ,axis=1, inplace=True)
                df= pd.concat([df, df_encoded ], axis=1)



            if config_data["Remove_outlier"] == True:
                z = np.abs(stats.zscore(df))
                df = df[(z < 3).all(axis=1)]

            # Here we are selecting the column which are having more then 70 correlation.
            if config_data["feature_selection"] == True:
                col_corr = set()
                corr_matrix = df.corr()
                for i in range(len(corr_matrix.columns)):
                        for j in range(i):
                            if abs(corr_matrix.iloc[i, j]) > 0.90:
                                col_corr.add(corr_matrix.columns[i])

                df = df.drop(col_corr,axis=1)




        df.to_csv('clean_data.csv')
        shutil.move("clean_data.csv",folderLocation)
        clean_data_address = os.path.abspath(os.path.join(folderLocation,"clean_data.csv"))
        config_data['clean_data_address'] = clean_data_address
    
        with open(config, 'w') as yaml_file:
            yaml_file.write( yaml.dump(config_data, default_flow_style=False))

        return clean_data_address