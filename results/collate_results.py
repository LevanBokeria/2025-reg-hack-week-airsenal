import argparse
import os

import pandas as pd


def run(directory):
    
    files = sorted(os.listdir(directory))
    df_list = [process_df(directory, file) for file in files]

    # merge all dataframes on player_id, datetime and minutes
    data = df_list[0]
    for tmp_df in df_list[1:]:
        data = pd.merge(data, tmp_df, on=['player_id', 'datetime', 'minutes'], how='outer')

    return data

def process_df(stem, filename):
    df = pd.read_csv(os.path.join(stem, filename), index_col=0)
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    name = filename.split('.')[0]
    df = df.rename(columns={'predmin': name})
    return df
    

if __name__ == "__main__":
    # Make command line operation accepting a file path as an argument 
    parser = argparse.ArgumentParser(description='Collate results from multiple CSV files.')
    parser.add_argument('--input_dir', '-i', type=str, help='Directory containing the CSV files to collate.')
    parser.add_argument('--output_filename', '-o', type=str, default='collated_results.csv', help='Output file name for the collated results.')
    args = parser.parse_args()
    result = run(args.input_dir)
    result.to_csv(args.output_filename)
