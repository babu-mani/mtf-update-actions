import requests
import zipfile
import io
import pandas as pd
import time
import os
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.patches as patches
import tweepy

# --- CONFIGURATION & STYLE ---
COLORS = {
    'bg': '#111827',
    'card_bg': '#1F2937',
    'title': '#F9FAFB',
    'subtitle': '#9CA3AF',
    'text': '#E5E7EB',
    'accent': '#3B82F6',
    'positive': '#10B981',
    'negative': '#F43F5E',
    'border': '#4B5563',
    'bright_text': '#F3F4F6',
    'header_strip': '#374151'
}

# --- FONT SETUP ---
FONT_DIR = "." 
FONT_REGULAR = os.path.join(FONT_DIR, 'Inter-Regular.ttf')
FONT_BOLD = os.path.join(FONT_DIR, 'Inter-Bold.ttf')

try:
    prop_regular = fm.FontProperties(fname=FONT_REGULAR) if os.path.exists(FONT_REGULAR) else fm.FontProperties()
    prop_bold = fm.FontProperties(fname=FONT_BOLD) if os.path.exists(FONT_BOLD) else fm.FontProperties(weight='bold')
except:
    prop_regular = fm.FontProperties()
    prop_bold = fm.FontProperties(weight='bold')

STYLE = {
    'fig_title': {'fontproperties': prop_bold, 'fontsize': 36, 'color': COLORS['title']},
    'fig_subtitle': {'fontproperties': prop_regular, 'fontsize': 16, 'color': COLORS['subtitle']},
    'card_title': {'fontproperties': prop_regular, 'fontsize': 14, 'color': COLORS['subtitle']},
    'card_value': {'fontproperties': prop_bold, 'fontsize': 24, 'color': COLORS['bright_text']},
    'section_header': {'fontproperties': prop_bold, 'fontsize': 18, 'color': COLORS['accent']},
    'watermark': {'fontproperties': prop_regular, 'fontsize': 12, 'color': '#D1D5DB', 'alpha': 0.7}
}

# --- TWITTER BOT LOGIC ---
def post_to_twitter(image_path, date_str, data):
    print("🐦 Attempting to tweet...")
    
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("⚠️ Twitter keys not found in environment. Skipping Tweet.")
        return

    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        
        media = api.media_upload(filename=image_path)
        
        client = tweepy.Client(consumer_key=api_key, consumer_secret=api_secret,
                               access_token=access_token, access_token_secret=access_secret)
        
        # --- NEW TWEET TEXT FORMAT ---
        net_sign = "+" if data['net'] >= 0 else ""
        
        tweet_text = (
            f"MTF (Margin Trading) Insights | {date_str}\n\n"
            f"Net Margin Book Added: ₹{net_sign}{data['net']:,.2f} Cr\n"
            f"Margin Positions Added: ₹{data['added']:,.2f} Cr\n"
            f"Margin Positions Liquidated: ₹-{data['liquidated']:,.2f} Cr\n"
            f"Industry Margin (MTF) Book: ₹{data['industry_book']:,.2f} Cr\n\n"
            f"#MTF #MarginTrading #Nifty #BankNifty #StockMarket"
        )
        # -----------------------------

        client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        print("✅ Tweet posted successfully!")
        
    except Exception as e:
        print(f"❌ Failed to tweet: {e}")

# --- FETCHER LOGIC ---
def get_robust_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.nseindia.com/'
    })
    try:
        session.get("https://www.nseindia.com/", timeout=5)
    except:
        pass
    return session

def fetch_mtf_data(url, date_display):
    session = get_robust_session()
    try:
        print(f"🔍 Checking {date_display} ... ", end="")
        response = session.get(url, timeout=20)
        if response.status_code == 404:
            print("❌ (No Data)")
            return None
        response.raise_for_status()
        print("✅ Found! Processing...")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_filename = [f for f in z.namelist() if f.lower().endswith('.csv')][0]
            with z.open(csv_filename) as f:
                content = f.read()
                
                # Part 1: Summary
                df_summary = pd.read_csv(io.BytesIO(content), header=None, nrows=20)
                def get_val(keyword):
                    row = df_summary[df_summary[1].str.contains(keyword, na=False, case=False)]
                    if not row.empty:
                        return float(str(row.iloc[0, 2]).replace(',', '').strip()) / 100
                    return 0.0

                data = {
                    'added': get_val("Fresh Exposure"),
                    'liquidated': get_val("Exposure liquidated"),
                    'industry_book': get_val("Net scripwise outstanding")
                }
                data['net'] = data['added'] - data['liquidated']
                
                # Part 2: Details
                csv_text = content.decode('utf-8', errors='ignore').splitlines()
                header_idx = -1
                for i, line in enumerate(csv_text):
                    if "Symbol" in line and "Qty" in line:
                        header_idx = i
                        break
                
                top_adds_val = []
                top_adds_vol = []
                
                if header_idx != -1:
                    df = pd.read_csv(io.BytesIO(content), skiprows=header_idx)
                    df.columns = [c.strip() for c in df.columns]
                    col_symbol = next((c for c in df.columns if "Symbol" in c), "Symbol")
                    col_amt = next((c for c in df.columns if "Amt" in c and "Fin" in c), None)
                    col_qty = next((c for c in df.columns if "Qty" in c and "Fin" in c), None)

                    if col_amt:
                        df_val = df.sort_values(by=col_amt, ascending=False).head(10)
                        for _, row in df_val.iterrows():
                            top_adds_val.append((row[col_symbol], row[col_amt]/100))

                    if col_qty:
                        df_vol = df.sort_values(by=col_qty, ascending=False).head(10)
                        for _, row in df_vol.iterrows():
                            top_adds_vol.append((row[col_symbol], row[col_qty]))

                data['top_val'] = top_adds_val
                data['top_vol'] = top_adds_vol
                return data

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

