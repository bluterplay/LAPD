from datetime import datetime
from pandas import date_range, read_csv, DataFrame
from statsmodels.tsa.api import SimpleExpSmoothing
from pickle import load

class CubeCrimesGenerator():
    
    def __init__(self,df):
        self.df = df.copy()
        data= self.df.copy()
        data["Date"]=data["date_rptd"]
        self.start= str(data["Date"].min())
        self.end= str(data["Date"].max())
        self.ls_dfs=[]
    
    def checkDates(self,data,zone,crimeType):
        data["Date"]=data["date_rptd"]
        date_index = date_range(start=self.start, end=self.end, freq="D")
        data = data.set_index("Date").reindex(date_index)
        data.drop(columns=["date_rptd"], inplace=True)
        field = "Crimes_Z"+str(zone)+"T"+str(crimeType)
        data.rename(columns={0: field}, inplace= True)
        data[field]= data[field].fillna(0)
        return data
       
    def generateDataframes(self):
        ls_dfs= []
        for zone in range(5):
            test = self.df[self.df['zonas']==zone].copy()
            for crime in range(100,105):
                test2 = test[test['crm_cd']==crime].copy()
                temp =test2.groupby('date_rptd').size().copy()
                temp= temp.to_frame()
                temp= temp.reset_index()
                data= self.checkDates(temp,zone,crime)
                self.ls_dfs.append(data)
                
    def generateCube(self):
        self.generateDataframes()
        df_final= self.ls_dfs[0]

        for i in range(1, len(self.ls_dfs)):
            column= self.ls_dfs[i].columns[0]
            df_final[column]= list(self.ls_dfs[i][column])
            
        return df_final
    
class FeatureEngineering():
    
    def __init__(self,df):
        self.df= df
        self.temp= DataFrame()
        
    def createLags(self,column):
        temp= self.df[[column]]
        for i in range(1,34):
            temp[column+"_"+str(i)] = temp[column].shift(i)
        self.temp=temp
    
    def smoothing(self, column):
        for i in range(2,10,1):
            j=i/10
            fit1 = SimpleExpSmoothing(self.temp[column], initialization_method="heuristic").fit(smoothing_level=j, optimized=False)
            lista=fit1.fittedvalues
            self.temp['exp'+str(j)]=lista
            
    def createMA(self,column):
        for i in range(10,50,10):
            self.temp["MA"+str(i)]= self.temp[column].rolling(window =i).mean()
    
    def scalerData(self,column,sc,sc2):
        X,y=self.temp.drop([column],axis=1).to_numpy(),self.temp[[column]].to_numpy(),

        X=sc.tansfomr(X)
        y=sc2.transform(y)


        X= X.reshape(X.shape[0], 1, X.shape[1])
        return X, y
    
    def createVariables(self,column):
        self.createLags(column)
        self.smoothing(column)
        self.createMA(column)
        self.temp.dropna(inplace=True)
        zone=column[8]
        crime=column[10:]
        scx_file="models/FeatureEngineer/Scalers/sc_x_"+crime+"_"+zone+".pkl"
        scy_file="models/FeatureEngineer/Scalers/sc_y_"+crime+"_"+zone+".pkl"
        with open(scx_file, "rb") as fp:
            sc= load(fp)
        with open(scy_file, "rb") as fp:
            sc2= load(fp)
        return self.scalerData(column,sc,sc2)
    
    
        


df = read_csv('DatosLimpiosSuperclases.csv')
zonas=read_csv('clusters.csv')
df=df.merge(zonas,left_on='dr_no',right_on='dr_no')
df_ = df[['date_rptd','crm_cd','zonas']]

test= CubeCrimesGenerator(df_)
cubo= test.generateCube()
print(cubo.head())

feat= FeatureEngineering(cubo)
feat.createVariables("Crimes_Z0T100")
print(feat.temp.head())