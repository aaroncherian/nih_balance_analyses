import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Paths
path_to_freemocap_analysis_folder = Path(r'D:\2024-04-25_P01\1.0_recordings\sesh_2024-04-25_14_45_59_P01_NIH_Trial1\data_analysis\freemocap_analysis\analysis_2024-05-14_10_59_10')
path_to_qualisys_analysis_folder = Path(r'D:\2024-04-25_P01\1.0_recordings\sesh_2024-04-25_14_45_59_P01_NIH_Trial1\data_analysis\qualisys_analysis\analysis_2024-05-14_09_55_22')

# Colors
colors = {'freemocap': '#014E9C', 'qualisys': '#BE4302'}

# Common CSV filename
velocity_csv = 'condition_velocities.csv'

# Read and process Qualisys data
path_to_qual_csv = path_to_qualisys_analysis_folder / velocity_csv
df_qual = pd.read_csv(path_to_qual_csv, index_col=False)
df_qual['System'] = 'qualisys'

# Read and process FreeMoCap data
path_to_freemocap_csv = path_to_freemocap_analysis_folder / velocity_csv
df_freemocap = pd.read_csv(path_to_freemocap_csv, index_col=False)
df_freemocap['System'] = 'freemocap'

# Merge the datasets
df_combined = pd.concat([df_freemocap, df_qual], ignore_index=True, sort=False)

# Debug: Print the combined DataFrame columns
print("Columns in df_combined:", df_combined.columns)

# Loop through dimensions
for dimension in ['x', 'y', 'z']:
    # Filter and melt data for the current dimension
    cols = [col for col in df_combined.columns if col.endswith(f'_{dimension}')]
    # Debug: Print selected columns for the current dimension
    print(f"Selected columns for dimension {dimension}:", cols)
    
    if len(cols) != 4:
        print(f"Error: Missing expected columns for dimension {dimension}")
        continue

    df_dimension = df_combined[['System'] + cols]
    df_dimension.columns = ['System', 'Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam']

    df_melted = pd.melt(df_dimension, id_vars=['System'], 
                        value_vars=['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam'], 
                        var_name='Condition', value_name='COM_Velocity')

    # Create subplots
    fig = make_subplots(rows=1, cols=1)

    fig.add_trace(go.Violin(x=df_melted['Condition'][df_melted['System'] == 'freemocap'],
                            y=df_melted['COM_Velocity'][df_melted['System'] == 'freemocap'],
                            legendgroup='freemocap', scalegroup='freemocap', name='freemocap',
                            side='negative',
                            line_color=colors['freemocap']),
                  )

    fig.add_trace(go.Violin(x=df_melted['Condition'][df_melted['System'] == 'qualisys'],
                            y=df_melted['COM_Velocity'][df_melted['System'] == 'qualisys'],
                            legendgroup='qualisys', scalegroup='qualisys', name='qualisys',
                            side='positive',
                            line_color=colors['qualisys']),
                  )

    # Update traces and layout
    fig.update_traces(box_visible=True, meanline_visible=True,
                      points=False,  # show all points
                      scalemode='count')  # scale violin plot area with total count
    fig.update_layout(title=f'COM {dimension.upper()} Velocity vs. Condition',
                      template='plotly_white')

    fig.show()

    # fig.write_html(str(rf'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\split_violin_{dimension}.html'), full_html=False, include_plotlyjs='cdn')