# --- VISUALIZATION ENGINE ---
def create_dashboard(data, date_str):
    fig = plt.figure(figsize=(16, 9), facecolor=COLORS['bg'])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    
    # 1. Header
    fig.text(0.05, 0.92, "MTF Market Insights", ha='left', **STYLE['fig_title'])
    fig.text(0.05, 0.88, f"Margin Trading Funding Analysis | {date_str}", ha='left', **STYLE['fig_subtitle'])
    
    # 2. KPI Cards
    card_y = 0.68
    card_h = 0.15
    card_w = 0.20
    gap = 0.03
    start_x = 0.05

    kpis = [
        ("Positions Added", f"₹{data['added']:,.2f} Cr", COLORS['positive']),
        ("Positions Liquidated", f"₹{data['liquidated']:,.2f} Cr", COLORS['negative']),
        ("Net Book Added", f"{'+' if data['net']>=0 else ''}₹{data['net']:,.2f} Cr", COLORS['positive'] if data['net']>=0 else COLORS['negative']),
        ("Total Industry Book", f"₹{data['industry_book']:,.2f} Cr", COLORS['accent'])
    ]

    for i, (title, val, color) in enumerate(kpis):
        x = start_x + i*(card_w + gap)
        rect = patches.FancyBboxPatch((x, card_y), card_w, card_h, boxstyle="round,pad=0.02", fc=COLORS['card_bg'], ec='none')
        ax.add_patch(rect)
        fig.text(x + card_w/2, card_y + card_h - 0.04, title, ha='center', **STYLE['card_title'])
        fig.text(x + card_w/2, card_y + 0.05, val, ha='center', fontproperties=prop_bold, fontsize=22, color=color)

    # 3. Tables Section
    table_y_top = 0.60
    col1_x = 0.05
    col2_x = 0.52
    
    fig.text(col1_x, table_y_top, "Top 10 MTF Additions (By Value)", **STYLE['section_header'])
    y_curr = table_y_top - 0.06
    row_height = 0.045 
    
    for idx, (sym, val) in enumerate(data['top_val']):
        bg_col = COLORS['card_bg'] if idx % 2 == 0 else COLORS['bg']
        rect = patches.Rectangle((col1_x, y_curr-0.01), 0.40, row_height, fc=bg_col)
        ax.add_patch(rect)
        fig.text(col1_x + 0.02, y_curr + 0.01, f"{idx+1}. {sym}", fontproperties=prop_regular, fontsize=15, color=COLORS['text'])
        fig.text(col1_x + 0.38, y_curr + 0.01, f"₹{val:,.1f} Cr", fontproperties=prop_bold, fontsize=15, color=COLORS['positive'], ha='right')
        y_curr -= (row_height + 0.005)

    fig.text(col2_x, table_y_top, "Top 10 Volume Buzzers (By Qty)", **STYLE['section_header'])
    y_curr = table_y_top - 0.06
    
    for idx, (sym, qty) in enumerate(data['top_vol']):
        bg_col = COLORS['card_bg'] if idx % 2 == 0 else COLORS['bg']
        rect = patches.Rectangle((col2_x, y_curr-0.01), 0.40, row_height, fc=bg_col)
        ax.add_patch(rect)
        qty_str = f"{qty/1000000:.1f}M" if qty > 1000000 else f"{qty/1000:.0f}K"
        fig.text(col2_x + 0.02, y_curr + 0.01, f"{idx+1}. {sym}", fontproperties=prop_regular, fontsize=15, color=COLORS['text'])
        fig.text(col2_x + 0.38, y_curr + 0.01, qty_str, fontproperties=prop_bold, fontsize=15, color=COLORS['accent'], ha='right')
        y_curr -= (row_height + 0.005)

    # 4. Watermark
    watermark_text = f"@ChartWizMani | Data as of {date_str} | For Informational Use Only"
    fig.text(0.98, 0.02, watermark_text, ha='right', va='bottom', **STYLE['watermark'])

    # Save
    os.makedirs("MTF_Images", exist_ok=True)
    filename = f"MTF_Images/MTF_Dashboard_{date_str.replace('-','_')}.png"
    plt.savefig(filename, dpi=150, facecolor=COLORS['bg'], bbox_inches='tight')
    plt.close()
    print(f"🖼️ Dashboard saved: {filename}")
    
    # --- UPDATED CALL ---
    post_to_twitter(filename, date_str, data) # Added data here

# --- MAIN ---
def main():
    print("🚀 Starting MTF Visualizer...")
    time.sleep(3) 

    found = False
    for days_ago in range(7):
        target_date = datetime.now() - timedelta(days=days_ago)
        date_url = target_date.strftime("%d%m%y")
        date_display = target_date.strftime("%d-%b-%Y")
        url = f"https://nsearchives.nseindia.com/content/equities/mrg_trading_{date_url}.zip"
        
        data = fetch_mtf_data(url, date_display)
        if data:
            create_dashboard(data, date_display)
            found = True
            break
            
    if not found:
        print("❌ No data found in last 7 days.")

if __name__ == "__main__":
    main()
