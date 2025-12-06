import pandas as pd
import numpy as np
import dotenv
dotenv.load_dotenv()
import time
import re
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        candidates = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        for m in candidates:
            try:
                llm = ChatGoogleGenerativeAI(model=m, temperature=0, max_retries=1)
                llm.invoke("Hi")
                print(f"[Brain] ✅ Connected to {m}")
                return llm
            except: continue
        self.active = False
        print("[Brain] ⚠️ Offline Mode (Keywords only).")
        return None

    def analyze(self, text):
        # 1. Entity Detection
        text_lower = str(text).lower()
        entity = "Generic"
        if "atomberg" in text_lower: entity = "ATOMBERG"
        elif any(x in text_lower for x in ["havells", "orient", "crompton", "polycab", "ottomate"]): entity = "COMPETITOR"
        
        # 2. AI Analysis
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
        # Force kill old instance if exists
        if self.driver:
            try: self.driver.quit()
            except: pass
            
        print(f"[{self.name}] 🔌 Booting new Chrome instance...")
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-first-run')
            # Critical stability fixes for Mac
            options.add_argument('--disable-popup-blocking') 
            
            # Simple init - let UC handle versioning
            self.driver = uc.Chrome(options=options, version_main=142)
            print(f"[{self.name}] ✅ Browser started.")
        except Exception as e:
            print(f"[{self.name}] ❌ CRITICAL DRIVER ERROR: {e}")
            raise e

    def _ensure_driver_alive(self):
        # Self-healing: Restart browser if it crashed
        try:
            if not self.driver or len(self.driver.window_handles) == 0:
                raise Exception("Window missing")
        except:
            print(f"[{self.name}] ⚠️ Browser connection lost. Restarting...")
            self._init_driver()

    def _parse_metrics(self, text):
        text = str(text).upper()
        if "K" in text: return float(re.findall(r"[\d\.]+", text)[0]) * 1000
        if "M" in text: return float(re.findall(r"[\d\.]+", text)[0]) * 1000000
        if re.findall(r"[\d\.]+", text): return float(re.findall(r"[\d\.]+", text)[0])
        return 0

    # --- PHASE 1: YOUTUBE SURVEYOR ---
    def scan_youtube(self, query="smart fan review", limit_n=10):
        self._ensure_driver_alive()
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
                        try: meta = item.find_element(By.XPATH, './/div[@id="metadata-line"]/span[1]').text
                        except: meta = "0"
                        views = self._parse_metrics(meta)
                        
                        if title not in scraped_ids:
                            scraped_ids.add(title)
                            self.memory = pd.concat([self.memory, pd.DataFrame([{
                                "source": "YouTube", "text": title, "metrics": views, 
                                "url": link, "type": "Feed"
                            }])], ignore_index=True)
                            print(f"   -> Found: {title[:30]}...")
                    except: continue
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                scrolls += 1
        except Exception as e: print(f"YT Error: {e}")

    # --- PHASE 1: X (TWITTER) SURVEYOR ---
    def scan_twitter(self, query="smart fan", limit_n=10):
        self._ensure_driver_alive()
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
                        try:
                            time_el = item.find_element(By.TAG_NAME, "time")
                            link = time_el.find_element(By.XPATH, "..").get_attribute("href")
                        except: link = ""
                        
                        if text not in scraped_ids:
                            scraped_ids.add(text)
                            self.memory = pd.concat([self.memory, pd.DataFrame([{
                                "source": "X", "text": text, "metrics": 100, 
                                "url": link, "type": "Feed"
                            }])], ignore_index=True)
                            print(f"   -> Found: {text[:30]}...")
                    except: continue
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                scrolls += 1
        except Exception as e: print(f"X Error: {e}")

    # --- PHASE 2: DEEP DIVE ---
   # --- PHASE 2: DEEP DIVE (WITH ATOMBERG ENFORCEMENT) ---
    def deep_dive_best_content(self):
        print(f"\n[{self.name}] 🕵️ Phase 2: Deep Dive Analysis...")
        
        # 1. First, check our existing memory (from "Smart Fan" search)
        self._analyze_memory()
        atomberg_content = self.memory[
            (self.memory['entity'] == "ATOMBERG") & 
            (self.memory['source'] == "YouTube")
        ]
        
        target_url = None
        source = "YouTube"
        
        # 2. DECISION LOGIC: Organic vs. Forced Search
        if not atomberg_content.empty:
            # We found one naturally! Pick the most viewed one.
            top_post = atomberg_content.sort_values(by="metrics", ascending=False).iloc[0]
            print(f"[{self.name}] ✅ Found Atomberg video in Top 10: '{top_post['text'][:30]}...'")
            target_url = top_post['url']
        else:
            # We didn't find one naturally. FORCE A SEARCH.
            print(f"[{self.name}] ⚠️ No Atomberg video in Top 10 Generic results.")
            print(f"[{self.name}] 🔎 Initiating TARGETED SEARCH for 'Atomberg Renesa Review'...")
            
            try:
                # Force search for specific product
                self.driver.get("https://www.youtube.com/results?search_query=atomberg+renesa+review")
                time.sleep(3)
                
                # Click the first non-ad video
                videos = self.driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
                for v in videos:
                    title = v.find_element(By.ID, "video-title").text
                    # Ensure it's actually about Atomberg
                    if "atomberg" in title.lower():
                        target_url = v.find_element(By.ID, "video-title").get_attribute("href")
                        print(f"[{self.name}] 🎯 Targeted Search Found: '{title[:30]}...'")
                        break
            except Exception as e:
                print(f"[{self.name}] Targeted Search Failed: {e}")

        # 3. EXTRACT COMMENTS (If we have a valid URL)
        if target_url:
            self._extract_youtube_comments(target_url)
        else:
            print(f"[{self.name}] ❌ Could not find ANY Atomberg video to analyze.")

    def _extract_youtube_comments(self, url):
        try:
            # Fix Shorts URL if needed
            if "youtube.com/shorts/" in url:
                url = url.replace("youtube.com/shorts/", "youtube.com/watch?v=")

            self.driver.get(url)
            wait = WebDriverWait(self.driver, 20)
            new_comments = []

            print(f"[{self.name}] Triggering YouTube comments...")
            # Jitter Scroll to wake up YouTube
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, 2500);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 600);") 
            
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytd-comment-thread-renderer")))
                comments = self.driver.find_elements(By.TAG_NAME, "ytd-comment-thread-renderer")
                
                for c in comments[:15]:
                    try:
                        t = c.find_element(By.ID, "content-text").text
                        new_comments.append({"text": t, "source": "YouTube Comment"})
                    except: continue
            except:
                print(f"[{self.name}] Comments timed out.")

            if new_comments:
                self.deep_memory = pd.DataFrame(new_comments)
                print(f"[{self.name}] ✅ Extracted {len(new_comments)} comments.")
            else:
                print(f"[{self.name}] ⚠️ No comments found.")
                
        except Exception as e: print(f"Extraction Error: {e}")
    # --- PHASE 3: REPORTING ---
    def _analyze_memory(self):
        if "entity" not in self.memory.columns:
            results = []
            for _, row in self.memory.iterrows():
                res = self.brain.analyze(row['text'])
                results.append({**row, **res})
            self.memory = pd.DataFrame(results)

    def generate_final_report(self):
        if self.memory.empty:
            print(f"[{self.name}] ⚠️ No data collected.")
            return
        
        print(f"\n[{self.name}] 📝 Generating Reports...")
        self._analyze_memory()
        df = self.memory
        
        # Metrics
        df['log_impact'] = np.log1p(df['metrics'])
        total_impact = df['log_impact'].sum()
        atomberg_impact = df[df['entity']=="ATOMBERG"]['log_impact'].sum()
        sov = (atomberg_impact / total_impact * 100) if total_impact > 0 else 0
        
        # Risk
        top_metric = df['metrics'].max()
        risk = "HIGH" if (top_metric / df['metrics'].sum()) > 0.4 else "LOW"

        # Generate MD
        report = f"""
# Market Intelligence Report: Atomberg
**Date:** {time.strftime("%Y-%m-%d")} | **Agent:** {self.name}

## 1. Executive Summary
* **Global Share of Voice:** {sov:.2f}%
* **Viral Dependency Risk:** {risk}
* **Total Posts Scanned:** {len(df)}

## 2. Platform Breakdown
* **YouTube:** {len(df[df['source']=='YouTube'])} posts
* **X (Twitter):** {len(df[df['source']=='X'])} posts

## 3. Strategic Insights (Voice of Customer)
"""
        if not self.deep_memory.empty:
            txt = " ".join(self.deep_memory['text'].tolist()).lower()
            if "price" in txt or "cost" in txt: report += "* **💰 Pricing:** Users discuss affordability vs features.\n"
            if "remote" in txt or "app" in txt: report += "* **📱 Tech:** High interest in App/Remote reliability.\n"
            if "noise" in txt or "sound" in txt: report += "* **⚠️ Quality:** Some concerns regarding motor noise/wobble.\n"
            if "service" in txt: report += "* **🛠️ Service:** Queries about after-sales support availability.\n"
        else:
            report += "* *No qualitative data extracted.*"

        with open("Atomberg_Report.md", "w", encoding="utf-8") as f:
            f.write(report)
            
        # Save JSONs
        df.to_json("atomberg_feed_data.json", orient="records", indent=4)
        if not self.deep_memory.empty:
            self.deep_memory.to_json("atomberg_comments_data.json", orient="records", indent=4)
            
        print(f"[{self.name}] ✅ SUCCESS. Files saved: Atomberg_Report.md, atomberg_feed_data.json")

    def shutdown(self):
        if self.driver: 
            try: self.driver.quit()
            except: pass

if __name__ == "__main__":
    agent = AtombergMarketingAgent()
    try:
        agent.scan_youtube("smart fan review", limit_n=10)
        agent.scan_twitter("smart fan", limit_n=10)
        agent.deep_dive_best_content()
        agent.generate_final_report()
    finally:
        agent.shutdown()