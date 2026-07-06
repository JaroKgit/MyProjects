import pandas as pd
import matplotlib.pyplot as plt   
import numpy as np
import scipy.stats as stats
import warnings  
from scipy.stats import chi2_contingency, fisher_exact
import os  

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
'''
df_tomb_status.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\tomb_status.csv", index=False)
print("df_tomb_status DONE")
features_antropo.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\features_antropo.csv", index=False)
print("features_antropo DONE")
for key, df in features_data.items():
    df.to_excel(rf"G:\Edu\FJFI ČVUT\bakalarka\first_research\{key}.xlsx", index=False)
print("features_data DONE")
df_feature_specs.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\df_feature_specs.csv", index=False)
print("df_feature_specs DONE")
'''
###########################
###########################
###########################
###########################
########################### Next function will look into all vertebre data and 
########################### it will count how many vertebre damage of each type
########################### there are. Tedy kolik kostí má jaký typ poškození

def vertabre_damage(df_feature_specs):
    vertebrae = df_feature_specs[df_feature_specs['group'] == 'vertebrae']
    vertebrae_idd = vertebrae[vertebrae['changes'] == 'IDD']
    vertebrae_ec=vertebrae[vertebrae['changes'] == 'EC']
    vertebrae_oa=vertebrae[vertebrae['changes'] == 'OA']
    vertebrae_sn=vertebrae[vertebrae['changes'] == 'SN']
    vertebrae_ma_p=vertebrae[vertebrae['changes'] == 'MA-P']

    count_idd=len(vertebrae_idd)
    count_ec=len(vertebrae_ec)
    count_oa=len(vertebrae_oa)
    count_sn=len(vertebrae_sn)
    count_ma_p=len(vertebrae_ma_p)

    file_path = os.path.join(r"\Edu\FJFI ČVUT\bakalarka\first_research\vertebre_idd_oa_sn_etc.png")

    plt.figure(figsize=(6,6))
    plt.pie(
        [count_idd,count_ec, count_ma_p,count_oa,count_sn],
        labels=["IDD","EC","MA-P","OA","SN"],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'weight':'bold', 'fontsize':12}
    )
    plt.title("Vertabre damages")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    return 

"vertebre_damage_call=vertabre_damage(df_feature_specs)"
########################### Next funtion will simply look
########################### into how many bones have IDD
########################### And how many doesn't have idd, tedypoměr těch IDD/zbytek

