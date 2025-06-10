import pandas as pd

def last_weeks_avg(df, weeks=5):

    # Sort by player and week to ensure correct rolling calculation
    df = df.sort_values(['player', 'week', 'date'])

    df[f'avg_weeks_last_{weeks}_mean'] = df.groupby('player')['minutes'].transform(
        lambda x: x.shift(1).rolling(window=weeks, min_periods=1).mean())
    df[f'avg_weeks_last_{weeks}_median'] = df.groupby('player')['minutes'].transform(
        lambda x: x.shift(1).rolling(window=weeks, min_periods=1).median())
    
    return df


def get_predicted_minutes_rmse(df, 
                               minutes_column='minutes', 
                               predicted_column='predicted_minutes',
                               exclude_zero_min_players=False):
    """
    Calculate the RMSE between actual minutes and predicted minutes.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing actual and predicted minutes.
    minutes_column (str): Column name for actual minutes.
    predicted_column (str): Column name for predicted minutes.
    
    Returns:
    float: The RMSE value.
    """

    if exclude_zero_min_players:
        df = filter_zero_min_players(df, minutes_column)

    rmse = ((df[minutes_column] - df[predicted_column]) ** 2).mean() ** 0.5
    return rmse


def filter_zero_min_players(df, minutes_column='minutes'):
    """
    Exclude players with zero total minutes from the DataFrame.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing player minutes.
    minutes_column (str): Column name for actual minutes.
    
    Returns:
    pd.DataFrame: DataFrame excluding players with zero total minutes.
    """
    
    zero_min_players = df.groupby('player')[minutes_column].sum().loc[lambda x: x == 0].index

    return df[~df['player'].isin(zero_min_players)]