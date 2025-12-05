import pandas as pd
import numpy as np
from textblob import TextBlob
import re

# --- CONFIGURATION ---
INPUT_FILE = "atomberg_tweets.csv" # The file you just scraped
TARGET_BRAND = "atomberg"
COMPETITORS = ["orient", "havells", "crompton", "polycab", "usha"]

def clean_metric_count(metric_str):
    """
    Converts '1.5K', '10M', '5' into integers.
    Parses strings like "5 replies, 10 likes" to extract the highest number or sum them.
    """
    if pd.isna(metric_str) or metric_str == "0 metrics":
        return 0
    
    # Extract all numbers from the string
    # This finds patterns like 1.5K, 10, 500
    numbers = re.findall(r'(\d+\.?\d*)([KkMm]?)', str(metric_str))
    
    total_score = 0
    for num, multiplier in numbers:
        val = float(num)
        if multiplier.lower() == 'k':
            val *= 1000
        elif multiplier.lower() == 'm':
            val *= 1000000
        total_score += val
        
    return int(total_score)

def get_sentiment_weight(text):
    """
    Returns a multiplier based on sentiment.
    Positive = 1.5x (Boost)
    Neutral = 1.0x (Baseline)
    Negative = 0.5x (Penalty)
    """
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity # Range from -1 to 1
    
    if polarity > 0.1:
        return 1.5 # Positive
    elif polarity < -0.1:
        return 0.5 # Negative
    else:
        return 1.0 # Neutral

def identify_brand(text):
    text = str(text).lower()
    if TARGET_BRAND in text:
        return "Atomberg"
    
    for comp in COMPETITORS:
        if comp in text:
            return "Competitor"
            
    return "Irrelevant"

# --- MAIN EXECUTION ---
print("1. Loading Data...")
df = pd.read_csv(INPUT_FILE)

# 2. Process Data
print("2. Analyzing Sentiment & Metrics...")
df['clean_metrics'] = df['Metrics'].apply(clean_metric_count)
df['brand_type'] = df['Text'].apply(identify_brand)
df['sentiment_weight'] = df['Text'].apply(get_sentiment_weight)

# 3. Calculate "Impact Score"
# Logic: Logarithmic Engagement * Sentiment Weight
# We add +1 to log to handle 0 engagement cases safely
df['impact_score'] = np.log1p(df['clean_metrics']) * df['sentiment_weight']

# Filter out irrelevant tweets (those mentioning neither brand)
relevant_df = df[df['brand_type'] != "Irrelevant"]

# 4. Calculate Share of Voice (SoV)
print("\n" + "="*40)
print("FINAL RESULTS FOR REPORT")
print("="*40)

# Group by brand type
results = relevant_df.groupby('brand_type')['impact_score'].sum()

atomberg_score = results.get('Atomberg', 0)
competitor_score = results.get('Competitor', 0)
total_market_score = atomberg_score + competitor_score

if total_market_score > 0:
    sov_percentage = (atomberg_score / total_market_score) * 100
else:
    sov_percentage = 0

print(f"Total Mentioned Tweets Processed: {len(relevant_df)}")
print(f"Atomberg Total Impact Score: {atomberg_score:.2f}")
print(f"Competitor Total Impact Score: {competitor_score:.2f}")
print("-" * 20)
print(f"ATOMBERG SHARE OF VOICE (Q-SoV): {sov_percentage:.2f}%")
print("="*40)

# Optional: Save processed data to check your work
relevant_df.to_csv("final_analysis_results.csv", index=False)
print("\nDetailed analysis saved to 'final_analysis_results.csv'")