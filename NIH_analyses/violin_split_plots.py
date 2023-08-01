import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Paths
path_to_freemocap_analysis_folder = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_14_53_48_MDN_NIH_Trial3\data_analysis\analysis_2023-06-01_10_12_24')
path_to_qualisys_analysis_folder = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\qualisys_MDN_NIH_Trial3\data_analysis\analysis_2023-06-01_17_14_40')

# Colors
colors = {'freemocap': '#014E9C', 'qualisys': '#BE4302'}

# Loop through dimensions
for dimension in ['x', 'y', 'z']:
    velocity_csv = f'condition_velocities_{dimension}.csv'
    
    # Read and process Qualisys data
    path_to_qual_csv = path_to_qualisys_analysis_folder / velocity_csv
    df_qual = pd.read_csv(path_to_qual_csv, index_col=False)
    df_qual.drop(columns=df_qual.columns[0], axis=1, inplace=True)
    df_qual['System'] = 'qualisys'

    # Read and process FreeMoCap data
    path_to_freemocap_csv = path_to_freemocap_analysis_folder / velocity_csv
    df_freemocap = pd.read_csv(path_to_freemocap_csv, index_col=False)
    df_freemocap.drop(columns=df_freemocap.columns[0], axis=1, inplace=True)
    df_freemocap['System'] = 'freemocap'

    # Merge the datasets
    df_merged = pd.concat([df_freemocap, df_qual], ignore_index=False, sort=False)

    df_melted = pd.melt(df_merged, id_vars='System', value_vars=['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam'], var_name='Condition', value_name='COM_Velocity')

    # Create subplots
    fig = make_subplots(rows=1, cols=1)



    conditions = ['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam']

    fig.add_trace(go.Violin(x=df_melted['Condition'][df_melted['System'] == 'freemocap'],
                            y=df_melted['COM_Velocity'][df_melted['System'] == 'freemocap'],
                            legendgroup = 'freemocap', scalegroup = 'freemocap', name = 'freemocap',
                            side = 'negative',
                            line_color = colors['freemocap']),
                            )
    
    fig.add_trace(go.Violin(x=df_melted['Condition'][df_melted['System'] == 'qualisys'],
                            y=df_melted['COM_Velocity'][df_melted['System'] == 'qualisys'],
                            legendgroup = 'qualisys', scalegroup = 'qualisys', name = 'qualisys',
                            side = 'positive',
                            line_color = colors['qualisys']),
                            )

    # Update traces and layout
    fig.update_traces(box_visible=True, meanline_visible=True,
                      points='all',  # show all points
                      jitter=0.05,   # add some jitter on points for better visibility
                      scalemode='count')  # scale violin plot area with total count
    fig.update_layout(title=f'COM {dimension.upper()} Velocity vs. Condition',
                      template='plotly_white')

    # fig.show()

    fig.write_html(str(rf'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\split_violin_{dimension}.html'), full_html=False, include_plotlyjs='cdn')
