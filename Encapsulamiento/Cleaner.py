import pandas as pd
import numpy as np
import csv
import pickle


class Cleaner():

    def __init__(self,data):
        self.df=data.copy()
        self.df.loc[self.df.vict_age==0,'vict_age']=np.nan
        self.df.loc[(self.df.vict_age<0)|(self.df.vict_age>100),'vict_age']=np.nan
        self.dc_cat= dc_cat={'status':['AA', 'AO', 'IC', 'JA'],
                            'vict_sex': ['F', 'H', 'M'],
                            'vict_descent': ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'O', 'P', 'S','U', 'V', 'W', 'X'],
                            'ucr': ['AGG. Assults', 'BRGLARY', 'BTFV', 'Homicide', 'MVT', 'OTHER THEFT','PERSONAL THFT', 'Rape', 'Robbery', 'SIMPLEASSAULT']}
        
    def dummies(self,df, ls,column):
        n=len(df)
        dc_values={key:[0 for x in range(n)] for key in ls}
        i=0
        for _,row in df.iterrows():
            try:
                a=ls.index(row[column])
                dc_values[row[column]][i]=1
            except:
                pass
            i+=1
        return pd.DataFrame(dc_values, index=df.index)
        
    def manageNan(self):
        # Concatenate crimes codes
        crm_cd_concat=self.df[['crm_cd_1','crm_cd_2','crm_cd_3','crm_cd_4']].fillna('').astype('string')
        crm_cd_concat=crm_cd_concat['crm_cd_1']+crm_cd_concat['crm_cd_2']+crm_cd_concat['crm_cd_3']+crm_cd_concat['crm_cd_4']
        self.df['crm_cd_concat']=crm_cd_concat
        # fill naś and typos
        self.df['weapon_desc'].fillna('NO WEAPON',inplace=True)
        self.df['weapon_used_cd'].fillna('0',inplace=True)
        self.df.loc[self.df.vict_sex.isna(),'vict_sex']='X'
        self.df.loc[self.df.vict_sex=='H','vict_sex']=='X'
        self.df.loc[self.df.vict_descent.isna(),'vict_descent']='U'
        self.df.loc[self.df.lon==0,['lat','lon']]=np.nan
        # Drop columns
        self.df.drop(['crm_cd_1','crm_cd_2','crm_cd_3','crm_cd_4','area_name','crm_cd_desc','premis_desc','weapon_desc', 'status_desc'],axis=1,inplace=True)
        try:
            self.df.drop(self.df.loc[self.df.status=='CC'].index,inplace=True)
        except:
            pass
        
    def manageLocation(self):
        # Delete spaces
        self.df.location = self.df.location.str.strip()
        self.df.location = self.df.location.apply(lambda x: "  ".join(x.split()))
        self.df.location = self.df.location.str.replace(" ", "")
        self.df.location = self.df.location.str.upper()
        # Replace with dictonary values
        directorio = pd.read_excel('Directorio_Lat_Lon.xlsx')
        directorio.location = directorio.location.str.replace(" ", "")
        directorio.location = directorio.location.str.upper()
        loc_lat = dict(zip(directorio.location,directorio.lat))
        loc_lon = dict(zip(directorio.location,directorio.lon))
        self.df.lat.fillna(self.df.location.map(loc_lat),inplace=True)
        self.df.lon.fillna(self.df.location.map(loc_lon),inplace=True)
        self.df.drop('location',axis=1,inplace=True)
        
    def clean(self):
        self.df.drop('cross_street',axis=1,inplace=True)
        self.manageNan()
        self.manageLocation()
    
    def createDummies(self):
        imputar=self.df.drop(['dr_no', 'date_rptd', 'date_occ','area',
                         'rpt_dist_no','part_1_2','crm_cd','mocodes','premis_cd',
                         'weapon_used_cd','crm_cd_concat','rpt_dist_no'],axis=1).copy()
        dum1= self.dummies(imputar,self.dc_cat["status"],"status")
        imputar.drop('status',axis=1,inplace=True)
        dum2= self.dummies(imputar,self.dc_cat["vict_sex"],"vict_sex")
        imputar.drop('vict_sex',axis=1,inplace=True)
        dum3= self.dummies(imputar,self.dc_cat["vict_descent"],"vict_descent")
        imputar.drop('vict_descent',axis=1,inplace=True)
        dum4= self.dummies(imputar,self.dc_cat["ucr"],"ucr")
        imputar.drop('ucr',axis=1,inplace=True)
        
        imputar=pd.concat([imputar,dum1,dum2,dum3,dum4],axis=1)

        return imputar
    
    def imputeAge(self):
        ucr=pd.read_csv('ucr.csv')
        ucr=ucr.astype({'Code':'string'})
        self.df=self.df.astype({'crm_cd':'string'})
        ucr=dict(zip(ucr['Code'],ucr['Subcategory']))
        self.df['ucr']=self.df.crm_cd.map(ucr)
        self.df.ucr=self.df.ucr.fillna('Other')
        
        imputar=self.createDummies()
        X=imputar[imputar.vict_age.isna()].copy()
        y=X.vict_age.values
        print(X.shape)
        X=X.drop('vict_age',axis=1).values
        print(X.shape)
        
        file = open("models/escaladorXEdad.pkl",'rb')
        sc_X = pickle.load(file)
        file.close()
        
        X=sc_X.transform(X)
        clf=pickle.load(open('models/edad_regresion.sav', 'rb'))
        y=clf.predict(X)
        self.df.loc[self.df.vict_age.isna(),'vict_age']=y
        
    def imputePremis(self):
        imputar=self.createDummies()
        X=imputar.loc[self.df.premis.isna(),imputar.columns!='premis']
        
        sc_X=pickle.load(open("models/escaladorXPremis.pkl", "rb"))
        X= sc_X.transform(X)
        
        clf=pickle.load(open('models/premis_clasificacion.sav', 'rb'))
        self.df.loc[self.df.premis.isna(),'premis']=clf.predict(X)
    
    def col_corr(self,codigo,descripcion):
        dicc=dict(zip(self.df[codigo],self.df[descripcion]))
        w = csv.writer(open(codigo+".csv", "w"))
        for key, val in dicc.items():
            w.writerow([key, val])
        self.df.drop(descripcion,axis=1,inplace=True)
        
    def categoricas(self):
        features=['rpt_dist_no','weapon_used_cd','premis']
        for feature in features:
            aux = self.df[feature].value_counts(True,dropna=False)
            ls_categories = [category for category, freq in aux.items() if freq > 0.03 or category is np.nan]
            self.df.loc[:,feature] = self.df[feature].map(lambda x: x if (x in ls_categories or x is np.nan) else "Others")
            
    def clipping(self):
        self.df['lon']=self.df['lon'].clip(-118.7, -118.1)
        self.df['lat']=self.df['lat'].clip(33.6, 34.4)
        
    def lugar(self):
        pl=[[[119,120,121,145,146.0,150.0,501.0, 502.0, 504.0,507.0, 508.0, 509.0, 510.0,511,515.0, 516.0,707],['vivienda']],
            [[101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 109.0, 110.0,116,117,
              124.0, 125.0,128,136.0, 137.0,152,154,158,415,705.0,748.0],['calle']],
            [[725.0, 726.0,240.0,732.0,752,753,756.0],['gobierno']],
            [[123,142,156,204.0, 213.0],['estacionamiento']],
            [[151.0,157.0,238,241,254,302,303,304.0, 305.0,702],['establecimiento']],
            [[201.0, 202.0, 203.0,205.0, 206.0,208,209.0, 210.0, 211.0,217.0, 218.0,
                                219.0, 220.0, 221.0, 222.0, 223.0, 224.0, 225.0,228,233.0,242,244.0, 245.0,
                                247.0, 248.0, 249.0,250.0, 251.0, 252.0,255,401.0, 402.0, 404.0, 405.0,
                                406.0, 407.0, 408.0,409.0, 410.0, 411.0, 412.0, 413.0, 414.0,417.0,703,
                                148.0,709,301,216
                                ],['establecimiento_publico']],
            [[207,706.0,733.0,735.0],['nocturno']],
            [[503,505,519.0],['hotel']],
            [[111.0, 112.0, 113.0, 114.0, 115.0,122,126,212.0, 214.0, 215.0,801.0, 802.0,804,809.0, 810.0,
                 811.0, 834.0, 835.0, 836.0, 868.0, 869.0, 870.0, 871.0, 872.0, 873.0,
                 874.0, 875.0, 876.0, 877.0, 878.0, 879.0, 880.0, 882.0, 883.0, 884.0,
                                885.0, 889.0, 890.0, 891.0, 892.0, 893.0, 894.0, 895.0, 896.0, 897.0,
                                898.0, 900.0, 901.0, 902.0, 903.0, 904.0, 905.0, 906.0, 907.0, 908.0,
                                909.0, 910.0, 911.0, 912.0, 913.0, 915.0, 916.0, 917.0, 918.0, 919.0,
                                920.0, 921.0, 922.0, 931.0, 932.0, 933.0, 934.0, 935.0, 936.0, 937.0,
                                940.0, 941.0, 942.0, 943.0, 944.0, 945.0, 946.0, 947.0, 948.0, 949.0,
                                950.0, 951.0, 952.0, 953.0, 954.0, 956.0, 957.0, 958.0, 961.0, 962.0,
                                963.0, 964.0, 965.0, 966.0, 967.0, 968.0, 969.0, 970.0, 971.0,129,135
                               ],['transporte']],
            [[138,143,727,140],['escaleras']],
            [[139,108,147.0,712.0,713,144,714.0, 715.0, 716.0, 717.0, 718.0,711,734.0, 736.0, 737.0, 738.0, 739.0,
                  742.0, 743.0,754,757.0, 758.0],['recreacion']],
            [[141,149,155,745.0,107.0,118,506.0,518.0,127],['espacio_abierto']],
            [[227.0,234.0, 235.0, 236.0, 237.0,239,246.0,253,403,701.0,719,755],['medico']],
            [[229,601,602.0, 603.0, 604.0, 605.0, 606.0, 607.0, 608.0],['financiero']],
            [[230.0, 512.0,514,517],['cuidado_personas']],
            [[231.0,704.0,720.0, 721.0, 722.0, 723.0,724.0,729],['escuela']],
            [[232.0,245.0,513,710,744.0,746.0],['otro']],
            [[709.0, 730.0, 731.0,740],['iglesia']],
            [[750.0, 751.0],['internet']]]
        premis=[]
        for secc in pl:
            premis+=list(zip(secc[0],secc[1]*len(secc[0])))
        premis=dict(premis)
        self.df['premis']=self.df.premis_cd.map(premis)

df=pd.read_csv("lapd.csv")
sample= df.iloc[:2000,:].copy()

test= Cleaner(sample)

test.clean()

test.imputeAge()

test.clipping()

test.lugar()

test.categoricas()

test.imputePremis()

print(test.df.sample(10))