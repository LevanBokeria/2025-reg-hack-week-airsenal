# Player Minutes Dashboard

A simple Streamlit dashboard for visualizing player minutes predictions compared to actual minutes played.

## Features

- Upload CSV files with player data
- Interactive line charts showing true minutes vs model predictions
- Player selection dropdown
- **📅 Datetime cutoff slider** - Define a cutoff date to reveal model predictions. Before cutoff: only True Minutes shown. After cutoff: All model columns appear as dashed lines.
- Summary statistics and Mean Absolute Error (MAE) for each model
- Data table view for selected player

## Required CSV Format

Your CSV file must contain the following columns:
- `Player_ID`: Unique identifier for each player
- `Date`: Date in YYYY-MM-DD format
- `Minutes`: True minutes played (ground truth)

**Optional columns:**
- Any additional columns will be treated as model predictions and displayed as separate lines
- Examples: `Model_1`, `Model_2`, `Baseline`, `Neural_Net`, `Random_Forest`, etc.

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the dashboard:
```bash
streamlit run dashboard.py
```

2. Open your browser and go to `http://localhost:8501`

3. Upload your CSV file using the file uploader

4. Select a player ID from the dropdown

5. **Adjust the cutoff date slider** to reveal model predictions from the selected date onwards (before cutoff: only True Minutes visible)

6. View the interactive line chart and summary statistics for all models

## Example Data

The dashboard expects data in this format:

| Player_ID | Date       | Minutes | Model_A | Model_B | Baseline |
|-----------|------------|---------|---------|---------|----------|
| 1         | 2021-01-01 | 90      | 85      | 88      | 80       |
| 1         | 2021-01-08 | 45      | 40      | 43      | 35       |
| 2         | 2021-01-01 | 60      | 55      | 58      | 50       |

💡 **Flexible Model Support**: You can include any number of model prediction columns with any names.

The dashboard will automatically:
- Convert dates to proper datetime format
- Sort data by date for proper line plotting
- Calculate summary statistics including MAE for model evaluation
- Display interactive plots with hover information
- **Reveal all model predictions from the selected cutoff date** - Only True Minutes shown before cutoff, all model columns appear as dashed lines after
- Add a vertical dotted line to mark the cutoff date
- **Support for any number of model columns** - automatically detects and visualizes all prediction columns
