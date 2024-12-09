#Step 1:Import the necessary libraies
import os
import glob
import pandas as pd
import plotly.io as pio
import dask.dataframe as dd
from dask import delayed
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Step 2:Load data and metadata
data_dir = "D:\data structures\Research\cleaned_dataset\data"
metadata_file = "D:\data structures\Research\cleaned_dataset\metadata.csv"
pattern = "*.csv"

metadata = pd.read_csv(metadata_file)
all_files = glob.glob(os.path.join(data_dir, pattern))

#Step 3:Filter metadata to files that exist
all_filenames = {os.path.basename(f) for f in all_files}
metadata = metadata[metadata['filename'].isin(all_filenames)]
print("Metadata rows:", len(metadata))
print("Number of CSV files:", len(all_files))

test_csv = os.path.join(data_dir, metadata['filename'].iloc[0])  # First metadata file
df_test = pd.read_csv(test_csv, nrows=5) 
print("Columns in test file:", df_test.columns)
df_test.head()

all_filenames = {os.path.basename(f) for f in all_files}
metadata = metadata[metadata['filename'].isin(all_filenames)]
print("Filtered metadata rows:", len(metadata))

#Step 4:Create dictionaries for quick lookups
file_to_testid = dict(zip(metadata['filename'], metadata['test_id']))
file_to_batteryid = dict(zip(metadata['filename'], metadata['battery_id']))
file_to_temp = dict(zip(metadata['filename'], metadata['ambient_temperature']))
file_to_Re = dict(zip(metadata['filename'], metadata['Re']))
file_to_Rct = dict(zip(metadata['filename'], metadata['Rct']))
file_to_type = dict(zip(metadata['filename'], metadata['type']))
file_to_capacity = dict(zip(metadata['filename'], metadata['Capacity']))
file_to_starttime = dict(zip(metadata['filename'], metadata['start_time']))

#Step 5: Columns to Extract
basic_cols = ["Voltage_measured", "Current_measured", "Temperature_measured", 
              "Current_load", "Voltage_load", "Time", "Sense_current", "Battery_current", "Current_ratio", "Battery_impedance", "Rectified_Impedance", "Current_charge", "Voltage_charge" ]

#Step 6: Define a function to load a single file and attach metadata
def load_file_with_metadata(filepath):
    fname = os.path.basename(filepath)
    # First, read without forcing float
    df = pd.read_csv(filepath, usecols=lambda c: c in basic_cols)
    
    if df.empty:
        print("No data loaded from:", fname, "Check column names or data.")
    else:
        # convert to known numeric columns:
        numeric_columns = ["Voltage_measured", "Temperature_measured", "Voltage_load", "Time"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        #  have complex columns, parsing them:
        # df['Current_measured'] = df['Current_measured'].apply(lambda x: complex(x.strip('()')) if pd.notnull(x) else x)
        
        df['filename'] = fname
        df['test_id'] = file_to_testid.get(fname, None)
        df['battery_id'] = file_to_batteryid.get(fname, None)
        df['ambient_temperature'] = file_to_temp.get(fname, None)
        df['Re'] = file_to_Re.get(fname, None)
        df['Rct'] = file_to_Rct.get(fname, None)
        df['type'] = file_to_type.get(fname, None)
        df['Capacity'] = file_to_capacity.get(fname, None)
        df['start_time'] = file_to_starttime.get(fname, None)
    return df


# Step 7: Load All Files with Dask
dfs = []
for filepath in all_files:
    ddf = dd.from_delayed([delayed(load_file_with_metadata)(filepath)])
    dfs.append(ddf)

if dfs:
    dd_combined = dd.concat(dfs, interleave_partitions=True)
    df_combined = dd_combined.compute()
else:
    df_combined = pd.DataFrame()

print("df_combined shape before filtering:", df_combined.shape)
print(df_combined.head())


missing_metadata = df_combined[df_combined[['test_id','Rct','Re']].isna().any(axis=1)]
if not missing_metadata.empty:
    print("Rows missing test_id, Rct or Re:", missing_metadata.shape)
    # Optionally inspect why:
    # print(missing_metadata[['filename','test_id','Rct','Re']].head())
else:
    print("No missing test_id, Rct, Re before dropping rows.")


#Step 8: Filter and Aggregate
df_combined['Capacity'] = pd.to_numeric(df_combined['Capacity'], errors='coerce')

df_combined['ambient_temperature'] = pd.to_numeric(df_combined['ambient_temperature'], errors='coerce')

#df_combined['Re'] = pd.to_numeric(df_combined['Re'], errors='coerce')

df_combined['Rct'] = pd.to_numeric(df_combined['ambient_temperature'], errors='coerce')




df_agg = df_combined.groupby(['battery_id', 'test_id'], as_index=False).agg({
    'Re': 'mean',
    'Rct': 'mean',
    'Capacity': 'mean',
    'ambient_temperature': 'first'})
print("df_agg shape:", df_agg.shape)
print(df_agg.head())

#Step 9: Plot
# Use the original df_agg as it is for rct.
fig_rct = go.Figure()
for b_id in df_agg['battery_id'].unique():
    subset_rct = df_agg[df_agg['battery_id'] == b_id]
    fig_rct.add_trace(go.Scatter(
        x=subset_rct['test_id'],
        y=subset_rct['Rct'],
        mode='lines',
        name=f'Rct_{b_id}'))

fig_rct.update_layout(
    title='Charge Transfer Resistance (Rct) vs. Test ID',
    xaxis_title='Test ID',
    yaxis_title='Charge Transfer Resistance (Ohms)')
fig_rct.show()

# 2. Plot Re AFTER dropping NaNs in Re.
df_agg_re = df_agg.dropna(subset=['Re'])

fig_re = go.Figure()
for b_id in df_agg_re['battery_id'].unique():
    subset_re = df_agg_re[df_agg_re['battery_id'] == b_id]
    fig_re.add_trace(go.Scatter(
        x=subset_re['test_id'],
        y=subset_re['Re'],
        mode='lines',
        name=f'Re_{b_id}'))

fig_re.update_layout(
    title='Electrolyte Resistance (Re) vs. Test ID',
    xaxis_title='Test ID',
    yaxis_title='Electrolyte Resistance (Ohms)')
fig_re.show()
