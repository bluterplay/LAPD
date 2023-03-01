import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.plotting import table 

class Discrete():
    def __init__ (self, df):
        self.df = df
        self.discrete = ["area_name", "crm_cd_desc", "vict_sex", "weapon_desc", "premis_desc"]

    def pie_chart(self):
        palette_color = sns.color_palette('pastel')
        for tag in self.discrete:
            plt.clf()
            area = self.df.groupby([tag])[tag].count()[:5]
            plt.pie(area,labels=area.index, colors=palette_color, autopct='%.0f%%')
            plt.savefig(f'../Graphs/pie_{tag}.png',  bbox_inches='tight')

    def freq_table(self):
        palette_color = sns.color_palette('pastel')

        for tag in self.discrete:
            plt.clf()
            ax = plt.subplot()
            # print(pd.DataFrame(self.df[tag].value_counts())[:5])
            ax.xaxis.set_visible(False)  # hide the x axis
            ax.yaxis.set_visible(False) 
            table(ax, pd.DataFrame(self.df[tag].value_counts())[:5])  
            plt.savefig(f'../Graphs/table_{tag}.png')

    def bar_chart(self):
        palette_color = sns.color_palette('pastel')

        for tag in self.discrete:
            plt.clf()
            sns.countplot(x=self.df[tag])
            plt.savefig(f'../Graphs/barchart_{tag}.png')

    def time_series(self):
        palette_color = sns.color_palette('pastel')

        time_series = self.df.groupby(["date_rptd"])["crm_cd_desc"].count()

        plt.clf()
        sns.lineplot(x=time_series.index, y=time_series.values, data=time_series)
        plt.savefig('../Graphs/timeseries.png')





if __name__ == "__main__":
    df = pd.read_csv("../lapd.csv")


    gen = Discrete(df)
    gen.pie_chart()
    
    gen.freq_table()
    plt.clf()
    gen.bar_chart()
    plt.clf()
    gen.time_series()