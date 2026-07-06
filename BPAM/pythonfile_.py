import pandas as pd
import numpy as np
import warnings  
import statsmodels.api as sm
from patsy import dmatrices

'''
Libraries
pandas - reads documents and data; matplotlib - makes graphs; numpy - matematic; warnings - destroys pandas announcments, os - finding way for graphs in my storage
'''

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_tomb_bones_data(): ###PŘIPRAVÍ MI TO DATAFRAME
    
    features_data = {'df_dc':       pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_04_export_tomb_DC.xlsx","Sheet1"),
                     'df_ec':       pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_04_export_tomb_EC_NMT.xlsx","Sheet1"),
                     'df_metric':   pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_04_export_tomb_metric.xlsx","Sheet1"),
                     'df_vert':     pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_04_export_tomb_vertebrae.xlsx","Sheet1"),
                     'df_pat':      pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_12_export_patologie.xlsx","Sheet1")}
    
    # Add ?temporal age_group file
    df_age = pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_04_export_age_grouping.xlsx","Sheet1")
    
    # Add ?temporal feature speciffication file 
    df_feature_specs = pd.read_excel(r"G:\Edu\FJFI ČVUT\bakalarka\data\2025_06_12_feature_specification.xlsx","all")

    df_tomb_status = df_age.copy()

    # Standardization of column names
    for key in features_data.keys():
        features_data[key].rename(columns = {'grave number': 'grave_number'}, inplace = True)
    df_tomb_status.rename(columns = {'grave number': 'grave_number'}, inplace = True)
    
    # Standardization of tomb_status
    df_tomb_status['tomb_status'] = df_tomb_status['tomb_status'].replace(['main'], 'm')
    df_tomb_status['tomb_status'] = df_tomb_status['tomb_status'].replace(['subsidiary'], 's')
    df_tomb_status['tomb_status'] = df_tomb_status['tomb_status'].replace(['location not yet identified'], np.nan)

    # Standardization of sex
    df_tomb_status['sex'] = df_tomb_status['sex'].replace(['M', 'M?', 'Mann', 'Mann ?'], 'm')
    df_tomb_status['sex'] = df_tomb_status['sex'].replace(['F', 'F?', 'Frau', 'Female', 'Frau ?'], 'f')
    df_tomb_status['sex'] = df_tomb_status['sex'].replace(['?(M?)', 'NEZPRACOVÁNO', 'U', 'XX', 'Kind'], np.nan)

    # Standardization of features
    features_data['df_ec'].EC_UTB_L.replace(['Bs'], 2, inplace = True)
    features_data['df_ec'].EC_UTB_R.replace(['Bs'], 2, inplace = True)
    for key in features_data.keys():
        features_data[key].replace(['ABS','NR','\n'], np.nan, inplace = True)


    return features_data, df_tomb_status, df_feature_specs

def analyze_antropo_features(features_data, df_tomb_status): ###PŘIPRAVÍ MI TO DATAFRAME

    # Get list of features
    descriptive_features = df_tomb_status.columns
    descriptive_features = descriptive_features.tolist() + ['Old_Kingdom']     # also descriptive, but missing in status file 2025-06-06
    
    features_antropo = pd.DataFrame()
    for key in features_data.keys():
        features_add = pd.Index(features_data[key].columns, name = 'feature') 
        features_add = features_add.to_frame(index = False)
        features_add['file'] = key
        features_add = features_add[~features_add.feature.isin(descriptive_features)]
        features_antropo = pd.concat([features_antropo, features_add])
    features_antropo.reset_index(inplace=True, drop=True)
    
    # Analyze features - number, of observations, number of levels, ...
    features_antropo['n_obs'] = np.nan
    features_antropo['n_cat'] = np.nan
    features_antropo['val_list'] = [[] for _ in range(len(features_antropo))]
    features_antropo['val_cnts'] = [[] for _ in range(len(features_antropo))]
    for i in range(len(features_antropo)):
        req_feature_name = features_antropo.feature[i]
        feature_file = features_antropo.file[i]
        feature_data = features_data[feature_file][['mainID', req_feature_name]].copy()
        feature_data = feature_data[feature_data[req_feature_name].isnull() == False]
        feature_hist = feature_data.groupby(req_feature_name).size().reset_index(name='g_count')   
        features_antropo.loc[i, 'n_obs'] = len(feature_data)
        features_antropo.loc[i, 'n_cat'] = len(feature_hist)
        if len(feature_data) > 0:
            features_antropo.loc[i, 'min_cat_obs'] = min(feature_hist.g_count)
        else:
            features_antropo.loc[i, 'min_cat_obs'] = 0
        features_antropo.at[i, 'val_list'] = feature_hist[req_feature_name].tolist()
        features_antropo.at[i, 'val_cnts'] = feature_hist.g_count.tolist()

    return features_antropo

def get_feature_data(features_data, features_antropo, df_tomb_status, req_feature_name): ###PŘIPRAVÍ MI TO DATAFRAME
    
    feature_file = features_antropo.file[features_antropo.feature == req_feature_name].values[0]  
    req_feature_data = features_data[feature_file][['mainID', req_feature_name]].copy()
    req_feature_data.rename(columns = {req_feature_name: 'feature'}, inplace = True)

    req_feature_data = pd.merge(df_tomb_status[['mainID' ,'tomb_status', 'sex', 'age_group', 'locality']], req_feature_data,
                                                  how = 'left',  on = 'mainID') 

    req_feature_data['feature'] = req_feature_data['feature'].astype(str)
    req_feature_data['feature'] = req_feature_data['feature'].replace(['nan'], np.nan)
    
    req_feature_data = req_feature_data[req_feature_data.tomb_status.isna() == False]

    return req_feature_data

features_data, df_tomb_status, df_feature_specs = get_tomb_bones_data()
df_tomb_status.rename(columns = {'age_cat_CORR': 'age_group'}, inplace = True)
df_tomb_status['age_group'] = df_tomb_status['age_group'].replace('A', np.nan)
features_antropo = analyze_antropo_features(features_data, df_tomb_status)

###########################
###########################
########################### CUBIOD

df_cuboid = df_tomb_status.dropna(subset=['age_group', 'sex', 'tomb_status'])

cuboid = df_cuboid.groupby(['age_group', 'sex', 'tomb_status']).size().unstack(fill_value=0)

print("Cuboid (count of tombs by age_group × sex × tomb_status):")
print(cuboid)
cuboid.to_excel(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\loglinear+Utest\cuboid.xlsx")

# Převod na long form
df_long = cuboid.reset_index().melt(id_vars=['age_group','sex'], value_vars=['m','s'],
                                    var_name='tomb_status', value_name='count')

df_long = df_long[df_long['count'] > 0]
y, X = dmatrices('count ~ age_group*sex*tomb_status', data=df_long, return_type='dataframe')

# Fit Poisson GLM
model = sm.GLM(y, X, family=sm.families.Poisson()).fit()

glm_results = pd.DataFrame({
    'coef': model.params,
    'std_err': model.bse,
    'z_value': model.tvalues,
    'p_value': model.pvalues,
    'conf_lower': model.conf_int()[0],
    'conf_upper': model.conf_int()[1]
})

glm_results.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\loglinear+Utest\glm_results.csv", index=True)
print(model.summary())
