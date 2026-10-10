import pandas as pd
import glob
import os

def explore_and_clean():
    # 1. Detect the CSV file automatically
    csv_files = glob.glob('data/*.csv')
    # Filter out the cleaned files if they exist
    csv_files = [f for f in csv_files if 'clean' not in f]
    
    if not csv_files:
        print("Error: No original dataset found in the 'data' folder.")
        return
        
    file_path = csv_files[0]
    print(f"--- 1. Auto-detected CSV File: {file_path} ---")
    
    # 2. Load it using pandas
    print("\n--- 2. Loading data... ---")
    # 10. Keeping original CSV unchanged (we only read it)
    df = pd.read_csv(file_path, low_memory=False)
    
    # 3. Show number of rows and columns
    print(f"\n--- 3. Dataset Shape ---")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    
    # 4. Display all column names
    print(f"\n--- 4. Column Names ---")
    print(list(df.columns))
    
    # 5. Check data types
    print(f"\n--- 5. Data Types ---")
    print(df.dtypes)
    
    # 6. Check missing values
    print(f"\n--- 6. Missing Values ---")
    print(df.isnull().sum()[df.isnull().sum() > 0]) # Only showing columns with missing values to keep output readable
    
    # 7. Check duplicate rows
    print(f"\n--- 7. Duplicate Rows ---")
    duplicates = df.duplicated().sum()
    print(f"Found {duplicates} duplicate rows.")
    
    # 8. & 9. Identify columns
    print(f"\n--- 8 & 9. Mapping the Columns ---")
    print("Match-level information identified: 'match_id', 'season', 'date', 'venue', 'city', 'toss_winner', 'toss_decision', 'match_won_by', 'player_of_match'")
    print("Ball-by-ball information identified: 'batting_team', 'bowling_team', 'batter', 'bowler', 'runs_batter', 'runs_total', 'bowler_wicket'")
    
    # --- SPLITTING DATA FOR DASHBOARD ---
    # We will generate `matches_clean.csv` and `deliveries_clean.csv` without modifying the original dataset!
    
    # Extract unique matches based on match_id
    match_cols = ['match_id', 'season', 'date', 'venue', 'city', 'toss_winner', 'toss_decision', 'match_won_by', 'player_of_match']
    matches = df[match_cols].drop_duplicates(subset=['match_id']).copy()
    matches = matches.rename(columns={'match_id': 'id', 'match_won_by': 'winner'})
    
    # Extract deliveries
    deliv_cols = ['match_id', 'batting_team', 'bowling_team', 'over', 'ball', 'batter', 'bowler', 'runs_batter', 'runs_total', 'bowler_wicket', 'is_super_over'] if 'is_super_over' in df.columns else ['match_id', 'batting_team', 'bowling_team', 'over', 'ball', 'batter', 'bowler', 'runs_batter', 'runs_total', 'bowler_wicket']
    deliveries = df[deliv_cols].copy()
    deliveries = deliveries.rename(columns={
        'batter': 'batsman', 
        'runs_batter': 'batsman_runs',
        'runs_total': 'total_runs'
    })
    
    # Standardize missing values
    matches['city'] = matches['city'].fillna('Unknown')
    matches['winner'] = matches['winner'].fillna('No Result')
    matches['player_of_match'] = matches['player_of_match'].fillna('None')
    
    # Save for dashboard
    matches.to_csv('data/matches_clean.csv', index=False)
    deliveries.to_csv('data/deliveries_clean.csv', index=False)
    print("\n--- Saved matches_clean.csv and deliveries_clean.csv for the dashboard seamlessly! ---")

if __name__ == "__main__":
    explore_and_clean()
