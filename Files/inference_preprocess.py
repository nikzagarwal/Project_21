import shutil
import numpy as np
import pandas as pd

# Handling missing data using-
from sklearn.impute import KNNImputer

# Handling non-numeric data using-
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder 

from yaml.loader import FullLoader
import os
import yaml
from scipy import stats

class InferencePreprocess:     
    def inference_preprocess(self,config,folderLocation):

        with open(config) as f:
            config_data= yaml.load(f,Loader=FullLoader) 
  
        df = pd.read_csv(config_data["inference_data_address"])
        df.dropna(how='all', axis=1, inplace=True)


        if config_data['drop_column_name'] != []:
            df=df.drop(config_data["drop_column_name"], axis = 1)

            
        if config_data['imputation_column_name'][0] != []:
            for index, column in enumerate(config_data["imputation_column_name"]):

                if config_data["impution_type"][index] =='knn':
                    df_value = df[[column]].values
                    imputer = KNNImputer(n_neighbors = 4, weights = "uniform",missing_values = np.nan)
                    df[[column]] = imputer.fit_transform(df_value)

                if config_data["impution_type"][index] != 'knn':
                    replace_value = config_data["mean_median_mode_values"][index] 
                    df[column].replace(to_replace = np.nan, value = replace_value)

        else:
            for col_name in df.columns:
                if df[col_name].dtype == 'object':
                    df.replace(to_replace =[config_data["na_notation"]],value ="No data")
                else:
                    df.replace(to_replace =[config_data["na_notation"]],value =0)

        if config_data['scaling_column_name'][0] != []:
            for index, column in enumerate(config_data["scaling_column_name"]):
                scaling_type = config_data["scaling_type"][index]                
                df_value = df[[column]].values

                if scaling_type == "normalization":
                    mi = config_data['scaling_values'][index]['min']
                    ma = config_data['scaling_values'][index]['max']
                    df_std = (df_value - mi) / (ma - mi)
                    scaled_value = df_std * (1 - 0)

                elif scaling_type == 'standarization':
                    mi = config_data['scaling_values'][index]['min']
                    mean = config_data['scaling_values'][index]['mean']
                    ma = config_data['scaling_values'][index]['max']
                    df_std = (df_value - mi) / (ma - mi)
                    scaled_value = (df_value - mean) / df_std 

                df[[column]] = scaled_value
            

        if config_data['encode_column_name'][0] != []:
            for index, column in enumerate(config_data["encode_column_name"]):
                encoding_type = config_data["encoding_type"][index]

                if df[column].dtype == 'object'and df[column].nunique() > 30:
                    df=df.drop(column, axis = 1)

                if config_data["target_column_name"] == column and df[column].dtype == 'object':
                    config_data["encoding_type"][index] = "Label Encodeing"
                    encoder = LabelEncoder()
                    df[column] = encoder.fit_transform(df[column])
                    label_encoding_dict = dict(zip(encoder.classes_, range(len(encoder.classes_))))
                    config_data['labels'] = label_encoding_dict
                    
                elif df[column].dtype != 'object'and df[column].nunique() > 30:
                    pass          
                
                elif config_data["target_column_name"] == column and df[column].dtype != 'object':
                    pass


                elif encoding_type == "Label Encodeing":
                    encoder = LabelEncoder()
                    df[column] = encoder.fit_transform(df[column])

                elif encoding_type == "One-Hot Encoding":
                    encoder = OneHotEncoder(drop = 'first', sparse=False)
                    df_encoded = pd.DataFrame (encoder.fit_transform(df[[column]]))
                    df_encoded.columns = encoder.get_feature_names([column])
                    df.drop([column] ,axis=1, inplace=True)
                    df= pd.concat([df, df_encoded ], axis=1)
            

        ### Default    

        for column in df.columns:
            if df[column].dtype == 'object'and df[column].nunique() > 30:
                df=df.drop(column, axis = 1)

        if df[config_data["target_column_name"]].dtype == 'object':
            print("lc")
            encoder = LabelEncoder()
            df[config_data["target_column_name"]] = encoder.fit_transform(df[config_data["target_column_name"]])
            print(encoder.classes_)
            label_encoding_dict = dict(zip(encoder.classes_, range(len(encoder.classes_))))
            config_data['labels'] = label_encoding_dict


        objest_type_column_list = []
        for column in df.columns:
            if df[column].dtype == 'object':
                objest_type_column_list.append(column)
                config_data['encode_column_name'].extend([column])
                config_data['encoding_type'].extend(['One-Hot Encoding'])

        if objest_type_column_list != []:
            print(objest_type_column_list)
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
                
        df.to_csv('inference_clean_data.csv')
        shutil.move("inference_clean_data.csv",folderLocation)
        inference_clean_data_address = os.path.abspath(os.path.join(folderLocation,"inference_clean_data.csv"))
        config_data['inference_clean_data_address'] = inference_clean_data_address

        with open(config, 'w') as yaml_file:
            yaml_file.write( yaml.dump(config_data, default_flow_style=False))
        
        return inference_clean_data_address