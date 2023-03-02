import json
import pandas as pd
from sodapy import Socrata


class Get_Data():
    def __init__(self, df= pd.DataFrame()):
        self.df= df
    
    def create_df(self):
        
        client = Socrata("data.lacity.org", None)
        results = client.get("2nrs-mtv8", limit=800000)
        results_df = pd.DataFrame.from_records(results)
        results_df.to_csv(r'lapd.csv')
        self.df = results_df
        
    def infer_dtypes(self):
        ls_dates=["date_rptd", "date_occ"]
        ls_numeric=["vict_age","lat", "lon"]
        ls_strings=[x for x in self.df.columns if x not in ls_dates+ls_numeric]
        for date in ls_dates:
            self.df[date]= pd.to_datetime(self.df[date])
        for num in ls_numeric:
            self.df[num]= pd.to_numeric(self.df[num])
        for s in ls_strings:
            self.df[s].apply(lambda x: str(x).split(','))
        self.df["time_occ"]=self.df["time_occ"].apply(lambda x: int(x[0:2])*60+int(x[2:]))


#Data= Get_Data()
#Data.create_df()
#Data.infer_dtypes()
#df= Data.df.copy()
#print(df.info())



