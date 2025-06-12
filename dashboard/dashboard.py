
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def load_data(uploaded_file):
    """Load and validate the CSV data"""
    try:
        df = pd.read_csv(uploaded_file)
        df = df.iloc[:, 1:] # Remove the first column if it's an index or unwanted column
        
        # Check if required columns exist
        required_columns = ['player_id', 'datetime', 'minutes']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV must contain at least these columns: {required_columns}")
            return None
        
        # Check if there are additional columns (model predictions)
        model_columns = [col for col in df.columns if col not in required_columns]
        if not model_columns:
            st.warning("No model prediction columns found. Only 'minutes' will be plotted.")
        
        # Convert Date column to datetime
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def load_player_mapping():
    """Load player ID to name mapping"""
    try:
        mapping_path = "/Users/wbrown/Documents/2025-reg-hack-week-airsenal/results/Player_Id_to_Name.csv"
        mapping_df = pd.read_csv(mapping_path)
        
        # Create a dictionary mapping player_id to name
        player_mapping = dict(zip(mapping_df['player_id'], mapping_df['name']))
        return player_mapping
    except Exception as e:
        st.warning(f"Could not load player name mapping: {str(e)}")
        return None

def create_line_plot(df, player_id, cutoff_date=None, player_mapping=None, selected_models=None):
    """Create a line plot for the selected player with optional cutoff date for line style change"""
    # Filter data for the selected player
    player_data = df[df['player_id'] == player_id].copy()
    
    if player_data.empty:
        st.warning(f"No data found for Player ID: {player_id}")
        return None
    
    # Sort by date to ensure proper line plotting
    player_data = player_data.sort_values('datetime')
    
    # Get model columns (all columns except player_id, Date, Minutes)
    all_model_columns = [col for col in df.columns if col not in ['player_id', 'datetime', 'minutes']]
    
    # Use selected models if provided, otherwise use all model columns
    model_columns = selected_models if selected_models is not None else all_model_columns
    
    # Create the plot
    fig = go.Figure()
    
    # Define colors for different lines (cycling through if more models than colors)
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    def add_line_with_cutoff(x_data, y_data, name, color):
        """Add a line with solid/dashed style based on cutoff date"""
        
        if cutoff_date is None:
            # No cutoff - just add solid line for all
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                name=name,
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
        elif name == 'True Minutes':
            # Minutes column - split at cutoff: solid before, dashed after
            before_cutoff = player_data[player_data['datetime'] <= cutoff_date]
            after_cutoff = player_data[player_data['datetime'] >= cutoff_date]
            
            # Add solid line for data before cutoff
            if not before_cutoff.empty:
                fig.add_trace(go.Scatter(
                    x=before_cutoff['datetime'],
                    y=before_cutoff['minutes'],
                    mode='lines+markers',
                    name=f"{name} (Before)",
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    showlegend=True
                ))
            
            # Add dashed line for data after cutoff
            if not after_cutoff.empty:
                fig.add_trace(go.Scatter(
                    x=after_cutoff['datetime'],
                    y=after_cutoff['minutes'],
                    mode='lines+markers',
                    name=f"{name} (After)",
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond'),
                    showlegend=True
                ))
        else:
            # Model columns - only show after cutoff date with dashed lines
            after_cutoff = player_data[player_data['datetime'] >= cutoff_date]
            
            if not after_cutoff.empty:
                fig.add_trace(go.Scatter(
                    x=after_cutoff['datetime'],
                    y=after_cutoff[name],
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond'),
                    showlegend=True
                ))
    
    # Add True Minutes line (always blue)
    add_line_with_cutoff(player_data['datetime'], player_data['minutes'], 'True Minutes', 'blue')
    
    # Add lines for each model column
    for i, model_col in enumerate(model_columns):
        color = colors[(i + 1) % len(colors)]  # Skip blue (index 0) since it's used for Minutes
        add_line_with_cutoff(player_data['datetime'], player_data[model_col], model_col, color)
    
    # Add vertical line at cutoff date if specified
    if cutoff_date is not None:
        fig.add_vline(
            x=int(cutoff_date.timestamp() * 1000),
            line_dash="dot",
            line_color="gray",
            annotation_text="Cutoff Date",
            annotation_position="top"
        )
    
    # Create title with player name if available
    if player_mapping and player_id in player_mapping:
        title = f'Minutes Played Comparison - {player_mapping[player_id]} (ID: {player_id})'
    else:
        title = f'Minutes Played Comparison - Player ID: {player_id}'
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='datetime',
        yaxis_title='minutes',
        yaxis=dict(range=[-5, 95]),  # Fix y-axis range from 0 to 90
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Player Minutes Dashboard",
        page_icon="⚽",
        layout="wide"
    )
    
    st.title("⚽ Player Minutes Dashboard")
    st.markdown("Upload a CSV file to visualize player minutes predictions vs actual minutes played")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="CSV must contain: player_id, Date, Minutes. Additional columns will be treated as model predictions."
    )
    
    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)
        
        if df is not None:
            # Load player mapping
            player_mapping = load_player_mapping()
            
            # Display basic info about the dataset
            st.subheader("Dataset Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Unique Players", df['player_id'].nunique())
            with col3:
                date_range = f"{df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}"
                st.metric("Date Range", date_range)
            
            # Model selection (before player selection to make it persistent)
            st.subheader("📊 Model Selection")
            
            # Get all available model columns
            all_model_columns = [col for col in df.columns if col not in ['player_id', 'datetime', 'minutes']]
            
            if all_model_columns:
                selected_models = st.multiselect(
                    "Choose models to display:",
                    options=all_model_columns,
                    default=all_model_columns,  # Show all models by default
                    help="Select which model predictions to display on the chart"
                )
            else:
                selected_models = []
                st.info("No model columns found in the dataset.")
            
            # Player selection
            st.subheader("👤 Select Player")
            player_ids = sorted(df['player_id'].unique())
            
            if player_mapping:
                # Create options with player names
                player_options = []
                player_id_to_display = {}
                
                for player_id in player_ids:
                    player_name = player_mapping.get(player_id, f"Unknown Player (ID: {player_id})")
                    display_text = f"{player_name} (ID: {player_id})"
                    player_options.append(display_text)
                    player_id_to_display[display_text] = player_id
                
                selected_display = st.selectbox(
                    "Choose a Player:",
                    player_options,
                    help="Select a player to view their minutes comparison"
                )
                
                selected_player = player_id_to_display[selected_display]
            else:
                # Fallback to player IDs if mapping fails
                selected_player = st.selectbox(
                    "Choose a Player ID:",
                    player_ids,
                    help="Select a player to view their minutes comparison"
                )
            
            # Create and display the plot
            if selected_player:
                # Check if any models are selected
                if not selected_models:
                    st.warning("⚠️ Please select at least one model to display.")
                    return
                
                # Get player data for date range
                player_data = df[df['player_id'] == selected_player].sort_values('datetime')
                
                if not player_data.empty:
                    # Date slider for cutoff point
                    st.subheader("📅 Cutoff Date Selection")
                    st.markdown("Select a cutoff date to reveal **Model predictions**. Before the cutoff: only True Minutes shown. After the cutoff: Model predictions appear as dashed lines.")
                    
                    min_date = player_data['datetime'].min().date()
                    max_date = player_data['datetime'].max().date()
                    
                    # Default to middle date
                    default_date = min_date + (max_date - min_date) / 2
                    
                    cutoff_date = st.slider(
                        "Cutoff Date",
                        min_value=min_date,
                        max_value=max_date,
                        value=default_date,
                        format="YYYY-MM-DD",
                        help="Model predictions will only be shown from this date onwards as dashed lines. True Minutes is always visible."
                    )
                    
                    # Convert back to datetime for plotting
                    cutoff_datetime = pd.to_datetime(cutoff_date)
                    
                    # Option to disable cutoff
                    disable_cutoff = st.checkbox("Disable cutoff (show all data with solid lines)")
                    
                    fig = create_line_plot(df, selected_player, None if disable_cutoff else cutoff_datetime, player_mapping, selected_models)
                else:
                    fig = create_line_plot(df, selected_player, None, player_mapping, selected_models)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data table for selected player
                    if player_mapping and selected_player in player_mapping:
                        player_display_name = f"{player_mapping[selected_player]} (ID: {selected_player})"
                    else:
                        player_display_name = f"Player ID: {selected_player}"
                    
                    st.subheader(f"Data for {player_display_name}")
                    player_data = df[df['player_id'] == selected_player].sort_values('datetime')
                    st.dataframe(player_data, use_container_width=True)
                    
                    # Show summary statistics
                    st.subheader("Summary Statistics")
                    
                    # Get model columns (only selected ones)
                    model_columns = [col for col in selected_models if col in player_data.columns]
                    
                    # Create columns dynamically based on number of models (max 4 columns for readability)
                    num_cols = min(len(model_columns) + 1, 4)  # +1 for True Minutes
                    cols = st.columns(num_cols)
                    
                    # True Minutes stats
                    with cols[0]:
                        st.write("**True Minutes**")
                        st.write(f"Mean: {player_data['minutes'].mean():.1f}")
                        st.write(f"Max: {player_data['minutes'].max()}")
                        st.write(f"Min: {player_data['minutes'].min()}")
                    
                    # Model columns stats
                    for i, model_col in enumerate(model_columns[:3]):  # Limit to 3 models for layout
                        col_idx = i + 1
                        if col_idx < len(cols):
                            with cols[col_idx]:
                                st.write(f"**{model_col}**")
                                st.write(f"Mean: {player_data[model_col].mean():.1f}")
                                st.write(f"Max: {player_data[model_col].max()}")
                                st.write(f"Min: {player_data[model_col].min()}")
                                mae = abs(player_data['minutes'] - player_data[model_col]).mean()
                                st.write(f"MAE: {mae:.1f}")
                    
                    # If more than 3 models, show additional stats in expandable section
                    if len(model_columns) > 3:
                        with st.expander(f"Additional Model Statistics ({len(model_columns) - 3} more models)"):
                            extra_cols = st.columns(min(len(model_columns) - 3, 3))
                            for i, model_col in enumerate(model_columns[3:]):
                                col_idx = i % 3
                                with extra_cols[col_idx]:
                                    st.write(f"**{model_col}**")
                                    st.write(f"Mean: {player_data[model_col].mean():.1f}")
                                    st.write(f"Max: {player_data[model_col].max()}")
                                    st.write(f"Min: {player_data[model_col].min()}")
                                    mae = abs(player_data['minutes'] - player_data[model_col]).mean()
                                    st.write(f"MAE: {mae:.1f}")
    
    else:
        st.info("👆 Please upload a CSV file to get started")
        
        # Show example data format
        st.subheader("Expected CSV Format")
        example_data = pd.DataFrame({
            'player_id': [1, 1, 2, 2],
            'datetime': ['2021-01-01', '2021-01-08', '2021-01-01', '2021-01-08'],
            'minutes': [90, 45, 60, 90],
            'Model_A': [85, 40, 55, 88],
            'Model_B': [88, 43, 58, 92],
            'Baseline': [80, 35, 50, 85]
        })
        st.dataframe(example_data, use_container_width=True)
        st.info("💡 You can have any number of model prediction columns beyond the required player_id, Date, and Minutes columns.")

if __name__ == "__main__":
    main()
