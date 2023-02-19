import requests
import json
import pandas as pd


class Get_Data():
    
    def create_df(self):
        
        r = requests.get('https://data.lacity.org/resource/2nrs-mtv8.json')
        r.status_code
        
        x= r.text[1:-1].split("\n")[:][1:]
        lista_textos = [x[1:] for x in r.text.split("\n")]
        
        lista_diccionarios = []

        for i in range(len(lista_textos)-2):
            resul = json.loads(lista_textos[i])
            lista_diccionarios.append(resul) 
            
        df = pd.DataFrame.from_dict(lista_diccionarios)
        
        return df
