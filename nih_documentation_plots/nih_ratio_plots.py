import pandas as pd
import plotly.graph_objects as go

def aggregate_path_lengths(trials):
  
    trials_dataframe = pd.DataFrame(trials)

    trials_mean = trials_dataframe.mean()
    trials_std = trials_dataframe.std()

    return trials_mean, trials_std, trials_dataframe

# Example usage
trial_1 = {'Eyes Closed, Solid Ground/Eyes Open, Solid Ground':.71, 'Eyes Closed, Foam Pad/Eyes Open, Solid Ground':2.34}
trial_2 = {'Eyes Closed, Solid Ground/Eyes Open, Solid Ground':1.12, 'Eyes Closed, Foam Pad/Eyes Open, Solid Ground':3.79}
trial_3 = {'Eyes Closed, Solid Ground/Eyes Open, Solid Ground':1.26, 'Eyes Closed, Foam Pad/Eyes Open, Solid Ground':3.16}

trial_data = [trial_1, trial_2, trial_3]

trials_mean, trials_std, trials_dataframe = aggregate_path_lengths(trial_data)

# Conditions
conditions = trials_dataframe.columns

# Create a plotly figure
fig = go.Figure()

# Plotting individual trials
for index, row in trials_dataframe.iterrows():
    fig.add_trace(go.Scatter(x=conditions, y=row, mode='lines+markers', line=dict(color='#72117c'), opacity=0.6))

# Adding mean and error bars
fig.add_trace(go.Scatter(x=conditions, y=trials_mean, mode='lines+markers', line=dict(color='black'), error_y=dict(type='data', array=trials_std), name='Mean'))

# Labels and titles
fig.update_layout(
    height = 600,
    width = 700,
    title='NIH Toolbox Ratio Scores',
    xaxis_title='Condition Ratio',
    yaxis_title='Ratio Score',
    font=dict(size=12),
    showlegend=False,
    template = 'plotly_white'
)

# Display the plot
fig.show()

fig.write_html(str(r'C:\Users\aaron\Documents\GitHub\nih_balance_analyses\docs\images\nih_ratio_plots.html'), full_html=False, include_plotlyjs='cdn')