from dotenv import load_dotenv
import os

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()
username = os.getenv("Username")
password = os.getenv("Password")
# --- CONFIGURATION ---
# NOTE: Use a "burner" account. Excessive scraping can get accounts suspended.
X_USERNAME = username
X_PASSWORD = password
SEARCH_QUERY = '"smart fan" (atomberg OR orient OR havells)' # Targeted search
SCROLL_LIMIT = 5 # How many times to scroll down (controls "Top N" results)

def init_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Keep commented to see the browser work
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login_to_x(driver):
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(5) # Wait for load
    
    # Enter Username
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(X_USERNAME)
    username_field.send_keys(Keys.RETURN)
    time.sleep(3)

    # Enter Password
    try:
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(X_PASSWORD)
        password_field.send_keys(Keys.RETURN)
    except:
        # Sometimes X asks for "Phone/Email" verification first
        print("X asked for verification. Please handle manually in browser if needed.")
    
    time.sleep(5) # Wait for login to complete

def scrape_tweets(driver):
    search_url = f"https://twitter.com/search?q={SEARCH_QUERY}&src=typed_query&f=live"
    driver.get(search_url)
    time.sleep(5)

    tweets_data = []
    unique_ids = set()

    for _ in range(SCROLL_LIMIT):
        # Find all tweet articles on the screen
        articles = driver.find_elements(By.TAG_NAME, "article")
        
        for article in articles:
            try:
                # Extract Text (Data-testid is the most stable selector on X)
                text_element = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                tweet_text = text_element.text
                
                # Check for duplicates
                if tweet_text in unique_ids:
                    continue
                unique_ids.add(tweet_text)

                # Extract Metrics (Likes, Reposts)
                # Note: This relies on "aria-label" which contains numbers like "5 likes"
                # Using a generic collection of metric groups
                metrics = article.find_element(By.XPATH, './/div[@role="group"]')
                metrics_text = metrics.get_attribute("aria-label") or ""
                
                tweets_data.append({
                    "text": tweet_text,
                    "metrics_raw": metrics_text # We will parse "5 likes, 2 replies" later
                })
                
            except Exception as e:
                continue # Skip incomplete tweets

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Be nice to the server!

    return pd.DataFrame(tweets_data)

# --- EXECUTION ---
driver = init_driver()
try:
    login_to_x(driver)
    df = scrape_tweets(driver)
    print(f"Successfully scraped {len(df)} tweets!")
    df.to_csv("x_raw_data.csv", index=False)
finally:
    driver.quit()