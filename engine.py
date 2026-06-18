import urllib.request
import json
import time

def calculate_liquidity_risk(ticker_symbol):
    """
    Pure Python API version - Zero dependencies. 
    Compatible with Python 3.14+ out of the box.
    """
    ticker = ticker_symbol.upper().strip()
    
    # Direct raw request to Yahoo Finance public chart API
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=60d&interval=1d"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        volumes = result['indicators']['quote'][0]['volume']
        
        # Filter out any null data points
        valid_data = [(c, v) for c, v in zip(closes, volumes) if c is not None and v is not None]
        
        if len(valid_data) < 15:
            return {"error": f"Insufficient liquidity history for '{ticker}'."}
            
    except Exception as e:
        return {"error": f"Could not connect to liquidity pipelines: {str(e)}"}

    # Calculate Dollar Volume streams (Price * Volume)
    dollar_volumes = [c * v for c, v in valid_data]
    
    latest_close = valid_data[-1][0]
    latest_vol = dollar_volumes[-1]
    
    # Calculate Rolling Average using trailing 14 periods
    trailing_14 = dollar_volumes[-15:-1]
    avg_vol = sum(trailing_14) / len(trailing_14) if trailing_14 else latest_vol
    
    # Core Abstraction Logic
    volume_deficit_ratio = latest_vol / avg_vol if avg_vol > 0 else 1.0
    
    if volume_deficit_ratio < 0.70:
        calculated_risk = 0.84 
        verdict = "EVAPORATING. Price is running on thin air. Institutional volume has left the building."
    elif volume_deficit_ratio < 0.85:
        calculated_risk = 0.52
        verdict = "DRYING UP. Capital momentum is slowing down."
    else:
        calculated_risk = 0.18
        verdict = "HIGH HUMIDITY. Strong, healthy capital flows backing current levels."

    safety_score = int((1 - calculated_risk) * 100)

    return {
        "Ticker": ticker,
        "Current Price": f"${round(latest_close, 2)}",
        "Liquidity Risk Score": f"{int(calculated_risk * 100)}%",
        "Safety Index": f"{safety_score}%",
        "Engine Verdict": verdict
    }
