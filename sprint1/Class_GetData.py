import requests
import json
import pandas as pd


class Get_Data():
    def __init__(self, df= pd.DataFrame()):
        self.df= df
    
    def create_df(self):
        
        r = requests.get('https://data.lacity.org/resource/2nrs-mtv8.json')
        r.status_code
        
        x= r.text[1:-1].split("\n")[:][1:]
        lista_textos = [x[1:] for x in r.text.split("\n")]
        
        lista_diccionarios = []

        for i in range(len(lista_textos)-2):
            resul = json.loads(lista_textos[i])
            lista_diccionarios.append(resul) 
            
        self.df = pd.DataFrame.from_dict(lista_diccionarios)
        
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


Data= Get_Data()
Data.create_df()
Data.infer_dtypes()
df= Data.df.copy()
df.to_csv("lapd.csv", index=False)

