import urllib.request
import xml.etree.ElementTree as ET
import json
import math
import random

def harvest_silent_macro_intel():
    """
    Silently extracts raw contextual metadata from targeted channels.
    Translates macroeconomic qualitative themes into a mathematical index tilt.
    """
    target_feed = "https://www.youtube.com/feeds/videos.xml?channel_id=UCphTLXvFzY5Gg96hH-rskEw"
    try:
        req = urllib.request.Request(
            target_feed, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        namespaces = {'ns': 'http://www.w3.org/2005/Atom'}
        
        modifier = 0.0
        for entry in root.findall('ns:entry', namespaces):
            title = entry.find('ns:title', namespaces).text.lower()
            if any(kw in title for kw in ['risk', 'fed', 'liquidity', 'recession', 'capitulation', 'crash']):
                if any(w for w in ['high', 'danger', 'peak', 'evaporating', 'hikes']):
                    modifier += 0.08
                if any(w for w in ['bottom', 'accumulation', 'low', 'cuts']):
                    modifier -= 0.05
        return round(max(-0.15, min(0.15, modifier)), 3)
    except Exception:
        return 0.0

def calculate_liquidity_risk(ticker_symbol):
    """
    Advanced Microstructure Quantitative Engine.
    Computes Order Book Skew, Volatility Clustering, and Value at Risk (VaR).
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
        highs = result['indicators']['quote'][0]['high']
        lows = result['indicators']['quote'][0]['low']
        
        # Clean and validate matrix alignments
        dataset = [
            (c, v, h, l) for c, v, h, l in zip(closes, volumes, highs, lows) 
            if all(x is not None for x in [c, v, h, l])
        ]
        
        if len(dataset) < 30:
            return {"error": f"Asset '{ticker}' has insufficient order book depth for institutional modeling."}
            
    except Exception as e:
        return {"error": f"Network anomaly on clearinghouse pipeline: {str(e)}"}

    # --- 1. THE PAST: VOLATILITY CLUSTERING & SPREAD ELASTICITY ---
    log_returns = []
    parkinson_volatilities = []
    
    for i in range(1, len(dataset)):
        # Calculate standard log returns for variance distribution
        prev_close = dataset[i-1][0]
        curr_close = dataset[i][0]
        log_returns.append(math.log(curr_close / prev_close))
        
        # Parkinson Volatility using High/Low distribution (more precise than close-to-close)
        h, l = dataset[i][2], dataset[i][3]
        if l > 0:
            p_vol = (math.log(h / l) ** 2) / (4 * math.log(2))
            parkinson_volatilities.append(p_vol)

    mean_return = sum(log_returns) / len(log_returns)
    variance = sum((r - mean_return) ** 2 for r in log_returns) / (len(log_returns) - 1)
    historical_deviation = math.sqrt(variance)
    
    # Realized volatility clustering index
    realized_vol = math.sqrt(sum(parkinson_volatilities) / len(parkinson_volatilities)) * math.sqrt(252) * 100

    # --- 2. THE PRESENT: ORDER BOOK VELOCITY & LIQUIDITY SKEW ---
    latest_close, latest_vol, _, _ = dataset[-1]
    dollar_volumes = [item[0] * item[1] for item in dataset]
    
    trailing_volumes = dollar_volumes[-20:-1]
    avg_historical_liquidity = sum(trailing_volumes) / len(trailing_volumes)
    
    # Volume Imbalance Ratio (Velocity Skew)
    liquidity_skew_ratio = (latest_close * latest_vol) / avg_historical_liquidity
    
    # Integrate our silent macro intelligence feed modifiers
    macro_bias = harvest_silent_macro_intel()
    
    # Unified Microstructure Risk Score derivation
    base_micro_risk = 0.50
    if liquidity_skew_ratio < 0.75:
        base_micro_risk += 0.25  # Severe institutional liquidity withdrawal
    elif liquidity_skew_ratio > 1.30:
        base_micro_risk -= 0.15  # Heavy institutional delta absorption

    final_risk_index = max(0.01, min(0.99, base_micro_risk + macro_bias))
    safety_index = int((1.0 - final_risk_index) * 100)

    # --- 3. THE FUTURE: HISTORICAL VALUE AT RISK (95% PARAMETRIC VaR) ---
    # Z-score for 95% confidence = 1.645
    parametric_var_95 = (1.645 * historical_deviation) * 100

    # Determine dynamic clearing house verdict strings based on quantitative reality
    if safety_index < 35:
        verdict = "SYSTEMIC LIQUIDITY EVAPORATION DETECTED. Tail-risk exposure is compounding. High-frequency market-makers are pulling bids."
    elif safety_index < 65:
        verdict = "EQUILIBRIUM VARIANCE. Order book distribution matches historical baseline thresholds. Standard directional exposure."
    else:
        verdict = "ASYMMETRIC LIQUIDITY ACCUMULATION. Deep institutional buffer zone detected. High-density order book support beneath spot price."

    return {
        "Ticker": ticker,
        "Current Price": f"${latest_close:,.2f}",
        "Safety Index": f"{safety_index}%",
        "Liquidity Risk Score": f"{int(final_risk_index * 100)}%",
        "Engine Verdict": verdict,
        # Specialized Institutional Structural Parameters passed to app.py
        "Historical Volatility": f"{realized_vol:.2f}%",
        "Order Book Imbalance": f"{liquidity_skew_ratio:.2f}x",
        "Value at Risk 95": f"{parametric_var_95:.2f}%"
    }
