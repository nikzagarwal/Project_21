import os
import yaml
from yaml.loader import SafeLoader
import pandas as pd
from pandas_profiling import ProfileReport


def plot(raw_data_address,folderLocation):
    df = pd.read_csv(raw_data_address)
    plotFileLocation=os.path.join(folderLocation,"plot.html")
    if(os.path.exists(plotFileLocation)):
        return plotFileLocation
    else:
        if (df.shape[1] <= 15):
            profile = ProfileReport(df,title="Project-21 Report")
            profile.to_file(plotFileLocation)
        else:
            profile = ProfileReport(df,title="Project-21 Report",minimal=True)
            profile.to_file(plotFileLocation)
    return plotFileLocation
    
    