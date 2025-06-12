import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import pickle
np.random.seed(42)

from sktime.regression.kernel_based import RocketRegressor
from apply_rocket import apply_rocket
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

def run_single_experiment(model, position, train_dict_path, val_dict_path, results_dir):
    """Run a single experiment - this function will be executed in parallel"""
    
    # Load data within each process
    with open(train_dict_path, 'rb') as f:
        train_dict = pickle.load(f)
    with open(val_dict_path, 'rb') as f:
        val_dict = pickle.load(f)
    
    try:
        print(f"Starting {model}-{position}...")
        
        # Run the experiment
        y_pred, y_val = apply_rocket(train_dict, val_dict, 
                                   position=position, 
                                   rocket_model=model)
        
        mae = mean_absolute_error(y_val, y_pred)
        rmse = root_mean_squared_error(y_val, y_pred)
        
        # Save detailed predictions
        pred_file = f'{results_dir}/predictions_{model}_{position}.pkl'
        with open(pred_file, 'wb') as f:
            pickle.dump({
                'predictions': y_pred, 
                'actual': y_val,
                'model': model,
                'position': position,
                'timestamp': datetime.now().isoformat()
            }, f)
        
        result = {
            'model': model,
            'position': position,
            'mae': mae,
            'rmse': rmse,
            'n_samples': len(y_val),
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        print(f"Completed {model}-{position}: RMSE={rmse:.3f}, MAE={mae:.3f}")
        return result
        
    except Exception as e:
        print(f"Error in {model}-{position}: {e}")
        return {
            'model': model,
            'position': position,
            'mae': None,
            'rmse': None,
            'n_samples': None,
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error_message': str(e)
        }

def run_rocket_experiments_parallel(max_workers=4):
    """Run experiments in parallel"""
    
    positions = ['GK','FWD']
    rocket_models = ['rocket']
    
    # Create results directory
    results_dir = '../outputs/rocket_experiments'
    os.makedirs(results_dir, exist_ok=True)
    
    # File paths for data
    train_dict_path = '../datasets/training_dictionary.pkl'
    val_dict_path = '../datasets/validation_dictionary.pkl'
    
    # Initialize or load existing results DataFrame
    results_file = f'{results_dir}/rocket_results_summary.csv'
    if os.path.exists(results_file):
        results_df = pd.read_csv(results_file)
        print(f"Loaded existing results with {len(results_df)} entries")
    else:
        results_df = pd.DataFrame()
        print("Starting fresh experiments")
    
    # Create list of experiments to run
    experiments_to_run = []
    for model in rocket_models:
        for position in positions:
 
            experiments_to_run.append((model, position))
    
    print(f"\nRunning {len(experiments_to_run)} experiments in parallel with {max_workers} workers...")
    print("Experiments to run:", [f"{m}-{p}" for m, p in experiments_to_run])
    
    # Run experiments in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_experiment = {
            executor.submit(run_single_experiment, model, position, 
                          train_dict_path, val_dict_path, results_dir): (model, position)
            for model, position in experiments_to_run
        }
        
        # Process completed jobs as they finish
        for future in as_completed(future_to_experiment):
            model, position = future_to_experiment[future]
            
            try:
                result = future.result()
                
                # Add result to DataFrame
                new_result = pd.DataFrame([result])
                results_df = pd.concat([results_df, new_result], ignore_index=True)
                
                # Save incrementally
                results_df.to_csv(results_file, index=False)
                results_df.to_pickle(f'{results_dir}/rocket_results_summary.pkl')
                
                print(f"✓ Saved results for {model}-{position}")
                
            except Exception as e:
                print(f"✗ Failed to process {model}-{position}: {e}")
    
    return results_df

# Run parallel experiments
results_df = run_rocket_experiments_parallel(max_workers=4)  # Adjust based on your CPU cores

# Display final summary
print("\n" + "="*50)
print("FINAL RESULTS SUMMARY")
print("="*50)

completed_results = results_df[results_df['status'] == 'completed']
if len(completed_results) > 0:
    print("\nRMSE by Position and Model:")
    rmse_pivot = completed_results.pivot(index='position', columns='model', values='rmse')
    print(rmse_pivot.round(3))
    
    print("\nMAE by Position and Model:")
    mae_pivot = completed_results.pivot(index='position', columns='model', values='mae')
    print(mae_pivot.round(3))
else:
    print("No completed results found")