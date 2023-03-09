import pandas as pd
import numpy as np
import csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge
from sklearn import linear_model
class Limpieza():
    def __init__(self,data):
        self.df=data
        self.df.loc[self.df.vict_age==0,'vict_age']=np.nan
        self.df.loc[(self.df.vict_age<0)|(self.df.vict_age>100),'vict_age']=np.nan
    def porcentaje(self):
        return (self.df).isna().sum()/len(self.df)*100
    def cantidad(self):
        return (self.df).isna().sum()
    def limpieza(self):
        self.df.drop('cross_street',axis=1,inplace=True)
        crm_cd_concat=self.df[['crm_cd_1','crm_cd_2','crm_cd_3','crm_cd_4']].fillna('').astype('string')
        crm_cd_concat=crm_cd_concat['crm_cd_1']+crm_cd_concat['crm_cd_2']+crm_cd_concat['crm_cd_3']+crm_cd_concat['crm_cd_4']
        self.df['crm_cd_concat']=crm_cd_concat
        self.df.drop(['crm_cd_1','crm_cd_2','crm_cd_3','crm_cd_4'],axis=1,inplace=True)
        self.df['weapon_desc'].fillna('NO WEAPON',inplace=True)
        self.df['weapon_used_cd'].fillna('0',inplace=True)
        self.df.loc[self.df.vict_sex.isna(),'vict_sex']='X'
        self.df.loc[self.df.vict_descent.isna(),'vict_descent']='U'
        self.df.loc[self.df.lon==0,['lat','lon']]=np.nan
        #return self.df
        self.df.location = self.df.location.str.strip()
        self.df.location = self.df.location.apply(lambda x: "  ".join(x.split()))
        self.df.location = self.df.location.str.replace(" ", "")
        self.df.location = self.df.location.str.upper()
        directorio = pd.read_excel('Directorio_Lat_Lon.xlsx')
        directorio.location = directorio.location.str.replace(" ", "")
        directorio.location = directorio.location.str.upper()
        loc_lat = dict(zip(directorio.location,directorio.lat))
        loc_lon = dict(zip(directorio.location,directorio.lon))
        self.df.lat.fillna(self.df.location.map(loc_lat),inplace=True)
        self.df.lon.fillna(self.df.location.map(loc_lon),inplace=True)
        self.df.drop('location',axis=1,inplace=True)
        #poner columna de código y luego descripción del código
        self.col_corr('area','area_name')
        self.col_corr('crm_cd','crm_cd_desc')
        self.col_corr('premis_cd','premis_desc')
        self.col_corr('weapon_used_cd','weapon_desc')
        self.col_corr('status','status_desc')
        self.df.loc[self.df.vict_sex=='H','vict_sex']=='X'
        self.df.drop(self.df.loc[self.df.status=='CC'].index,inplace=True)
    def imputar_edad(self):
        ucr=pd.read_csv('ucr.csv',header=None)
        ucr.columns=['Category','Subcategory','Code']
        ucr=ucr.astype({'Code':'string'})
        self.df=self.df.astype({'crm_cd':'string'})
        ucr=dict(zip(ucr['Code'],ucr['Subcategory']))
        self.df['ucr']=self.df.crm_cd.map(ucr)
        self.df.ucr=self.df.ucr.fillna('Other')
        imputar=self.df.drop(['dr_no', 'date_rptd', 'date_occ','area',
                         'rpt_dist_no','part_1_2','crm_cd','mocodes','premis_cd',
                         'weapon_used_cd','crm_cd_concat','rpt_dist_no'],axis=1).copy()
        dum1=pd.get_dummies(imputar['status']).drop('JO',axis=1)
        imputar.drop('status',axis=1,inplace=True)
        dum2=pd.get_dummies(imputar['vict_sex']).drop('X',axis=1)
        imputar.drop('vict_sex',axis=1,inplace=True)
        dum3=pd.get_dummies(imputar['vict_descent']).drop('Z',axis=1)
        imputar.drop('vict_descent',axis=1,inplace=True)
        dum4=pd.get_dummies(imputar['ucr']).drop('Other',axis=1)
        imputar.drop('ucr',axis=1,inplace=True)
        imputar=pd.concat([imputar,dum1,dum2,dum3,dum4],axis=1)
        scaler = MinMaxScaler()
        imputar=pd.DataFrame(scaler.fit_transform(imputar),columns=imputar.columns)
        X=imputar[~imputar.vict_age.isna()]
        y=X.vict_age.values
        X=X.drop('vict_age',axis=1).values
        neigh = KNeighborsRegressor(n_neighbors=5)
        neigh.fit(X, y.reshape(-1, 1))
        estimados=neigh.predict(imputar.loc[imputar.vict_age.isna(),imputar.columns!='vict_age'].values)
        estimados=[x[0] for x in estimados]
        estimados=pd.Series(index=imputar.loc[imputar.vict_age.isna(),'vict_age'].index,data=estimados)
        imputar.loc[imputar.vict_age.isna(),'vict_age']=estimados
        self.df['vict_age']=pd.DataFrame(scaler.inverse_transform(imputar),columns=imputar.columns)['vict_age']
    
    
    def imputar_edad_2(self):
        ucr=pd.read_csv('ucr.csv')
        ucr=ucr.astype({'Code':'string'})
        self.df=self.df.astype({'crm_cd':'string'})
        ucr=dict(zip(ucr['Code'],ucr['Subcategory']))
        self.df['ucr']=self.df.crm_cd.map(ucr)
        self.df.ucr=self.df.ucr.fillna('Other')
        imputar=self.df.drop(['date_rptd', 'date_occ','area',
                         'rpt_dist_no','part_1_2','crm_cd','mocodes','premis_cd',
                         'weapon_used_cd','crm_cd_concat','rpt_dist_no'],axis=1).copy()#'dr_no', 
        dum1=pd.get_dummies(imputar['status']).drop('JO',axis=1)
        imputar.drop('status',axis=1,inplace=True)
        dum2=pd.get_dummies(imputar['vict_sex']).drop('X',axis=1)
        imputar.drop('vict_sex',axis=1,inplace=True)
        dum3=pd.get_dummies(imputar['vict_descent']).drop('Z',axis=1)
        imputar.drop('vict_descent',axis=1,inplace=True)
        dum4=pd.get_dummies(imputar['ucr']).drop('Other',axis=1)
        imputar.drop('ucr',axis=1,inplace=True)
        imputar=pd.concat([imputar,dum1,dum2,dum3,dum4],axis=1)
        
        
        X=imputar[~imputar.vict_age.isna()]
        y=X.vict_age.values
        X=X.drop('vict_age',axis=1).values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        sc_X = MinMaxScaler()
        sc_y = MinMaxScaler()
        X_train=sc_X.fit_transform(X_train)
        y_train=sc_y.fit_transform(y_train.reshape(-1, 1))
        y_test=sc_y.transform(y_test.reshape(-1,1))
        X_test=sc_X.transform(X_test)
        
        clf = Ridge(alpha=1.0)
        clf.fit(X_train, y_train)
        y_train_p=clf.predict(X_train)
        #scores = cross_val_score(clf, X_train, y_train, cv=5)
        #y_train_p=scores.score(X_train)
        #print(r2_score(y_train, y_train_p))
        
        y_test_p=clf.predict(X_test)
        print(r2_score(y_test, y_test_p))
        
        print(mean_squared_error(y_train, y_train_p))
        print(mean_squared_error(y_test, y_test_p))
        
        
        
    def imputar_premis(self):
        self.df=self.df.astype({'premis_cd':'string'})
        imputar=self.df.drop([ 'date_rptd', 'date_occ','area',
                         'rpt_dist_no','part_1_2','crm_cd','mocodes',
                         'weapon_used_cd','crm_cd_concat','rpt_dist_no'],axis=1).copy()#'dr_no',
        dum1=pd.get_dummies(imputar['status']).drop('JO',axis=1)
        imputar.drop('status',axis=1,inplace=True)
        dum2=pd.get_dummies(imputar['vict_sex']).drop('X',axis=1)
        imputar.drop('vict_sex',axis=1,inplace=True)
        dum3=pd.get_dummies(imputar['vict_descent']).drop('Z',axis=1)
        imputar.drop('vict_descent',axis=1,inplace=True)
        dum4=pd.get_dummies(imputar['ucr']).drop('Other',axis=1)
        imputar.drop('ucr',axis=1,inplace=True)
        imputar=pd.concat([imputar,dum1,dum2,dum3,dum4],axis=1)
        
        sc_x = MinMaxScaler()
        X=imputar.loc[~self.df.premis_cd.isna(),imputar.columns!='premis_cd']
        y=imputar.loc[~self.df.premis_cd.isna(),'premis_cd']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        X_train=pd.DataFrame(sc_x.fit_transform(X_train),columns=X.columns)
        X_test=pd.DataFrame(sc_x.transform(X_test),columns=X.columns)
        
        
        
        
        neigh = KNeighborsClassifier(n_neighbors=4)
        neigh.fit(X_train,y_train)
        y_predict=neigh.predict(X_test)
        return accuracy_score(y_test, y_predict)
        
        
        #estimados=neigh.predict(imputar.loc[imputar.premis_cd.isna(),imputar.columns!='premis_cd'].values)
        
        #estimados=pd.Series(index=imputar.loc[imputar.premis_cd.isna(),'premis_cd'].index,data=estimados)
        #self.df.loc[imputar.premis_cd.isna(),'premis_cd']=estimados
        #self.df['premis_cd']=pd.DataFrame(scaler.inverse_transform(imputar.drop('premis_cd')),columns=imputar.columns)['premis_cd']
    
    def imputar_mocodes(self):
        imputar=self.df.drop([ 'date_rptd', 'date_occ','area',
                         'rpt_dist_no','part_1_2','crm_cd','premis_cd',
                         'weapon_used_cd','crm_cd_concat','rpt_dist_no'],axis=1).copy()#'dr_no',
        dum1=pd.get_dummies(imputar['status']).drop('JO',axis=1)
        imputar.drop('status',axis=1,inplace=True)
        dum2=pd.get_dummies(imputar['vict_sex']).drop('X',axis=1)
        imputar.drop('vict_sex',axis=1,inplace=True)
        dum3=pd.get_dummies(imputar['vict_descent']).drop('Z',axis=1)
        imputar.drop('vict_descent',axis=1,inplace=True)
        dum4=pd.get_dummies(imputar['ucr']).drop('Other',axis=1)
        imputar.drop('ucr',axis=1,inplace=True)
        imputar=pd.concat([imputar,dum1,dum2,dum3,dum4],axis=1)
        
        scaler = MinMaxScaler()
        
        
        
        sc_x = MinMaxScaler()
        X=imputar.loc[~imputar.mocodes.isna(),imputar.columns!='mocodes']
        y=imputar.loc[~imputar.mocodes.isna(),'mocodes']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        X_train=pd.DataFrame(sc_x.fit_transform(X_train),columns=X.columns)
        
        
        
        
        
        neigh = KNeighborsClassifier(n_neighbors=3, scoring='r2')
        neigh.fit(X_train,y_train)
        y_predict=neigh.predict(X_test)
        print(accuracy_score(y_test, y_predict))
        
        
       
    def col_corr(self,codigo,descripcion):
        dicc=dict(zip(self.df[codigo],self.df[descripcion]))
        w = csv.writer(open(codigo+".csv", "w"))
        for key, val in dicc.items():
            w.writerow([key, val])
        self.df.drop(descripcion,axis=1,inplace=True)
        
    def actualizar(self):
        return self.df
    def categoricas(self):
        features=['rpt_dist_no','premis_cd','weapon_used_cd']
        for feature in features:
            aux = self.df[feature].value_counts(True)
            ls_categories = [category for category, freq in aux.items() if freq > 0.03]
            self.df[feature] = self.df[feature].map(lambda x: x if x in ls_categories else "Others")