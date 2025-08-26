from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# matplotlib.use("Qt5Agg")

path_to_freemocap_analysis_folder = Path(r'D:\2025_07_31_JSM_pilot\freemocap\2025-07-31_16-00-42_GMT-4_jsm_nih_trial_1\validation\mediapipe\path_length_analysis\analysis_2025-08-26_11_40_15')
path_to_qualisys_analysis_folder = Path(r'D:\2025_07_31_JSM_pilot\freemocap\2025-07-31_16-00-42_GMT-4_jsm_nih_trial_1\validation\qualisys\path_length_analysis\analysis_2025-08-26_14_02_17')

# Colors for FreeMoCap and Qualisys
colors = {'freemocap': '#014E9C', 'qualisys': '#BE4302'}

sns.set_theme(style='whitegrid')

for dimension in ['x', 'y', 'z']:
    velocity_csv = f'condition_velocities_{dimension}.csv'
    path_to_qual_csv = path_to_qualisys_analysis_folder / velocity_csv
    df_qual = pd.read_csv(path_to_qual_csv, index_col=False)
    df_qual.drop(columns=df_qual.columns[0], axis=1, inplace=True)
    df_qual['System'] = 'qualisys'

    path_to_freemocap_csv = path_to_freemocap_analysis_folder / velocity_csv
    df_freemocap = pd.read_csv(path_to_freemocap_csv, index_col=False)
    df_freemocap.drop(columns=df_freemocap.columns[0], axis=1, inplace=True)
    df_freemocap['System'] = 'freemocap'

    df_merged = pd.concat([df_freemocap, df_qual], ignore_index=False, sort=False)

    df_melted = pd.melt(df_merged, id_vars='System', value_vars=['Eyes Open/Solid Ground', 'Eyes Closed/Solid Ground', 'Eyes Open/Foam', 'Eyes Closed/Foam'], var_name='Condition', value_name='COM_Velocity')
    
    ax = sns.violinplot(data=df_melted, x='Condition', y='COM_Velocity', hue='System', split=True, inner='quart', palette=colors, saturation=.6)
    plt.setp(ax.collections, alpha=.8)
    sns.despine(left=True)

    # Increase the size of text
    ax.set_xlabel('Condition', fontsize=16)
    ax.set_ylabel(f'COM {dimension.upper()} Velocity (mm/s)', fontsize=16)
    ax.set_title(f'COM {dimension.upper()} Velocity vs. Condition', fontsize=16)
    ax.tick_params(axis='both', labelsize=14)
    
    ax.set_ylim([-1.5, 1.5])
    fig = ax.get_figure()

    plt.show()

    # fig.savefig(path_to_freemocap_analysis_folder / f'combined_violin_plot_{dimension}.png')
