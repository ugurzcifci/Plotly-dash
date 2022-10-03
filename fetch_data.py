import pandas as pd

def __fetch_healthcare_organizations() -> pd.DataFrame:
    filename_healthcare = "datasets/salk-kurum-ve-kurulularna-ait-bilgiler.csv"
    file = open(filename_healthcare, 'r', encoding="ISO-8859-1")
    df_healthcare = pd.read_csv(file)
    return df_healthcare


def __fetch_SES_scores() -> pd.DataFrame:
    df_ses = pd.read_excel(r"datasets/2016-yl-mahallem-istanbul-ses-skorlar.xlsx")
    return df_ses

def __prepare_healthcare_data(df_healthcare) -> pd.DataFrame:
    df_saglik = df_healthcare
    df_saglik_object_columns = df_saglik.dtypes[df_saglik.dtypes == "object"]

    # Dealing with special characters
    for i in df_saglik_object_columns.index.values:
        df_saglik[i] = df_saglik[i].str.replace("ð", "ğ")
        df_saglik[i] = df_saglik[i].str.replace("ý", "ı")
        df_saglik[i] = df_saglik[i].str.replace("þ", "ş")
        df_saglik[i] = df_saglik[i].str.replace("Ý", "İ")
        df_saglik[i] = df_saglik[i].str.replace("Þ", "Ş")
        df_saglik[i] = df_saglik[i].str.replace("Ð", "Ğ")

    # Filling one missing value row & dropping unwanted columns
    df_saglik['ILCE_ADI'].iloc[3936] = 'KARTAL'
    df_saglik.drop(['ILCE_UAVT', 'ADRES', 'TELEFON', 'WEBSITESI'], axis=1, inplace=True)
    return df_saglik


class DerivedData:
    def __init__(self, df_healthcare, df_ses):
        self.df_merged = pd.merge(df_healthcare, df_ses, left_on=["ILCE_ADI", "MAHALLE"],
                             right_on=['İLÇE ADI', 'MAHALLE ADI'])

    def district_based_dataframes(self):
        # District based dataframes
        district_mean_ses = self.df_merged.groupby(['ILCE_ADI']).mean()
        district_sum_of_healthcare = self.df_merged.groupby(['ILCE_ADI']).count()['SES']
        district_healthcare_category = self.df_merged.groupby(['ILCE_ADI', 'ALT_KATEGORI']).count()
        return district_mean_ses, district_sum_of_healthcare, district_healthcare_category

    def nh_based_dataframes(self):
        # Neighborhood based dataframes
        nh_sum_of_healthcare = self.df_merged.groupby(['ILCE_ADI', 'MAHALLE']).count()['SES']
        nh_healthcare_category = self.df_merged.groupby(['ILCE_ADI', 'MAHALLE', 'ALT_KATEGORI']).count()
        return nh_sum_of_healthcare, nh_healthcare_category
