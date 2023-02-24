import seaborn as sns
import matplotlib.pyplot as plt
import sys
sys.path.insert(0,".")
from Class_GetData import Get_Data

class Graphs_Cont():
    
    def __init__(self):
        self.titulos={ "lon": "Longitud", "lat": "Latitud",
                       "vict_age": "Edad de la victima", 
                       "time_occ": "Hora del suceso"}
        self.ls_numeric= ["vict_age","lat", "lon", "time_occ" ]
    def hist(self, df):
        for num in self.ls_numeric:
            plt.clf()
            g=sns.histplot(x= num, data= df, bins= 30).set(title= 'Histograma '+str(self.titulos[num]))
            plt.savefig('Graphs/Histograma_'+str(num) +'.png')
            
    def box(self,df):
        plt.clf()
        g=sns.boxplot(y= "time_occ", x="area_name", data= df)
        g.set(title="Hora del suceso en distintas areas")
        g.set_xticklabels(labels= df["area_name"].unique(),rotation= 90)
        plt.savefig('Graphs/Boxplot_time.png')
        plt.clf()
        g=sns.boxplot(y= "vict_age", x="area_name", data= df)
        g.set(title="Edad victima en distintas areas")
        g.set_xticklabels(labels= df["area_name"].unique(),rotation= 90)
        plt.savefig('Graphs/Boxplot_vict_age.png')

    def heatMap(self,df):
        sns.heatmap(data= df[self.ls_numeric].corr(), annot=True)
        plt.savefig('Graphs/HeatMap.png')
        
    def scatter(self,df):
        g=sns.scatterplot(x='lon', y= 'lat', data= df).set(title="Geolocalización ")
        plt.savefig("Graphs/Geolocalizacion.png")

Data= Get_Data()
Data.create_df()
Data.infer_dtypes()
df= Data.df.copy()

graphs= Graphs_Cont()
graphs.box(df)
graphs.heatMap(df)
graphs.scatter(df)
graphs.hist(df)