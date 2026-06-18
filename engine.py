import urllib.request
import xml.etree.ElementTree as ET
import json
import time

def harvest_silent_macro_intel():
    """
    Silently extracts raw context metadata from targeted public feeds.
    Runs entirely on the server side with zero user exposure.
    """
    target_feed = "https://www.youtube.com/feeds/videos.xml?channel_id=UCphTLXvFzY5Gg96hH-rskEw"
    try:
        req = urllib.request.Request(
            target_feed, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        namespaces = {'ns': 'http://www.w3.org/2005/Atom'}
        
        modifier = 0.0
        match_count = 0
        
        for entry in root.findall('ns:entry', namespaces):
            title = entry.find('ns:title', namespaces).text.lower()
            
            # Scrape and translate specific technical vocabulary markers
            if any(kw in title for kw in ['risk', 'liquidity', 'fed', 'recession', 'cycle', 'band', 'capitulation']):
                match_count += 1
                if any(w for w in ['high', 'danger', 'peak', 'evaporating']):
                    modifier += 0.10
                if any(w for w in ['bottom', 'accumulation', 'low']):
                    modifier -= 0.08
                    
        # Normalize the modifier impact cap
        return round(max(-0.20, min(0.20, modifier)), 2)
    except Exception:
        # Seamless silent fallback if web request times out
        return 0.0

def calculate_liquidity_risk(ticker_symbol):
    """
    Analyzes Volume-Weighted Capital Momentum fused seamlessly with 
    our proprietary, white-labeled macro intelligence tilt layer.
    """
    ticker = ticker_symbol.upper().strip()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=60d&interval=1d"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        volumes = result['indicators']['quote'][0]['volume']
        
        valid_data = [(c, v) for c, v in zip(closes, volumes) if c is not None and v is not None]
        
        if len(valid_data) < 15:
            return {"error": f"Insufficient liquidity history for '{ticker}'."}
            
    except Exception as e:
        return {"error": f"Could not connect to liquidity pipelines: {str(e)}"}

    # Compute Core Data Stream Maths
    dollar_volumes = [c * v for c, v in valid_data]
    latest_close = valid_data[-1][0]
    latest_vol = dollar_volumes[-1]
    
    trailing_14 = dollar_volumes[-15:-1]
    avg_vol = sum(trailing_14) / len(trailing_14) if trailing_14 else latest_vol
    
    volume_deficit_ratio = latest_vol / avg_vol if avg_vol > 0 else 1.0
    
    # 1. Establish baseline risk from hard exchange volume parameters
    if volume_deficit_ratio < 0.70:
        base_risk = 0.80 
        verdict_slug = "EVAPORATING. Price velocity is running on thin air. Institutional order blocks have thinned."
    elif volume_deficit_ratio < 0.85:
        base_risk = 0.50
        verdict_slug = "DRYING UP. Capital momentum is observing deceleration patterns."
    else:
        base_risk = 0.20
        verdict_slug = "HIGH HUMIDITY. Strong, healthy capital flows backing current structural levels."

    # 2. Extract our hidden sentiment tilt factor from the channel analysis
    # This happens completely anonymously behind the scenes
    macro_tilt = harvest_silent_macro_intel()
    
    # 3. Fuse the layers together into your proprietary unified rating
    final_risk_score = max(0.05, min(0.95, base_risk + macro_tilt))
    safety_score = int((1 - final_risk_score) * 100)

    return {
        "Ticker": ticker,
        "Current Price": f"${round(latest_close, 2)}",
        "Liquidity Risk Score": f"{int(final_risk_score * 100)}%",
        "Safety Index": f"{safety_score}%",
        "Engine Verdict": verdict_slug
    }
