

!pip install sdv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split

import sdv
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import SingleTableMetadata

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

"""### Adjusting range of df viewing
- Show all rows and columns
- Show only 10 rows and columns


"""

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# pd.set_option('display.max_columns', 10)
# pd.set_option('display.max_rows', 10)

"""### Importing data"""

df = pd.read_csv('../../data/processed/[V2] Survey_cleaned_imbalanced.csv')

"""### Synthesising data
1. EDA
2. SVD
3. SMOTE

**Remove open-ended questions**

We first make copy of the cleaned data frame (df) to perform the data synthesis, before removing the columns with open-ended questions (i.e. 'Suggestions for improving USS experience' and 'Suggestions for improving USS website') as these are the only two columns that have non-integer entries. We also remove the unique index identifier (Survey_ID) as it affects the data synthesis.
- These columns and datapoints will be added back once the synthetic data is produced.
"""

# remove unique identifier (Survey_ID) and open-ended questions (col1, col2) -> add back after smote/oversampling methods are completed
df2 = df.copy()

# splicing segments of dataframe; col1 = uss experience, col2 = uss website
uss_exp_inx, uss_web_idx = df.columns.get_loc('Suggestions for improving USS experience'), df.columns.get_loc('Suggestions for improving USS website') # (151, 171)
df2_bef_col1 = df.iloc[:, 1:uss_exp_inx] # skip Survey_ID column this time
df2_btw_col1_col2 = df.iloc[:, uss_exp_inx + 1: uss_web_idx]
df2_aft_col2 = df.iloc[:, uss_web_idx + 1 :]

df2 = pd.concat([df2_bef_col1, df2_btw_col1_col2, df2_aft_col2], axis = 1)
df2.head()

"""#### 1. EDA
- age - majority: 20 - 29 years old: 66.84%
- gender - majority: Female: 73.16%
- tourist/local - majority: Local: 93.16%
"""

n = len(df)

"""##### Age"""

# age
age_eda = df.copy()
age_pk = pd.read_csv('/content/drive/MyDrive/DSA3101 Data/Survey Mapped Primary Keys/Age_mapped.csv')

# count number of instances of each category
age_counts = age_eda['Age'].value_counts().reset_index().sort_values(by='Age')
age_counts.columns = ['a', 'Count']
age_counts_merged = pd.merge(age_pk, age_counts, left_on='Age_ID', right_on='a', how='inner').drop(columns=['a']) # drop duplicate column
age_counts_merged

# get exact percentages
for index, row in age_counts_merged.iterrows():
    age = row['Age']
    count = row['Count']
    percentage = (count / n) * 100
    print(f"{age}: {percentage:.2f}%")

# 19 years old and younger: 9.47%
# 20 - 29 years old: 66.84%
# 30 - 39 years old: 6.84%
# 40 - 49 years old: 7.37%
# 50 years old and above: 9.47%

# visualise
plt.figure(figsize=(8, 5))
sns.barplot(data=age_counts_merged, x='Age', y='Count')
plt.title('Distribution of Age Categories')
plt.xlabel('Age Category')
plt.ylabel('Count')
plt.xticks(fontsize=8)
plt.tight_layout()
plt.show

"""##### Gender"""

# gender
gender_eda = df.copy()
gender_pk = pd.read_csv('/content/drive/MyDrive/DSA3101 Data/Survey Mapped Primary Keys/Gender_mapped.csv')

# count number of instances of each category
gender_counts = age_eda['Gender'].value_counts().reset_index().sort_values(by='Gender')
gender_counts.columns = ['g', 'Count']
gender_counts_merged = pd.merge(gender_pk, gender_counts, left_on='Gender_ID', right_on='g', how='inner').drop(columns=['g']) # drop duplicate column
gender_counts_merged

# get exact percentages
for index, row in gender_counts_merged.iterrows():
    gender = row['Gender']
    count = row['Count']
    percentage = (count / n) * 100
    print(f"{gender}: {percentage:.2f}%")

# Male: 26.84%
# Female: 73.16%

# visualise
plt.figure(figsize=(8, 5))
sns.barplot(data=gender_counts_merged, x='Gender', y='Count')
plt.title('Distribution of Gender Categories')
plt.xlabel('Gender Category')
plt.ylabel('Count')
plt.tight_layout()
plt.show

"""##### Tourist/Local"""