def ratio_vertabrae_idd_and_without(df_feature_specs):
    vertebrae = df_feature_specs[df_feature_specs['group'] == 'vertebrae']
    vertebrae_idd = vertebrae[vertebrae['changes'] == 'IDD']

    count_with_idd = len(vertebrae_idd)
    count_no_idd= len(vertebrae) - count_with_idd
    
    # Cesta k souboru
    file_path = os.path.join(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\idd_no_idd")
    
    # Pie chart
    plt.figure(figsize=(6,6))
    plt.pie(
        [count_no_idd, count_with_idd], 
        labels=['without IDD', 'with IDD'], 
        autopct='%1.1f%%', 
        startangle=90,
        textprops={'weight':'bold', 'fontsize':12}
    )
    plt.title("Distribution of individuals by " \
    "vertebral IDD damage and no IDD damage")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    
"ratio_vertabrae_idd_and_without_call=ratio_vertabrae_idd_and_without(df_feature_specs)"

###########################
###########################
########################### pomocná funkce chí default pro signifikantní data

def test_categorical_dependency(df, feature_col, category_col):
    # Odstranit NaN
    df_sub = df[[feature_col, category_col]].dropna()
    # Kontingenční tabulka
    contingency = pd.crosstab(df_sub[feature_col], df_sub[category_col])
    
    # Pokud 2x2 a některá buňka <5 → Fisherův exact test
    if contingency.shape == (2,2) and (contingency.values < 5).any():
        _, p_value = stats.fisher_exact(contingency)
    else:
        _, p_value, _, _ = stats.chi2_contingency(contingency)
    
    return p_value

def my_chi_function(data, column_feature, category_name):
    data[column_feature] = data[column_feature].fillna(0)
    filter_out_nan=data[[column_feature,category_name]].dropna()
    '''filter_out_nan[[column_feature, category_name]] = filter_out_nan[[column_feature, category_name]].fillna(0)'''
    '''filter_out_nan.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\filter_out_nan_5.csv", index=False)'''
    contingency_tabel=pd.crosstab(filter_out_nan[column_feature], filter_out_nan[category_name])
    '''contingency_tabel.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\contingency_tabel_my_chi_function_pokus_bez_dropna.csv", index=False)'''
    observed=contingency_tabel.values
    '''print(contingency_tabel)'''
    row_sum = observed.sum(axis=1).reshape(-1,1)  # součet každého řádku
    col_sum = observed.sum(axis=0).reshape(1,-1)  # součet každého sloupce
    total_sum = observed.sum()                          # celkový součet
    '''print(f"observed:{observed}, row_sum:{row_sum}, col_sum:{col_sum},total_sum:{total_sum}")'''
    
    expected = row_sum @ col_sum / total_sum

    chi2_stat = ((observed - expected) ** 2 / expected).sum()
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    '''print(f"expected:{expected},chi2_stat:{chi2_stat},degrees of freedom: {dof}")'''

    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(chi2_stat, dof)

    return p_value 

def my_fishers_method(data, column_feature, category_name):
    from scipy.stats import fisher_exact

    data[column_feature] = data[column_feature].fillna(0)
    filter_out_nan = data[[column_feature, category_name]].dropna()
    contingency_table = pd.crosstab(filter_out_nan[column_feature], 
                                    filter_out_nan[category_name])
    df_contingency_table = pd.DataFrame(contingency_table)

    output_folder = r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fishers"

    output_folder = r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fishers"
    table_path = f"{output_folder}\\contingency_{column_feature}_vs_{category_name}.csv"

    df_contingency_table.to_csv(table_path)
    print(f"Kontingenční tabulka uložena do: {table_path}")
    # Fisher pracuje jen pro 2x2 tabulku
    if contingency_table.shape == (2, 2):
        _, p_value = fisher_exact(contingency_table) ### Protože výsledek funkce je n-tice, _ je placeholder (výsledek tohoto nás nezajímá), je to odds_ratio (odhad poměru šancí mezi kategoriemi)
        return p_value
    else:
        return None
'''
Odds ratio OR=a*d/b*c, OR=1 není žádná asociace, OR<1 šance že data spolu mají něco společného je malá, OR>1 šance ža data spolu něco mají je velká
'''
    
###########################
###########################
########################### signifikantní data, chí funkce

def significant_data_fisher(df_feature_specs):
    
    features_to_test = df_feature_specs[
        (df_feature_specs['group'] == 'vertebrae') &
        (df_feature_specs['changes'] == 'IDD')
    ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Looking for Significant data (Fisher exact).")

    results_fisher = []

    for feature in features_to_test:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)

        # binarizace
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce')
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace([2,3,4], 1)

        # Fisher
        p_sex_fisher = my_fishers_method(req_feature_data, 'feature_bin', 'sex')
        p_age_fisher = my_fishers_method(req_feature_data, 'feature_bin', 'age_group')

        results_fisher.append({
            'feature': feature,
            'p_sex_fisher': p_sex_fisher,
            'p_age_fisher': p_age_fisher,
            'significant_sex_fisher': p_sex_fisher is not None and p_sex_fisher < 0.05,
            'significant_age_fisher': p_age_fisher is not None and p_age_fisher < 0.05
        })

    df_results = pd.DataFrame(results_fisher)

    output_folder = r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fishers"
    all_csv_path = f"{output_folder}\\vertebrae_IDD_results_fisher.csv"

    df_results.to_csv(all_csv_path, index=False)
    print(f"Výsledky Fisher exact testu uloženy do: {all_csv_path}")

significant_data_fisher_call=significant_data_fisher(df_feature_specs)

def significant_data(df_feature_specs):

    features_to_test = df_feature_specs[
        (df_feature_specs['group'] == 'vertebrae') &
        (df_feature_specs['changes'] == 'IDD')
    ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Looking for Significant data")

    results = []

    for feature in features_to_test:
        # Získání dat pro feature
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        '''req_feature_data.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\req_feature_data_from_get_feature_data_1.csv", index=False)'''
        # Převod na binární 0/1
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce')
        '''req_feature_data.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\req_feature_data2.csv", index=False)'''
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace(2, 1)
        '''req_feature_data.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\req_feature_data3.csv", index=False)'''
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace(3, 1)
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace(4, 1)
        '''req_feature_data.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\req_feature_data_final_that_we_submit_to_my_chi_function.csv", index=False)'''
        # Test vs pohlaví
        p_sex = my_chi_function(req_feature_data, 'feature_bin', 'sex')
        # Test vs věk
        p_age = my_chi_function(req_feature_data, 'feature_bin', 'age_group')
        
        results.append({
            'feature': feature,
            'p_sex': p_sex,
            'signif_sex': p_sex < 0.05,
            'p_age': p_age,
            'signif_age': p_age < 0.05
        })

    # Převod výsledků na DataFrame a export přehledně
    df_results = pd.DataFrame(results)

    # Přejmenování sloupců pro lepší čitelnost
    df_results = df_results.rename(columns={
        'p_sex': 'p_value_sex',
        'signif_sex': 'significant_sex',
        'p_age': 'p_value_age',
        'signif_age': 'significant_age'
    })

    # Seřadíme podle signifikantnosti (nejprve ty, které jsou signifikantní)
    df_results = df_results.sort_values(['significant_sex', 'significant_age'], ascending=False)

    output_folder = r"G:\Edu\FJFI ČVUT\bakalarka\first_research"

    # Všechny výsledky
    all_csv_path = f"{output_folder}\\vertebrae_IDD_results_all.csv"
    df_results.to_csv(all_csv_path, index=False)
    print(f"Všechny výsledky uloženy do: {all_csv_path}")

    # Pouze signifikantní feature
    df_significant = df_results[(df_results['significant_sex']) | (df_results['significant_age'])]
    signif_csv_path = f"{output_folder}\\vertebrae_IDD_results_significant.csv"
    df_significant.to_csv(signif_csv_path, index=False)
    print(f"Pouze signifikantní výsledky uloženy do: {signif_csv_path}")

    interaction_results = []

    for feature in df_significant['feature']:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        '''req_feature_data['feature_bin'] = req_feature_data['feature_bin'].fillna(0)'''
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce').replace(2,1)
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace(3, 1)
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].replace(4, 1)
        req_feature_data['feature_bin'] = req_feature_data['feature_bin'].fillna(0)
        '''req_feature_data.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\all_with_my_chi_function\significant_data1.csv", index=False)'''
        df_model = req_feature_data.dropna(subset=['sex', 'age_group'])
        '''df_model.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\all_with_my_chi_function\significant_data2.csv", index=False)'''
        df_model['sex_age'] = df_model['sex'].astype(str) + '_' + df_model['age_group'].astype(str)
        '''df_model.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\all_with_my_chi_function\significant_data3.csv", index=False)'''
        contingency = pd.crosstab(df_model['feature_bin'], df_model['sex_age'])
        '''contingency.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\all_with_my_chi_function\significant_data4.csv", index=False)'''
        p_value = my_chi_function(df_model, 'feature_bin', 'sex_age')
        '''_, p_value, _, _ = chi2_contingency(contingency)'''
        interaction_results.append({'feature': feature, 'p_interaction_sex_age': p_value})

    df_interaction = pd.DataFrame(interaction_results)
    df_interaction.to_csv(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\all_with_my_chi_function\significant_data_interactions.csv", index=False)
    print("Interakce uloženy do CSV.")

"significant_data_call=significant_data(df_feature_specs)"

########################### Next function will determine which age categories (IMM/YA/OA/MA)
########################### and how many people from this category
########################### have IDD defect. Then it will make a graph

def graphs_des_dates_age_unique(df_feature_specs):

    all_idd_ids = [] 

    features_to_test = df_feature_specs[
            (df_feature_specs['group'] == 'vertebrae') &
            (df_feature_specs['changes'] == 'IDD')
        ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Making a statistics and graph for age unique")

    for feature in features_to_test:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        # Jen vertebrae, kde je IDD přítomno (feature_bin = 1)
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce').replace(2,1)
        idd_rows = req_feature_data[req_feature_data['feature_bin'] == 1]
        all_idd_ids.extend(idd_rows['mainID'].tolist())

    df_idd_age = df_tomb_status[df_tomb_status['mainID'].isin(all_idd_ids)]

    # Odstranit duplicitní jedince
    df_idd_age_unique = df_idd_age.drop_duplicates(subset='mainID')

    # Spočítat věkové rozložení
    age_counts_unique = df_idd_age_unique['age_group'].value_counts(dropna=False)
    print("Age disproportion of people with vertabre IDD")
    print(age_counts_unique)
### graf
    file_path=os.path.join(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fig_age_unique")

    explode = [0.1 if x < 5 else 0 for x in age_counts_unique]
    plt.figure(figsize=(6,6))
    plt.pie(age_counts_unique, 
            labels=age_counts_unique.index, 
            autopct='%1.1f%%', 
            startangle=90,
            explode=explode,
            ###pctdistance=0.8,
            ###labeldistance=1.1,
            textprops={'weight':'bold', 'fontsize':12}
            )
    plt.title("Age disproportion of people with IDD vertabre damage")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    "plt.show()"

"graphs_des_dates_age_call=graphs_des_dates_age_unique(df_feature_specs)"

########################### tady se snažím vyfiltrovat že třeba jeden člověk má víc kostí vertabrae s idd, tak aby to bylo jenom 
########################### od jednoho člověka ale když o tom přemýšlím, tak je to statistika nic neříkající. a navíc si myslím že nefunguje
########################### NEFUNČKČNÍ NEBO NEJSOU DUPLUCITY!!!

def graphs_des_dates_age(df_feature_specs):

    all_idd_ids = []  # seznam mainID pro všechny vertebrae s IDD

    features_to_test = df_feature_specs[
            (df_feature_specs['group'] == 'vertebrae') &
            (df_feature_specs['changes'] == 'IDD')
        ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Making a statistics and graph for age ")

    for feature in features_to_test:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        # Jen vertebrae, kde je IDD přítomno (feature_bin = 1)
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce').replace(2,1)
        idd_rows = req_feature_data[req_feature_data['feature_bin'] == 1]
        all_idd_ids.extend(idd_rows['mainID'].tolist())

    df_idd_age = df_tomb_status[df_tomb_status['mainID'].isin(all_idd_ids)]

    # Spočítat věkové rozložení
    age_counts_unique = df_idd_age['age_group'].value_counts(dropna=False)
    print("Věkové rozložení kostí nezávisle na lidech s IDD vertebrae:")
    print(age_counts_unique)
### graf
    file_path=os.path.join(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fig_age")

    plt.figure(figsize=(6,6))
    plt.pie(age_counts_unique, 
            labels=age_counts_unique.index, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'weight':'bold', 'fontsize':12}
            )
    plt.title("Věkové rozložení kostí nezávisle na lidech s IDD vertebrae")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    "plt.show()"

'''graphs_des_dates_age_call=graphs_des_dates_age(df_feature_specs)'''

########################### In the next function I try to find out
########################### in which tombs are vertabre with IDD
########################### so basicly it is percentage of (vertabre IDD in main tomb)/(vertabre IDD in subsidiary tomb)

def stats_graphs_des_tombes_unique(df_feature_specs):
    features_to_test = df_feature_specs[
        (df_feature_specs['group'] == 'vertebrae') &
        (df_feature_specs['changes'] == 'IDD')
    ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Making Stats for tombs unique")

    all_idd_ids = []  

    for feature in features_to_test:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        # Jen vertebrae, kde je IDD přítomno (feature_bin = 1)
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce').replace(2,1)
        idd_rows = req_feature_data[req_feature_data['feature_bin'] == 1]
        all_idd_ids.extend(idd_rows['mainID'].tolist())

    df_idd_tombs = df_tomb_status[df_tomb_status['mainID'].isin(all_idd_ids)]

    # Odstranit duplicitní jedince
    df_idd_tombs_unique = df_idd_tombs.drop_duplicates(subset='mainID')

### Rozložení podle typu hrobky
    tomb_counts = df_idd_tombs_unique['tomb_status'].value_counts(dropna=False)
    print("Rozložení lidí s IDD vertebrae podle typu hrobky:")
    print(tomb_counts)

### graph
    file_path=os.path.join(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fig_tomb_unique")

    plt.figure(figsize=(6,6))
    plt.pie(tomb_counts, 
            labels=tomb_counts.index, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'weight':'bold', 'fontsize':12}
            )
    plt.title("Distribution of individuals with IDD by tombs")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    "plt.show()"

"stats_graphs_des_tombes_call=stats_graphs_des_tombes_unique(df_feature_specs)"

########################### tady se snažím vyfiltrovat že třeba jeden člověk má víc kostí vertabrae s idd, tak aby to bylo jenom 
########################### od jednoho člověka ale když o tom přemýšlím, tak je to statistika nic neříkající. a navíc si myslím že nefunguje
########################### 

def stats_graphs_des_tombes(df_feature_specs):
    features_to_test = df_feature_specs[
        (df_feature_specs['group'] == 'vertebrae') &
        (df_feature_specs['changes'] == 'IDD')
    ]['feature'].tolist()

    print(f"Analyzujeme {len(features_to_test)} vertebrae/IDD feature. Making Stats for tombs")

    all_idd_ids = []  # seznam mainID pro všechny vertebrae s IDD

    for feature in features_to_test:
        req_feature_data = get_feature_data(features_data, features_antropo, df_tomb_status, feature)
        # Jen vertebrae, kde je IDD přítomno (feature_bin = 1)
        req_feature_data['feature_bin'] = pd.to_numeric(req_feature_data['feature'], errors='coerce').replace(2,1)
        idd_rows = req_feature_data[req_feature_data['feature_bin'] == 1]
        all_idd_ids.extend(idd_rows['mainID'].tolist())

    df_idd_tombs = df_tomb_status[df_tomb_status['mainID'].isin(all_idd_ids)]

### Rozložení podle typu hrobky
    tomb_counts = df_idd_tombs['tomb_status'].value_counts(dropna=False)
    print("Rozložení kostí nezávisle na lidech s IDD vertebrae podle typu hrobky:")
    print(tomb_counts)

### graph
    file_path=os.path.join(r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fig_tomb")

    plt.figure(figsize=(6,6))
    plt.pie(tomb_counts, 
            labels=tomb_counts.index, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'weight':'bold', 'fontsize':12}
            )
    plt.title("Rozložení kostí nezávisle na lidech s IDD vertebrae podle typu hrobky")
    plt.savefig(file_path, dpi=300, bbox_inches='tight')
    "plt.show()"

'''stats_graphs_des_tombes_call=stats_graphs_des_tombes(df_feature_specs)'''


