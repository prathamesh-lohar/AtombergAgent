import pandas as pd
import numpy as np
import dotenv
dotenv.load_dotenv()
import time
import re
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from textblob import TextBlob 

# --- AI CONFIGURATION ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# API Key Check
os.environ["GOOGLE_API_KEY"] = os.getenv("api")

# --- MODULE 1: THE BRAIN ---
class CognitionEngine:
    def __init__(self):
        self.active = True
        print("[Brain] 🧠 Initializing Gemini Engine...")
        self.llm = self._connect_to_model()

    def _connect_to_model(self):
        candidates = ["gemini-2.5-flash-live", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        for m in candidates:
            try:
                llm = ChatGoogleGenerativeAI(model=m, temperature=0, max_retries=1)
                llm.invoke("Hi")
                print(f"[Brain] ✅ Connected to {m}")
                return llm
            except: continue
        self.active = False
        print("[Brain] ⚠️ Offline Mode.")
        return None

    def analyze(self, text):
        # 1. Entity Detection (Rule-based is safer for SoV)
        text_lower = str(text).lower()
        entity = "Generic"
        if "atomberg" in text_lower: entity = "ATOMBERG"
        elif any(x in text_lower for x in ["havells", "orient", "crompton", "polycab", "ottomate"]): entity = "COMPETITOR"
        
        # 2. Sentiment/Category (AI)
        category = "Chatter"
        sentiment = 0
        insight = "General"
        
        if self.active and self.llm:
            try:
                prompt = ChatPromptTemplate.from_template("""
                Analyze post: "{text}"
                1. Category: Feature, Complaint, Praise, Pricing, Chatter.
                2. Sentiment: -1.0 to 1.0.
                3. Insight: Max 4 words.
                Output: CATEGORY|SENTIMENT|INSIGHT
                """)
                res = (prompt | self.llm).invoke({"text": text})
                parts = res.content.strip().split("|")
                category = parts[0].strip()
                sentiment = float(parts[1].strip())
                insight = parts[2].strip()
            except: pass
        
        if sentiment == 0: # Fallback
            sentiment = TextBlob(str(text)).sentiment.polarity

        return {"entity": entity, "sentiment": sentiment, "category": category, "insight": insight}

# --- MODULE 2: THE AGENT ---
class AtombergMarketingAgent:
    def __init__(self):
        self.name = "Atomberg_Omni_Agent"
        self.memory = pd.DataFrame()
        self.deep_memory = pd.DataFrame()
        self.driver = None
        self.brain = CognitionEngine()

    def _init_driver(self):
        if not self.driver:
            options = uc.ChromeOptions()
            # options.add_argument('--headless') 
            #identify version_main dynamically
            try:
                import subprocess
                result = subprocess.run(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    capture_output=True,
                    text=True
                )
                version_match = re.search(r'(\d+)\.', result.stdout)
                version_main = int(version_match.group(1)) if version_match else None
                self.driver = uc.Chrome(options=options, version_main=version_main)
            except:
                # Fallback: let undetected_chromedriver auto-detect
                self.driver = uc.Chrome(options=options, version_main=142)


    def _parse_metrics(self, text):
        # Parses "1.2M views" or "5K likes"
        text = str(text).upper()
        if "K" in text: return float(re.findall(r"[\d\.]+", text)[0]) * 1000
        if "M" in text: return float(re.findall(r"[\d\.]+", text)[0]) * 1000000
        if re.findall(r"[\d\.]+", text): return float(re.findall(r"[\d\.]+", text)[0])
        return 0

    # --- PHASE 1: YOUTUBE SURVEYOR ---
    def scan_youtube(self, query="smart fan review", limit_n=10):
        self._init_driver()
        print(f"\n[{self.name}] 📺 Phase 1A: Scanning YouTube Top {limit_n}...")
        try:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            self.driver.get(url)
            time.sleep(3)
            
            scraped_ids = set()
            scrolls = 0
            while len(scraped_ids) < limit_n and scrolls < 5:
                items = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
                for item in items:
                    try:
                        title_el = item.find_element(By.ID, "video-title")
                        title = title_el.text
                        link = title_el.get_attribute("href")
                        
                        try:
                            meta = item.find_element(By.XPATH, './/div[@id="metadata-line"]/span[1]').text
                            views = self._parse_metrics(meta)
                        except: views = 0
                        
                        if title not in scraped_ids:
                            scraped_ids.add(title)
                            self.memory = pd.concat([self.memory, pd.DataFrame([{
                                "source": "YouTube", "text": title, "metrics": views, 
                                "url": link, "type": "Feed"
                            }])], ignore_index=True)
                            print(f"   -> Found Video: {title[:30]}... ({views} views)")
                    except: continue
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(3)
                scrolls += 1
        except Exception as e: print(f"YouTube Error: {e}")

    # --- PHASE 1: X (TWITTER) SURVEYOR ---
    def scan_twitter(self, query="smart fan", limit_n=10):
        self._init_driver()
        print(f"\n[{self.name}] 🐦 Phase 1B: Scanning X (Twitter) Top {limit_n}...")
        try:
            self.driver.get("https://twitter.com/i/flow/login")
            print(f"[{self.name}] ⚠️ ACTION: Log in to X manually.")
            input(">>> Press ENTER here once you see the Home Feed: ")
            
            url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
            self.driver.get(url)
            time.sleep(5)
            
            scraped_ids = set()
            scrolls = 0
            while len(scraped_ids) < limit_n and scrolls < 5:
                items = self.driver.find_elements(By.TAG_NAME, "article")
                for item in items:
                    try:
                        text = item.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                        
                        # Get URL (Timestamp link)
                        try:
                            time_el = item.find_element(By.TAG_NAME, "time")
                            link = time_el.find_element(By.XPATH, "..").get_attribute("href")
                        except: link = ""

                        # Get Metrics (Approximate from aria-label)
                        try:
                            group = item.find_element(By.XPATH, './/div[@role="group"]')
                            metrics_text = group.get_attribute("aria-label")
                            views = self._parse_metrics(metrics_text) # Sums up numbers found
                        except: views = 0

                        if text not in scraped_ids:
                            scraped_ids.add(text)
                            self.memory = pd.concat([self.memory, pd.DataFrame([{
                                "source": "X", "text": text, "metrics": views, 
                                "url": link, "type": "Feed"
                            }])], ignore_index=True)
                            print(f"   -> Found Tweet: {text[:30]}... ({views} eng.)")
                    except: continue
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                scrolls += 1
        except Exception as e: print(f"X Error: {e}")

    # --- PHASE 2: THE ANALYST (Deep Dive) ---
    def deep_dive_best_content(self):
        print(f"\n[{self.name}] 🕵️ Phase 2: Drilling into Viral Content...")
        
        # 1. Identify best Atomberg post
        self._analyze_memory()
        atomberg_content = self.memory[self.memory['entity'] == "ATOMBERG"]
        
        if atomberg_content.empty:
            print("No Atomberg content found.")
            return

        top_post = atomberg_content.sort_values(by="metrics", ascending=False).iloc[0]
        target_url = top_post['url']
        source = top_post['source']
        print(f"[{self.name}] 🎯 Viral Hit Found on {source}: {top_post['text'][:40]}...")
        
        try:
            self.driver.get(target_url)
            time.sleep(5)
            
            new_comments = []
            if source == "YouTube":
                self.driver.execute_script("window.scrollTo(0, 600);")
                time.sleep(3)
                comments = self.driver.find_elements(By.TAG_NAME, "ytd-comment-thread-renderer")
                for c in comments[:10]:
                    try:
                        t = c.find_element(By.ID, "content-text").text
                        new_comments.append({"text": t, "source": "YouTube Comment"})
                    except: continue
                    
            elif source == "X":
                self.driver.execute_script("window.scrollTo(0, 500);")
                time.sleep(3)
                # X Replies (skip the first article as it's the main tweet)
                replies = self.driver.find_elements(By.TAG_NAME, "article")
                for r in replies[1:8]:
                    try:
                        t = r.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                        new_comments.append({"text": t, "source": "X Reply"})
                    except: continue
            
            if new_comments:
                self.deep_memory = pd.DataFrame(new_comments)
                print(f"[{self.name}] ✅ Extracted {len(new_comments)} comments/replies.")
                
        except Exception as e: print(f"Deep Dive Error: {e}")

    # --- PHASE 3: REPORTING ---
    def _analyze_memory(self):
        if "entity" not in self.memory.columns:
            results = []
            for _, row in self.memory.iterrows():
                res = self.brain.analyze(row['text'])
                results.append({**row, **res})
            self.memory = pd.DataFrame(results)

    def generate_final_report(self):
        self._analyze_memory()
        df = self.memory
        
        # Weighted SoV
        df['log_impact'] = np.log1p(df['metrics'])
        atomberg_impact = df[df['entity']=="ATOMBERG"]['log_impact'].sum()
        total_impact = df['log_impact'].sum()
        sov = (atomberg_impact / total_impact * 100) if total_impact > 0 else 0
        
        print("\n" + "="*50)
        print("📢 FINAL ATOMBERG INTELLIGENCE REPORT")
        print("="*50)
        print(f"Total Posts Scanned: {len(df)}")
        print(f" - YouTube: {len(df[df['source']=='YouTube'])}")
        print(f" - X (Twitter): {len(df[df['source']=='X'])}")
        print("-" * 30)
        print(f"🏆 ATOMBERG SHARE OF VOICE: {sov:.2f}%")
        print("="*50)
        
        if not self.deep_memory.empty:
            print("💡 INSIGHTS FROM DEEP DIVE:")
            print(self.deep_memory['text'].head(5))

    def shutdown(self):
        if self.driver: self.driver.quit()

if __name__ == "__main__":
    agent = AtombergMarketingAgent()
    try:
        # 1. Scan YouTube
        agent.scan_youtube("smart fan review", limit_n=10)
        
        # 2. Scan X (Twitter)
        agent.scan_twitter("smart fan", limit_n=10)
        
        # 3. Deep Dive (Auto-selects best post from either X or YouTube)
        agent.deep_dive_best_content()
        
        # 4. Report
        agent.generate_final_report()
    finally:
        agent.shutdown()