# tourist/local
tl_eda = df.copy()
tl_pk = pd.read_csv('/content/drive/MyDrive/DSA3101 Data/Survey Mapped Primary Keys/Tourist_Local_mapped.csv')

# count number of instances of each category
tl_counts = age_eda['Tourist/Local'].value_counts().reset_index().sort_values(by='Tourist/Local')
tl_counts.columns = ['tl', 'Count']
tl_counts_merged = pd.merge(tl_pk, tl_counts, left_on='Tourist/Local_ID', right_on='tl', how='inner').drop(columns=['tl']) # drop duplicate column
tl_counts_merged

# get exact percentages
for index, row in tl_counts_merged.iterrows():
    gender = row['Tourist/Local']
    count = row['Count']
    percentage = (count / n) * 100
    print(f"{gender}: {percentage:.2f}%")

# Tourist: 6.84%
# Local: 93.16%

# visualise
plt.figure(figsize=(8, 5))
sns.barplot(data=tl_counts_merged, x='Tourist/Local', y='Count')
plt.title('Distribution of Tourist/Local Categories')
plt.xlabel('Tourist/Local Category')
plt.ylabel('Count')
plt.tight_layout()
plt.show

"""#### 2. SVD

We first perform SVD to increase the number of data points we have to prepare the data for SMOTE by increasing the number of minority data we have whilst maintaining the distribution. Since SVD replicates the behaviour of the original data, the synthesised data should have similar behaviour and distributions to the original dataframe.

##### SVD algorithm
"""

# 1. Create a metadata object and detect the properties of your dataframe
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(data=df2)

# 2. Inspect metadata to ensure correct column types and properties
print("Detected Metadata:")
print(metadata.to_dict())  # This will show the types of your columns

# 3. Optionally modify metadata if necessary (e.g., correct any misclassified columns)
# metadata.update_column(column_name='age', sdtype='numerical')

# 4. Initialize the GaussianCopulaSynthesizer with the metadata
synthesizer = GaussianCopulaSynthesizer(metadata=metadata)

# 5. Fit the synthesizer to your dataframe
synthesizer.fit(df2)

# 6. Sample synthetic data (adjust num_rows as needed)
synthetic_data = synthesizer.sample(num_rows=len(df2))
synthetic_data

# # 7. Show synthetic data
# print(synthetic_data.head())  # Display the first few rows of synthetic data

"""##### Evaluate distribution of the synthesised data"""

def compare_summary_statistics(real_data, synthetic_data):
    """
    Compare summary statistics (mean, median, standard deviation) between real and synthetic data.

    Parameters:
    - real_data: Real dataset (pandas DataFrame)
    - synthetic_data: Synthetic dataset (pandas DataFrame)
    """
    stats_real = real_data.describe().T[['mean', '50%', 'std']]
    stats_synthetic = synthetic_data.describe().T[['mean', '50%', 'std']]

    comparison = pd.concat([stats_real, stats_synthetic], axis=1, keys=['Real', 'Synthetic'])
    print(comparison)

# Example usage
compare_summary_statistics(df2, synthetic_data)

def compare_summary_statistics(real_data, synthetic_data, threshold):
    """
    Compare summary statistics (mean, median, standard deviation) between real and synthetic data.
    Calculate percentage differences and flag significant discrepancies.

    Parameters:
    - real_data: Real dataset (pandas DataFrame)
    - synthetic_data: Synthetic dataset (pandas DataFrame)
    - threshold (float): The percentage difference threshold to flag large deviations (default is 5%).

    Returns:
    - comparison (pd.DataFrame): DataFrame containing the statistics and percentage differences.
    - significant_diff (pd.DataFrame): DataFrame containing columns with significant deviations.
    """
    # Calculate summary statistics for real and synthetic data
    stats_real = real_data.describe().T[['mean', '50%', 'std']].rename(columns={'50%': 'median'})
    stats_synthetic = synthetic_data.describe().T[['mean', '50%', 'std']].rename(columns={'50%': 'median'})

    # Combine both into one DataFrame for easy comparison
    comparison = pd.concat([stats_real, stats_synthetic], axis=1, keys=['Real', 'Synthetic'])

    # Calculate percentage differences for mean, median, and standard deviation
    for stat in ['mean', 'median', 'std']:
        comparison[('Difference', stat)] = (comparison[('Synthetic', stat)] - comparison[('Real', stat)]) / comparison[('Real', stat)] * 100

    # Flag significant differences based on the threshold
    significant_diff = comparison[comparison[('Difference', 'mean')].abs() > threshold]

    # Output the results
    # print(f"Summary statistics comparison (threshold: {threshold}%):")
    # print(comparison)

    if not significant_diff.empty:
        print(f"\nColumns with significant differences (more than {threshold}%):")
        print(significant_diff)
    else:
        print("\nNo significant differences found.")

    return comparison, significant_diff

