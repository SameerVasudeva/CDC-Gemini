import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

ACCESSIBLE_COLOR_MALE = "#1f77b4"
ACCESSIBLE_COLOR_FEMALE = "#ff7f0e"

def plot_choropleth_map(df: pd.DataFrame):
    """Renders US state choropleth map of birth counts."""
    state_df = df.groupby(['state_abbr', 'state_of_residence'], as_index=False)['births'].sum()
    
    fig = px.choropleth(
        state_df,
        locations='state_abbr',
        locationmode="USA-states",
        color='births',
        scope="usa",
        hover_name='state_of_residence',
        hover_data={'births': ':,', 'state_abbr': False},
        color_continuous_scale="Viridis",
        labels={'births': 'Total Births'},
        title="U.S. Birth Distribution by Geography"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=450)
    return fig

def plot_monthly_trend(df: pd.DataFrame):
    """Renders chronological monthly birth trend line chart with zero baseline."""
    monthly_df = df.groupby('month', observed=True, as_index=False)['births'].sum()
    
    fig = px.line(
        monthly_df,
        x='month',
        y='births',
        markers=True,
        text=monthly_df['births'].apply(lambda x: f"{x:,}"),
        title="Monthly Birth Trend (Chronological)",
        labels={'month': 'Month', 'births': 'Total Births'}
    )
    fig.update_traces(textposition="top center", line_color="#2b5c8f", line_width=3)
    fig.update_yaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_sex_comparison(df: pd.DataFrame):
    """Renders monthly female vs male grouped bar comparison."""
    sex_df = df.groupby(['month', 'sex_of_infant'], observed=True, as_index=False)['births'].sum()
    
    fig = px.bar(
        sex_df,
        x='month',
        y='births',
        color='sex_of_infant',
        barmode='group',
        color_discrete_map={'Male': ACCESSIBLE_COLOR_MALE, 'Female': ACCESSIBLE_COLOR_FEMALE},
        title="Monthly Comparison of Male vs. Female Births",
        labels={'month': 'Month', 'births': 'Birth Count', 'sex_of_infant': 'Infant Sex'}
    )
    fig.update_yaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_state_ranking(df: pd.DataFrame):
    """Renders horizontal bar chart of birth counts by state."""
    state_df = df.groupby('state_of_residence', as_index=False)['births'].sum()
    state_df = state_df.sort_values('births', ascending=True)

    fig = px.bar(
        state_df,
        x='births',
        y='state_of_residence',
        orientation='h',
        title="Geography Ranking by Total Birth Count",
        labels={'births': 'Total Births', 'state_of_residence': 'State / Geography'}
    )
    fig.update_xaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=max(400, len(state_df) * 18))
    return fig

def plot_top_bottom_comparison(df: pd.DataFrame):
    """Compares top 5 highest and top 5 lowest birth volume states."""
    state_df = df.groupby('state_of_residence', as_index=False)['births'].sum()
    if len(state_df) < 2:
        return None

    sorted_df = state_df.sort_values('births', ascending=False)
    top_5 = sorted_df.head(5).copy()
    top_5['Group'] = 'Top 5 Highest'
    
    bottom_5 = sorted_df.tail(5).sort_values('births', ascending=True).copy()
    bottom_5['Group'] = 'Top 5 Lowest'
    
    combined = pd.concat([top_5, bottom_5])

    fig = px.bar(
        combined,
        x='births',
        y='state_of_residence',
        color='Group',
        orientation='h',
        title="Comparison: Top 5 Highest vs. Top 5 Lowest Geographies",
        labels={'births': 'Total Births', 'state_of_residence': 'State'},
        color_discrete_map={'Top 5 Highest': '#2ca02c', 'Top 5 Lowest': '#d62728'}
    )
    fig.update_xaxes(rangemode="tozero", tickformat=",d")
    fig.update_layout(height=400)
    return fig

def plot_heatmap(df: pd.DataFrame):
    """Renders state-by-month heatmap matrix."""
    pivot_df = df.pivot_table(
        index='state_of_residence', 
        columns='month', 
        values='births', 
        aggfunc='sum',
        observed=False
    ).fillna(0)

    fig = px.imshow(
        pivot_df,
        labels=dict(x="Month", y="State / Geography", color="Births"),
        x=pivot_df.columns.tolist(),
        y=pivot_df.index.tolist(),
        color_continuous_scale="Cividis",
        title="State-by-Month Birth Count Heatmap Matrix"
    )
    fig.update_layout(height=max(450, len(pivot_df) * 16))
    return fig
