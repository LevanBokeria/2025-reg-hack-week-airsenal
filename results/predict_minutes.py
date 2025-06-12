#!/usr/bin/env python3
"""
Script to copy random files from DEF, FWD, GK, and MID directories
and overwrite the predmin column with a simple prediction based on previous minutes.
"""

import os
import random
from pathlib import Path

import pandas as pd


def get_random_file_from_directory(directory_path):
    """Get a random file from the specified directory."""
    files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    if not files:
        raise ValueError(f"No CSV files found in {directory_path}")
    return random.choice(files)

def predict_minutes_simple(df):
    """
    Simple prediction that uses the previous timestamp's minutes.
    For the first row, use 0 as default.
    """
    df = df.copy()
    df['predmin'] = df['minutes'].shift(1).fillna(0)
    return df

def process_position_files():
    """Main function to process files from each position directory."""
    base_path = Path('/Users/wbrown/Documents/2025-reg-hack-week-airsenal/results')
    positions = ['DEF', 'FWD', 'GK', 'MID']
    
    # Create output directory
    output_dir = base_path / 'predicted_minutes'
    output_dir.mkdir(exist_ok=True)
    
    processed_files = []
    
    for position in positions:
        position_dir = base_path / position
        
        if not position_dir.exists():
            print(f"Warning: Directory {position_dir} does not exist")
            continue
            
        try:
            # Get random file from this position
            random_file = get_random_file_from_directory(position_dir)
            source_path = position_dir / random_file
            
            print(f"Processing {position}: {random_file}")
            
            # Read the CSV file
            df = pd.read_csv(source_path)
            
            # Apply simple prediction
            df_predicted = predict_minutes_simple(df)
            
            # Create output filename
            output_filename = f"single_lagstep_{position}.csv"
            output_path = output_dir / output_filename
            
            # Save the processed file
            df_predicted.to_csv(output_path, index=False)
            
            processed_files.append({
                'position': position,
                'original_file': random_file,
                'output_file': output_filename,
                'rows_processed': len(df_predicted)
            })
            
            print(f"  ✓ Saved to: {output_path}")
            print(f"  ✓ Rows processed: {len(df_predicted)}")
            
        except Exception as e:
            print(f"Error processing {position}: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"Output directory: {output_dir}")
    print(f"Files processed: {len(processed_files)}")
    
    for file_info in processed_files:
        print(f"  {file_info['position']}: {file_info['original_file']} -> {file_info['output_file']} ({file_info['rows_processed']} rows)")

if __name__ == "__main__":
    print("Starting predict_minutes.py script...")
    print("This script will:")
    print("1. Select a random file from each position directory (DEF, FWD, GK, MID)")
    print("2. Copy and process each file")
    print("3. Overwrite predmin column with simple prediction (previous timestamp's minutes)")
    print()
    
    process_position_files()
    print("\nScript completed!")