# Example usage:
comparison, significant_diff = compare_summary_statistics(df2, synthetic_data, 10.0)
significant_diff

"""##### Add synthesised data to the original data"""

merged_df = pd.concat([df2, synthetic_data], ignore_index=True)
merged_df

"""#### 3. SMOTE

We address the imbalanced data by first using oversampling to synthesise data. We will also use the number of data that falls under certain demographics of people to guide our subsequent data synthesis using domain knowledge.
"""

def balance_distributions_with_smote(df, target_columns):
    balanced_df = df.copy()  # Start with a copy of the original DataFrame
    for col in target_columns:
        print(f"Original distribution for column: {col}")
        print(balanced_df[col].value_counts(normalize=True) * 100)
        print("\n" + "-" * 40 + "\n")

        # Prepare data for resampling
        X = balanced_df.drop(columns=[col])
        y = balanced_df[col]

        # Initialize SMOTE
        smote = SMOTE(random_state=42)

        # Apply SMOTE
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Create a new DataFrame for the resampled data
        resampled_df = pd.DataFrame(X_resampled, columns=X.columns)

        # Concatenate the target column with the resampled features
        resampled_df[col] = y_resampled

        # Concatenate original and resampled DataFrames
        balanced_df = pd.concat([balanced_df, resampled_df], ignore_index=True)

        # Reset index after concatenation to ensure it's clean
        balanced_df.reset_index(drop=True, inplace=True)

        # Print new distribution
        print(f"New distribution for column: {col}")
        print(balanced_df[col].value_counts(normalize=True) * 100)
        print("\n" + "-" * 40 + "\n")

    return balanced_df

# Specify the categorical columns you want to balance
target_columns = ['Age', 'Gender', 'Tourist/Local']

# Call the function to balance distributions using SMOTE
balanced_df = balance_distributions_with_smote(merged_df, target_columns)
balanced_df

def print_category_distributions(df):
    # Iterate over each column in the DataFrame
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):  # Include integer-based categorical columns
            print(f"Distribution for column: {col}")
            print(df[col].value_counts(normalize=True) * 100)  # Normalize for percentage
            print("\n" + "-"*40 + "\n")

# Example usage with your DataFrame
print_category_distributions(balanced_df)

"""#### 4. Add back Survey_ID column and open-ended questions"""

df_syn = balanced_df.copy()
df_syn = df_syn.iloc[len(df2) : , :] # return synthesised data
df_orig = df2.copy() # original data

# add open-ended qns back to df_orig (add to end)
df_orig = pd.concat([df_orig, df['Suggestions for improving USS experience'], df['Suggestions for improving USS website']], axis = 1)
# df_orig.head()

# add rows on 'nil' for open-ended questions in df_syn (add to end)
df_syn['Suggestions for improving USS experience'] = 'nil'
df_syn['Suggestions for improving USS website'] = 'nil'
df_syn.head()

# merge original and synthesised data together
df3 = pd.concat([df_orig, df_syn], ignore_index=True)

# add Survey_ID back
df3['Survey_ID'] = range(1, len(df3) + 1)
df3.insert(0, 'Survey_ID', df3.pop('Survey_ID'))

df3.head(5)

"""### Export final cleaned excel file (csv, xlsx)"""

## cleaned balanced survey data ##

# export as csv
csv_file_name = "Survey_cleaned_balanced.csv"
csv_folder_path = '/content/drive/MyDrive/DSA3101 Data/Processed Data/'

df3.to_csv(csv_folder_path + csv_file_name, index=False)  # exclude index
print(f"Exported df3 to {csv_folder_path + csv_file_name}")

# export as xlsx
excel_file_name = "Survey_cleaned_balanced.xlsx"
excel_folder_path = '/content/drive/MyDrive/DSA3101 Data/Processed Data/'

df3.to_excel(excel_folder_path + excel_file_name, index=False)  # exclude index
print(f"Exported df3 to {excel_folder_path + excel_file_name}")
