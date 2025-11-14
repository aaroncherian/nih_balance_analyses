import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import plotly.io as pio

pio.renderers.default = "browser"   # put this once near the top
# Paths
path_to_freemocap_analysis_folder = Path(r"D:\2025_09_03_OKK\freemocap\2025-09-03_14-38-45_GMT-4_okk_nih_2\validation\mediapipe\path_length_analysis\analysis_2025-09-04_13_58_46_rigid")
path_to_qualisys_analysis_folder = Path(r"D:\2025_09_03_OKK\freemocap\2025-09-03_14-38-45_GMT-4_okk_nih_2\validation\qualisys\path_length_analysis\analysis_2025-09-04_13_58_46")

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

    fig.write_html(str(path_to_freemocap_analysis_folder/f'split_violin_{dimension}.html'), full_html=False, include_plotlyjs='cdn')
    fig.write_image(str(path_to_freemocap_analysis_folder/f'split_violin_{dimension}.png'))
