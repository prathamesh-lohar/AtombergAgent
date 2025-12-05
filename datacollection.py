import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
SEARCH_QUERY = '"smart fan" (atomberg OR orient OR havells)'
SCROLL_LIMIT = 5  # Increase this to get more data

def init_driver():
    # undetected_chromedriver automatically handles the driver binary
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # NEVER use headless with X.com, it triggers detection immediately
    
    print("Starting Undetected Chrome...")
    driver = uc.Chrome(options=options, version_main=142)
    return driver

def scrape_tweets(driver):
    print(f"Navigating to search: {SEARCH_QUERY}")
    search_url = f"https://twitter.com/search?q={SEARCH_QUERY}&src=typed_query&f=live"
    driver.get(search_url)
    time.sleep(5) 

    tweets_data = []
    unique_ids = set()
    
    print("Beginning extraction...")
    
    for i in range(SCROLL_LIMIT):
        print(f"  - Scrolling page {i+1}/{SCROLL_LIMIT}...")
        
        # Find all tweet articles
        articles = driver.find_elements(By.TAG_NAME, "article")
        
        for article in articles:
            try:
                # 1. Extract Tweet Text
                text_element = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                tweet_text = text_element.text.replace("\n", " ")
                
                # Deduplicate
                if tweet_text in unique_ids:
                    continue
                unique_ids.add(tweet_text)

                # 2. Extract Metrics (Likes/Replies/Retweets)
                try:
                    # Metrics are in a 'group' div with an aria-label like "5 replies, 20 likes"
                    metrics_group = article.find_element(By.XPATH, './/div[@role="group"]')
                    metrics_raw = metrics_group.get_attribute("aria-label")
                except:
                    metrics_raw = "0 metrics"

                # 3. Extract Handle (Who tweeted?)
                try:
                    user_element = article.find_element(By.XPATH, './/div[@data-testid="User-Name"]')
                    handle = user_element.text.split("\n")[-1] # Usually gets @username
                except:
                    handle = "Unknown"

                tweets_data.append({
                    "User": handle,
                    "Text": tweet_text,
                    "Metrics": metrics_raw
                })
                
            except Exception as e:
                # Skip tweets that are ads or malformed
                continue

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Randomized sleep to look human
        time.sleep(4) 

    return pd.DataFrame(tweets_data)

# --- MAIN EXECUTION FLOW ---
if __name__ == "__main__":
    driver = init_driver()
    
    try:
        # 1. Open Login Page
        driver.get("https://twitter.com/i/flow/login")
        
        # 2. PAUSE FOR HUMAN INTERVENTION
        print("\n" + "="*50)
        print("ACTION REQUIRED: Please log in manually in the browser window.")
        print("Handle any 2FA or Captchas yourself.")
        input(">>> Once you are on the Home Feed, press ENTER here to start scraping: ")
        print("="*50 + "\n")
        
        # 3. Start Scraping
        df = scrape_tweets(driver)
        
        # 4. Save Data
        print(f"\nSuccess! Scraped {len(df)} tweets.")
        filename = "atomberg_tweets.csv"
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        print("Closing driver...")
        driver.quit()