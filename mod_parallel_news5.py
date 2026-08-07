import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import json
import os

# Ρύθμιση σελίδας
st.set_page_config(
    page_title="News Dashboard - Iframe + Scraping",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    .news-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        height: 650px;
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
    }
    .news-card h4 {
        color: #1e3c72;
        border-bottom: 2px solid #1e3c72;
        padding-bottom: 8px;
        margin-top: 0;
        flex-shrink: 0;
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .news-card h4 a {
        color: #1e3c72;
        text-decoration: none;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .news-card h4 a:hover {
        color: #ff6b35;
        text-decoration: underline;
    }
    .news-card .iframe-wrapper {
        flex: 2;
        min-height: 250px;
        border-radius: 5px;
        overflow: hidden;
        background-color: #f5f5f5;
        margin-bottom: 10px;
    }
    .news-card .iframe-wrapper iframe {
        width: 100%;
        height: 100%;
        border: none;
    }
    .news-card .articles-list {
        flex: 1;
        overflow-y: auto;
        max-height: 200px;
        padding: 5px 0;
    }
    .news-item {
        padding: 6px 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 12px;
    }
    .news-item a {
        color: #1e3c72;
        text-decoration: none;
        font-weight: 500;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .news-item a:hover {
        color: #ff6b35;
        text-decoration: underline;
    }
    .stButton button {
        width: 100%;
        background-color: #1e3c72;
        color: white;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #ff6b35;
    }
    .no-articles {
        color: #6c757d;
        text-align: center;
        padding: 20px;
        font-style: italic;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ΟΙ ΠΗΓΕΣ ΣΟΥ
# ============================================
BASE_SOURCES_DATA = [
    
     # Greek News
    {"name": "Πρώτο Θέμα", "category": "news", "subcategory": "general", "url": "https://www.protothema.gr/"},
    {"name": "in.gr", "category": "news", "subcategory": "general", "url": "https://www.in.gr/"},
    {"name": "Καθημερινή", "category": "news", "subcategory": "general", "url": "https://www.kathimerini.gr/"},
    {"name": "Newsit", "category": "news", "subcategory": "general", "url": "https://www.newsit.gr/"},
    {"name": "News247", "category": "news", "subcategory": "general", "url": "https://www.news247.gr/"},
    {"name": "Capital", "category": "news", "subcategory": "general", "url": "https://www.capital.gr/"},
    {"name": "CNN Greece", "category": "news", "subcategory": "general", "url": "https://www.cnn.gr/"},
    {"name": "Documento", "category": "news", "subcategory": "general", "url": "https://www.documentonews.gr"},
    {"name": "iefimerida", "category": "news", "subcategory": "general", "url": "https://www.iefimerida.gr"},
    {"name": "Zougla", "category": "news", "subcategory": "general", "url": "https://www.zougla.gr/"},
    {"name": "Rizospastis", "category": "news", "subcategory": "general", "url": "https://www.rizospastis.gr/"},
    {"name": "902", "category": "news", "subcategory": "general", "url": "https://www.902.gr/"},
    {"name": "Εφημερίδα Συντακτών", "category": "news", "subcategory": "general", "url": "https://www.efsyn.gr"},
    {"name": "ieidiseis", "category": "news", "subcategory": "general", "url": "https://www.ieidiseis.gr"},
    {"name": "Ναυτεμπορική", "category": "news", "subcategory": "general", "url": "https://www.naftemporiki.gr/"},
    {"name": "Megatv", "category": "news", "subcategory": "general", "url": "https://www.megatv.com/live/"},
    {"name": "Ant1", "category": "news", "subcategory": "general", "url": "https://www.antenna.gr/live"},
    {"name": "Opentv", "category": "news", "subcategory": "general", "url": "https://www.tvopen.gr/live"},
        
    
    # International - Geopolitics
    {"name": "Atlantic Council", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.atlanticcouncil.org/"},
    {"name": "Axios", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.axios.com/"},
    {"name": "Al Jazeera", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.aljazeera.com/"},
    {"name": "People's Daily", "category": "international sources", "subcategory": "china", "url": "http://en.people.cn/index.html"},
    {"name": "PressReader", "category": "international sources", "subcategory": "global news", "url": "https://www.pressreader.com/"},
    {"name": "Reuters World", "category": "international sources", "subcategory": "global news", "url": "https://www.reuters.com/"},
    {"name": "BBC Monitoring – Global News", "category": "international sources", "subcategory": "global news", "url": "https://monitoring.bbc.co.uk/"},
    {"name": "Al Jazeera | Crisis Zones", "category": "international sources", "subcategory": "crisis zones", "url": "https://www.aljazeera.com/news/crisis/"},
    {"name": "eDoTourkia", "category": "international sources", "subcategory": "turkey", "url": "https://edotourkia.gr/el/"},
    {"name": "The Cradle", "category": "international sources", "subcategory": "geopolitics", "url": "https://new.thecradle.co/"},
    {"name": "Foreign Affairs", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.foreignaffairs.com/"},
    {"name": "Bloomberg Geopolitics", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.bloomberg.com/politics"},
    {"name": "NATO", "category": "international sources", "subcategory": "geopolitics", "url": "https://www.nato.int/"},

    
    # International - West
    {"name": "CNN", "category": "international sources", "subcategory": "west", "url": "https://edition.cnn.com"},
    {"name": "BBC", "category": "international sources", "subcategory": "west", "url": "https://www.bbc.com/news"},
    {"name": "Reuters World", "category": "international sources", "subcategory": "west", "url": "https://www.reuters.com/news/world"},
    
    # International - Eurasia
    {"name": "Al Jazeera", "category": "international sources", "subcategory": "Eurasia", "url": "https://www.aljazeera.com/"},
    {"name": "CGTN", "category": "international sources", "subcategory": "Eurasia", "url": "https://www.cgtn.com/"},
    {"name": "BRICS Affairs Greece", "category": "international sources", "subcategory": "Eurasia", "url": "https://bricsaffairs.gr/"},
    
    # International - Osint
    {"name": "RAND", "category": "international sources", "subcategory": "Osint", "url": "https://www.rand.org"},
    
    
    # Global Economy
    {"name": "IMF", "category": "global economy", "subcategory": "think tanks", "url": "https://www.imf.org/en/Home"},
    {"name": "World Bank", "category": "global economy", "subcategory": "think tanks", "url": "https://www.worldbank.org/en/home"},
    {"name": "OECD", "category": "global economy", "subcategory": "think tanks", "url": "https://www.oecd.org/"},
    {"name": "Brookings", "category": "global economy", "subcategory": "think tanks", "url": "https://www.brookings.edu"},
    {"name": "MarketWatch", "category": "global economy", "subcategory": "general", "url": "https://www.marketwatch.com/"},
    
    # Greek Economy
    {"name": "ΙΟΒΕ", "category": "economy", "subcategory": "organizations", "url": "http://iobe.gr"},
    {"name": "Τράπεζα της Ελλάδος", "category": "economy", "subcategory": "organizations", "url": "https://www.bankofgreece.gr/"},
    {"name": "ΕΛΣΤΑΤ", "category": "economy", "subcategory": "organizations", "url": "https://www.statistics.gr/"},
    {"name": "Οικονομικός Ταχυδρόμος", "category": "economy", "subcategory": "news", "url": "https://www.ot.gr/"},
    
    # Parapolitical
    {"name": "To Vima - Vimatodotis", "category": "parapolitical", "subcategory": "political", "url": "https://www.tovima.gr/editor/vimatodotis/"},
    {"name": "Powergame - Big Mouth", "category": "parapolitical", "subcategory": "political", "url": "https://www.powergame.gr/category/big-mouth/"},
    {"name": "New Money - Dark Room", "category": "parapolitical", "subcategory": "political", "url": "https://www.newmoney.gr/category/dark-room/"},
    {"name": "Kathimerini - Theoreio", "category": "parapolitical", "subcategory": "political", "url": "https://www.kathimerini.gr/columns/theoreio/", "notes": "Η πρόσβαση στο περιεχόμενο απαγορεύτηκε (σφάλμα 403)."},
    {"name": "Kathimerini - Business Talk", "category": "parapolitical", "subcategory": "political", "url": "https://www.kathimerini.gr/columns/business-talk/", "notes": "Η πρόσβαση στο περιεχόμενο απαγορεύτηκε (σφάλμα 403)."},
    {"name": "Newsit - Me to Ganti", "category": "parapolitical", "subcategory": "political", "url": "https://www.newsit.gr/category/blogs/me-to-ganti/"},
    {"name": "Newsit - Apocryptografos", "category": "parapolitical", "subcategory": "political", "url": "https://www.newsit.gr/category/blogs/apocryptografos/", "notes": "Το περιεχόμενο που ανακτήθηκε ήταν κυρίως ένα μήνυμα συγκατάθεσης για cookies."},
    {"name": "Naftemporiki - Paraskiniaka", "category": "parapolitical", "subcategory": "political", "url": "https://www.naftemporiki.gr/paraskiniaka/"}

]

CUSTOM_SOURCES_FILE = "custom_sources.json"

def load_custom_sources():
    if os.path.exists(CUSTOM_SOURCES_FILE):
        try:
            with open(CUSTOM_SOURCES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_custom_sources(custom_sources):
    with open(CUSTOM_SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_sources, f, ensure_ascii=False, indent=2)

def get_all_sources():
    custom = load_custom_sources()
    return BASE_SOURCES_DATA + custom

def extract_articles(url, source_name, max_articles=10):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if len(text) > 30 and not text.startswith('http'):
                if href.startswith('/'):
                    full_url = url.rstrip('/') + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                clean_text = re.sub(r'\s+', ' ', text).strip()
                
                if len(clean_text) > 20:
                    articles.append({
                        'title': clean_text[:100],
                        'url': full_url,
                        'source': source_name
                    })
                    
                    if len(articles) >= max_articles:
                        break
        
        return articles[:max_articles]
        
    except Exception as e:
        return []

def get_categories(all_sources):
    categories = set()
    for item in all_sources:
        categories.add(item['category'])
    return sorted(list(categories))

def get_sources_by_category(all_sources, category):
    return [item for item in all_sources if item['category'] == category]

def main():
    st.title("📰 Taz's News Dashboard")
    st.caption("💡 Πατήστε στον τίτλο της πηγής για να ανοίξει η ιστοσελίδα σε νέο παράθυρο")

    with st.expander("🎙️ Επιλογή Ραδιοφώνου Live", expanded=True):
        radio_stations = {
            "Real FM 97.8": "realfm",
            "Παραπολιτικά FM 90.1": "1986",
            "ERTnews Radio 105.8": "2073",
            "ΣΚΑΪ 100.3": "1334",
        }
        
        selected_station_name = st.selectbox(
            "Επιλέξτε σταθμό:",
            options=list(radio_stations.keys()),
            index=0,
            key="radio_station_selector"
        )
        
        station_id = radio_stations[selected_station_name]
        
        if station_id == "realfm":
            radio_url = "https://live24.gr/radio/realfm"
        else:
            radio_url = f"https://live24.gr/radio/generic.jsp?sid={station_id}"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 10px; padding: 10px; margin-bottom: 15px;">
            <iframe src="{radio_url}" 
                    style="width: 100%; max-width: 600px; height: 120px; border: none; border-radius: 8px;" 
                    allow="autoplay; encrypted-media">
            </iframe>
        </div>
        <p style="text-align: center; color: #6c757d; font-size: 0.8rem;">
            Ραδιόφωνο από το <a href="{radio_url}" target="_blank">live24.gr</a> | {selected_station_name}
        </p>
        """, unsafe_allow_html=True)
    
    all_sources = get_all_sources()
    categories = get_categories(all_sources)
    
    if 'selected_category' not in st.session_state:
       if "news" in categories:
            st.session_state.selected_category = "news"
       else:
            st.session_state.selected_category = categories[0] if categories else ""
    
    if 'news_data' not in st.session_state:
        st.session_state.news_data = {}
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    
    if 'auto_load_done' not in st.session_state:
        st.session_state.auto_load_done = False
    
    with st.sidebar:
        st.markdown("### 📋 Πίνακας Ελέγχου")
        
        selected_category = st.selectbox(
            "Επιλέξτε Κατηγορία:",
            categories,
            index=categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0
        )
        
        if selected_category != st.session_state.selected_category:
            st.session_state.selected_category = selected_category
            st.session_state.auto_load_done = False
            st.session_state.news_data = {}
        
        category_sources = get_sources_by_category(all_sources, selected_category)
        st.info(f"📊 {len(category_sources)} πηγές στην κατηγορία '{selected_category}'")
        
        if st.button("🔄 Ανανέωση Όλων", use_container_width=True):
            with st.spinner(f"Φόρτωση {len(category_sources)} πηγών..."):
                news_dict = {}
                progress_bar = st.progress(0)
                
                for idx, source in enumerate(category_sources):
                    url = source['url']
                    if url:
                        articles = extract_articles(url, source['name'], 10)
                        news_dict[source['name']] = articles
                    if len(category_sources) > 0:
                        progress_bar.progress((idx + 1) / len(category_sources))
                
                st.session_state.news_data = news_dict
                st.session_state.last_update = datetime.now()
                st.session_state.auto_load_done = True
                st.success(f"✅ Ανανεώθηκαν {len(category_sources)} πηγές!")
                time.sleep(1)
                st.rerun()
        
        if not st.session_state.auto_load_done and category_sources:
            with st.spinner(f"Αυτόματη φόρτωση {len(category_sources)} πηγών..."):
                news_dict = {}
                for source in category_sources:
                    url = source['url']
                    if url:
                        articles = extract_articles(url, source['name'], 10)
                        news_dict[source['name']] = articles
                st.session_state.news_data = news_dict
                st.session_state.last_update = datetime.now()
                st.session_state.auto_load_done = True
                st.rerun()
        
        if st.session_state.last_update:
            st.info(f"🕐 Τελευταία ενημέρωση: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### ➕ Προσθήκη Νέας Πηγής")
        
        with st.form("add_source_form"):
            new_name = st.text_input("Όνομα πηγής:")
            new_url = st.text_input("URL (με http:// ή https://):")
            new_category = st.selectbox("Κατηγορία:", categories + ["Νέα κατηγορία..."])
            
            if new_category == "Νέα κατηγορία...":
                new_category = st.text_input("Όνομα νέας κατηγορίας:")
            
            new_subcategory = st.text_input("Υποκατηγορία (προαιρετικό):", "")
            
            submitted = st.form_submit_button("➕ Προσθήκη Πηγής")
            
            if submitted and new_name and new_url:
                if not new_url.startswith(("http://", "https://")):
                    st.error("❌ Το URL πρέπει να ξεκινά με http:// ή https://")
                elif new_category and new_category != "Νέα κατηγορία...":
                    new_source = {
                        "name": new_name,
                        "category": new_category,
                        "subcategory": new_subcategory if new_subcategory else "general",
                        "url": new_url
                    }
                    
                    custom_sources = load_custom_sources()
                    custom_sources.append(new_source)
                    save_custom_sources(custom_sources)
                    
                    st.success(f"✅ Προστέθηκε η πηγή: {new_name}")
                    st.session_state.auto_load_done = False
                    st.session_state.news_data = {}
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Συμπληρώστε όλα τα απαραίτητα πεδία")
        
        custom_sources = load_custom_sources()
        if custom_sources:
            st.markdown("---")
            st.markdown("### 🗑️ Διαγραφή Custom Πηγών")
            for i, src in enumerate(custom_sources):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {src['name']} ({src['category']})")
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        custom_sources.pop(i)
                        save_custom_sources(custom_sources)
                        st.session_state.auto_load_done = False
                        st.session_state.news_data = {}
                        st.rerun()
        
        st.markdown("---")
        st.caption(f"📊 Σύνολο πηγών: {len(all_sources)}")
    
    # ============================================
    # ΕΜΦΑΝΙΣΗ ΜΕ 3 ΣΤΗΛΕΣ
    # ============================================
    category_sources = get_sources_by_category(all_sources, st.session_state.selected_category)
    
    if category_sources:
        num_sources = len(category_sources)
        num_rows = (num_sources + 2) // 3
        
        for row in range(num_rows):
            cols = st.columns(3)
            
            for col_idx in range(3):
                source_idx = row * 3 + col_idx
                
                if source_idx < num_sources:
                    source = category_sources[source_idx]
                    source_name = source['name']
                    source_url = source['url']
                    articles = st.session_state.news_data.get(source_name, [])
                    
                    with cols[col_idx]:
                        with st.container():
                            # Ο τίτλος είναι τώρα link
                            st.markdown(f"""
                            <div class="news-card">
                                <h4><a href="{source_url}" target="_blank">📰 {source_name}</a></h4>
                                <div class="iframe-wrapper">
                                    <iframe src="{source_url}" 
                                            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                                            loading="lazy">
                                    </iframe>
                                </div>
                                <div class="articles-list">
                            """, unsafe_allow_html=True)
                            
                            if articles:
                                for article in articles[:8]:
                                    title = article['title'][:80] + "..." if len(article['title']) > 80 else article['title']
                                    st.markdown(f"""
                                    <div class="news-item">
                                        <a href="{article['url']}" target="_blank">📌 {title}</a>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="no-articles">
                                    ⏳ Φόρτωση άρθρων...
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Δεν βρέθηκαν πηγές για αυτή την κατηγορία")

if __name__ == "__main__":
    main()
