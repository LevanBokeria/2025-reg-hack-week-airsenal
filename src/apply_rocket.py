import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
np.random.seed(42)

from sktime.regression.kernel_based import RocketRegressor

import pickle

def apply_rocket(train_dict, val_dict, position='FWD',rocket_model='rocket'):

    train = train_dict[position]
    val = val_dict[position]

    # Select relevant columns

    # How many minute columns do we have?
    num_minutes = len([col for col in train.columns if col.startswith('minutes_')])

    print(f"Number of minute columns: {num_minutes}")

    # Select those columns that start with 'minutes_' and the 'out_minutes' column
    train = train[[f'minutes_{i}' for i in range(num_minutes)] + ['out_minutes']]
    val   = val[[f'minutes_{i}' for i in range(num_minutes)] + ['out_minutes']]

    # Define X_train as first four columns and y_train as the last column
    X_train = train.iloc[:, :-1]
    y_train = train.iloc[:, -1]

    X_val = val.iloc[:, :-1]
    y_val = val.iloc[:, -1]    

    # Turn X_train into a 2D array
    X_train_array = X_train.values.reshape(X_train.shape[0], X_train.shape[1])
    X_val_array   = X_val.values.reshape(X_val.shape[0], X_val.shape[1])

    # Now fit the regressor
    reg = RocketRegressor(rocket_transform=rocket_model) 
    reg.fit(X_train_array, y_train)

    y_pred = reg.predict(X_val_array)

    return y_pred, y_val