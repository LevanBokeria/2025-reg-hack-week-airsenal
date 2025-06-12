#!/bin/bash

# Script to run collate_results.py on all four position subdirectories
# This will merge all model results for each position into a single file

echo "Starting to collate results for all positions..."

# Define the positions
positions=("DEF" "FWD" "GK" "MID")

# Run collate_results.py for each position
for pos in "${positions[@]}"; do
    echo "Processing $pos position..."
    python collate_results.py -i "$pos" -o "collated/${pos}_results.csv"
    echo "Completed $pos position - output saved to collated/${pos}_results.csv"
done

echo "All positions processed successfully!"