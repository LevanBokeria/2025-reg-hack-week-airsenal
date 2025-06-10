import pandas as pd

def last_weeks_avg(df, weeks=5):
    # Sort by player and week to ensure correct rolling calculation
    df = df.sort_values(['player', 'week', 'date'])
    df[f'avg_weeks_last_{weeks}'] = df.groupby('player')['minutes'].transform(
        lambda x: x.shift(1).rolling(window=weeks, min_periods=1).mean())
    
    return df


def get_predicted_minutes_rmse(df, minutes_column='minutes', predicted_column='predicted_minutes'):
    """
    Calculate the RMSE between actual minutes and predicted minutes.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing actual and predicted minutes.
    minutes_column (str): Column name for actual minutes.
    predicted_column (str): Column name for predicted minutes.
    
    Returns:
    float: The RMSE value.
    """
    rmse = ((df[minutes_column] - df[predicted_column]) ** 2).mean() ** 0.5
    return rmse