import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class Discrete():
    def __init__ (self, df):
        self.df = df
        self.discrete = ["area_name", "crm_cd_desc", "vict_sex", "weapon_desc", "premis_desc"]

    def pie_chart(self):
        palette_color = sns.color_palette('pastel')
        for tag in self.discrete:
            area = self.df.groupby([tag])[tag].count()[:5]
            plt.pie(area,labels=area.index, colors=palette_color, autopct='%.0f%%')

    def freq_table(self):
        palette_color = sns.color_palette('pastel')

        for tag in self.discrete:
            print(pd.DataFrame(self.df[tag].value_counts())[:5])

    def bar_chart(self):
        palette_color = sns.color_palette('pastel')

        for tag in self.discrete:
            sns.countplot(x=self.df[tag])


    def time_series(self):
        palette_color = sns.color_palette('pastel')

        time_series = self.df.groupby(["date_rptd"])["crm_cd_desc"].count()


        sns.lineplot(x=time_series.index, y=time_series.values, data=time_series)





if __name__ == "__main__":
    df = pd.read_csv("./lapd.csv")


    gen = Discrete(df)
    gen.pie_chart()
    gen.freq_table()
    gen.bar_chart()
    gen.time_series()