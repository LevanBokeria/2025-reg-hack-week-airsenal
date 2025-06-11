import pandas as pd
import streamlit as st

st.title("🔍 Dashboard Test")
st.write("Testing file uploader functionality")

# Simple file uploader test
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    
    # Try to read the file
    try:
        df = pd.read_csv(uploaded_file)
        st.write("File contents:")
        st.dataframe(df.head())
        st.write(f"Shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload a CSV file to test")
    st.write("Expected file format:")
    example_df = pd.DataFrame({
        'Player_ID': [1, 2, 3],
        'Date': ['2021-01-01', '2021-01-02', '2021-01-03'],
        'Minutes': [30, 45, 60],
        'Model 1': [28, 40, 57],
        'Model 2': [30, 42, 60]
    })
    st.dataframe(example_df)
