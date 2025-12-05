import pandas as pd
import numpy as np
from textblob import TextBlob
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# --- AGENT CONFIGURATION ---
class AtombergMarketingAgent:
    def __init__(self, target_brand, competitors):
        self.name = "Atomberg_Intel_Bot_v1"
        self.target_brand = target_brand
        self.competitors = competitors
        self.memory = None # This will store our DataFrame
        print(f"[{self.name}] Initialized. Mission: Track '{self.target_brand}' vs {self.competitors}")

    # --- TOOL 1: PERCEPTION (Scraping) ---
    def use_tool_scraper(self, search_query, limit=3):
        print(f"\n[{self.name}] 👁️ ACTIVATING PERCEPTION TOOL...")
        print(f"[{self.name}] Searching X (Twitter) for: {search_query}")
        
        # Initialize Driver (Undetected Chrome)
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, version_main=142)
        
        try:
            # 1. Login Handling (Human-in-the-loop)
            driver.get("https://twitter.com/i/flow/login")
            print(f"[{self.name}] ⚠️ WAITING FOR AUTHENTICATION...")
            input(">>> Please log in manually in the browser. Press ENTER here when ready to scrape: ")
            
            # 2. Execute Search
            url = f"https://twitter.com/search?q={search_query}&src=typed_query&f=live"
            driver.get(url)
            time.sleep(5)
            
            collected_data = []
            unique_ids = set()
            
            for i in range(limit):
                print(f"[{self.name}] Scrolling page {i+1}/{limit}...")
                articles = driver.find_elements(By.TAG_NAME, "article")
                
                for article in articles:
                    try:
                        text_el = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                        text = text_el.text.replace("\n", " ")
                        
                        if text in unique_ids: continue
                        unique_ids.add(text)
                        
                        try:
                            metrics_el = article.find_element(By.XPATH, './/div[@role="group"]')
                            metrics = metrics_el.get_attribute("aria-label")
                        except: metrics = "0"
                        
                        collected_data.append({"text": text, "metrics": metrics})
                    except: continue
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
            self.memory = pd.DataFrame(collected_data)
            print(f"[{self.name}] ✅ Perception Complete. Collected {len(self.memory)} data points.")
            
        finally:
            driver.quit()

    # --- TOOL 2: COGNITION (Analysis) ---
    def _clean_metrics(self, metric_str):
        # Internal helper to parse "1.5K" to 1500
        if pd.isna(metric_str): return 0
        numbers = re.findall(r'(\d+\.?\d*)([KkMm]?)', str(metric_str))
        total = 0
        for num, multiplier in numbers:
            val = float(num)
            if multiplier.lower() == 'k': val *= 1000
            elif multiplier.lower() == 'm': val *= 1000000
            total += val
        return int(total)

    def _get_sentiment(self, text):
        # Returns a multiplier: 1.5 (Good), 1.0 (Neutral), 0.5 (Bad)
        polarity = TextBlob(str(text)).sentiment.polarity
        if polarity > 0.1: return 1.5
        elif polarity < -0.1: return 0.5
        return 1.0

    def _identify_entity(self, text):
        text_lower = str(text).lower()
        if self.target_brand in text_lower: return "TARGET"
        for comp in self.competitors:
            if comp in text_lower: return "COMPETITOR"
        return "IRRELEVANT"

    def run_analysis(self):
        print(f"\n[{self.name}] 🧠 ACTIVATING COGNITION ENGINE...")
        if self.memory is None or self.memory.empty:
            print(f"[{self.name}] ❌ Memory empty. Run scraper first.")
            return

        df = self.memory.copy()
        
        # Apply cognitive functions
        df['clean_metrics'] = df['metrics'].apply(self._clean_metrics)
        df['entity'] = df['text'].apply(self._identify_entity)
        df['sentiment_weight'] = df['text'].apply(self._get_sentiment)
        
        # Logic: Impact = Log(Engagement) * Sentiment
        df['impact_score'] = np.log1p(df['clean_metrics']) * df['sentiment_weight']
        
        self.memory = df # Update memory with insights
        print(f"[{self.name}] ✅ Analysis Complete.")

    # --- ACTION: REPORTING ---
    def generate_sov_report(self):
        print(f"\n[{self.name}] 📢 GENERATING MISSION REPORT...")
        
        relevant_data = self.memory[self.memory['entity'] != "IRRELEVANT"]
        results = relevant_data.groupby('entity')['impact_score'].sum()
        
        target_score = results.get("TARGET", 0)
        comp_score = results.get("COMPETITOR", 0)
        total = target_score + comp_score
        
        sov = (target_score / total * 100) if total > 0 else 0
        
        print("\n" + "="*40)
        print(f"MISSION REPORT: {self.target_brand.upper()} SHARE OF VOICE")
        print("="*40)
        print(f"Total Conversations Scanned: {len(self.memory)}")
        print(f"Relevant Conversations:      {len(relevant_data)}")
        print(f"Atomberg Impact Score:       {target_score:.2f}")
        print(f"Competitor Impact Score:     {comp_score:.2f}")
        print("-" * 30)
        print(f"🏆 FINAL SoV METRIC:         {sov:.2f}%")
        print("="*40)

    # --- MAIN WORKFLOW LOOP ---
    def run_mission(self):
        # This is the "Agent Loop"
        query = f'"smart fan" ({self.target_brand} OR {" OR ".join(self.competitors)})'
        
        self.use_tool_scraper(query, limit=4) # Step 1: Perceive
        self.run_analysis()                   # Step 2: Think
        self.generate_sov_report()            # Step 3: Act

# --- INSTANTIATE AND RUN ---
if __name__ == "__main__":
    # Create the agent
    agent = AtombergMarketingAgent(
        target_brand="atomberg",
        competitors=["orient", "havells", "crompton", "polycab"]
    )
    
    # Run the mission
    agent.run_mission()