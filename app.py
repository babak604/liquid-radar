import os
import sys

# Protect the engine from importing yfinance before it's ready
try:
    import yfinance as yf
except ImportError:
    import pip
    pip.main(["install", "yfinance", "pandas", "numpy"])
    import yfinance as yf

import pandas as pd
import numpy as np

def trigger_push_notification(metrics):
    print("\n⚡ [PUSH ENGINE ACTIVATED] Dispatching live alert to subscribers...")
    print("------------------------------------------------------------------")
    print(f"🚨 LIQUID RADAR ALERT: {metrics['Ticker']} RISK IS SPIKING!")
    print(f"Current Condition: {metrics['Engine Verdict']}")
    print(f"Action Step: The smart money is moving to cash. Protect your capital. Delay new entries.")
    print("------------------------------------------------------------------\n")

def calculate_liquidity_risk(ticker_symbol):
    ticker_symbol = ticker_symbol.upper().strip()
    
    try:
        asset = yf.Ticker(ticker_symbol)
        df = asset.history(period="60d")
        
        if df.empty or len(df) < 15:
            return {"error": "Could not find active liquidity flows."}
    except Exception:
        return {"error": "Network timeout or invalid ticker format."}

    df['Dollar_Volume'] = df['Close'] * df['Volume']
    df['Rolling_Vol_Avg'] = df['Dollar_Volume'].rolling(window=14).mean()
    
    latest_close = df['Close'].iloc[-1]
    latest_vol = df['Dollar_Volume'].iloc[-1]
    avg_vol = df['Rolling_Vol_Avg'].iloc[-1]
    
    volume_deficit_ratio = latest_vol / avg_vol
    
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

    metrics = {
        "Ticker": ticker_symbol,
        "Current Price": f"${round(latest_close, 2)}",
        "Liquidity Risk Score": f"{int(calculated_risk * 100)}%",
        "Safety Index": f"{safety_score}%",
        "Engine Verdict": verdict
    }

    if safety_score < 50:
        trigger_push_notification(metrics)

    return metrics
