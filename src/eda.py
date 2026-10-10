import pandas as pd
import numpy as np

def load_clean_data(data_dir='data'):
    """Loads the cleaned datasets."""
    matches = pd.read_csv(f'{data_dir}/matches_clean.csv')
    deliveries = pd.read_csv(f'{data_dir}/deliveries_clean.csv')
    return matches, deliveries

def matches_per_season(matches):
    """1. Matches played per season"""
    if 'season' in matches.columns:
        df = matches['season'].value_counts().sort_index().reset_index()
        df.columns = ['season', 'matches'] # Force standard column names
        return df
    return None

def most_successful_teams(matches):
    """2. Most successful teams (total wins)"""
    df = matches['winner'].value_counts().reset_index()
    df.columns = ['team', 'wins']
    return df

def toss_impact(matches):
    """3. Toss impact: does winning the toss help win the match?"""
    matches['toss_winner_is_winner'] = matches['toss_winner'] == matches['winner']
    return matches['toss_winner_is_winner'].value_counts(normalize=True) * 100

def top_run_scorers(deliveries, top_n=10):
    """5. Top run scorers (all-time)"""
    runs = deliveries.groupby('batsman')['batsman_runs'].sum().sort_values(ascending=False).head(top_n)
    return runs.reset_index()

def top_wicket_takers(deliveries, top_n=10):
    """5. Top wicket takers (all-time)"""
    # Count only valid dismissals for bowlers using the 'bowler_wicket' column
    if 'bowler_wicket' in deliveries.columns:
        wickets = deliveries[deliveries['bowler_wicket'] == 1]
        top_bowlers = wickets.groupby('bowler')['bowler_wicket'].count().sort_values(ascending=False).head(top_n)
        df = top_bowlers.reset_index()
        df.columns = ['bowler', 'wickets']
        return df
    return None

def most_pom_awards(matches, top_n=10):
    """7. Most Player of the Match awards"""
    return matches['player_of_match'].value_counts().head(top_n).reset_index().rename(columns={'index': 'player', 'player_of_match': 'awards'})

if __name__ == "__main__":
    print("--- IPL Exploratory Data Analysis (Quick Insights) ---")
    try:
        matches, deliveries = load_clean_data()
        
        print("\n1. Matches Per Season:")
        print(matches_per_season(matches).to_string(index=False))
        
        print("\n2. Top 5 Most Successful Teams:")
        print(most_successful_teams(matches).head().to_string(index=False))
        
        print("\n3. Toss Impact (Win % if Toss is Won):")
        impact = toss_impact(matches)
        print(f"Yes: {impact.get(True, 0):.2f}% | No: {impact.get(False, 0):.2f}%")
        
        print("\n5a. Top 5 Run Scorers:")
        print(top_run_scorers(deliveries, 5).to_string(index=False))
        
        print("\n5b. Top 5 Wicket Takers:")
        print(top_wicket_takers(deliveries, 5).to_string(index=False))
        
    except FileNotFoundError:
        print("Cleaned data not found. Please ensure you ran src/data_cleaning.py first!")
