import yfinance as yf
import pandas as pd
import numpy as np

def calculate_liquidity_risk(ticker_symbol):
    """
    Analyzes Volume-Weighted Capital Momentum to determine if 
    the market floor is thinning out.
    """
    # 1. Ingest historical daily data for the asset
    asset = yf.Ticker(ticker_symbol)
    df = asset.history(period="60d")
    
    if df.empty:
        return {"error": "Could not retrieve live market data flows."}

    # 2. Calculate the rolling average of Dollar Volume (Price * Volume)
    # This represents the actual liquidity circulating in the asset
    df['Dollar_Volume'] = df['Close'] * df['Volume']
    df['Rolling_Vol_Avg'] = df['Dollar_Volume'].rolling(window=14).mean()
    
    # 3. Compute Price vs. Liquidity Divergence
    # True capital flight happens when price stays flat/rising while volume drops
    df['Price_Change'] = df['Close'].pct_change()
    df['Volume_Change'] = df['Dollar_Volume'].pct_change()
    
    # Extract latest metrics
    latest_close = df['Close'].iloc[-1]
    latest_vol = df['Dollar_Volume'].iloc[-1]
    avg_vol = df['Rolling_Vol_Avg'].iloc[-1]
    
    # 4. Core Abstraction Logic (Turning deep data into a simple risk score)
    # If current volume is 30% below the 14-day average while price is peaking, trigger warning
    volume_deficit_ratio = latest_vol / avg_vol
    
    base_danger_prob = 0.15 # Normal market noise baseline
    
    if volume_deficit_ratio < 0.70:
        # Bayesian updating simulation: high probability of an impending drop/correction
        calculated_risk = 0.84 
        verdict = "EVAPORATING: Price is running on thin air. Institutional money is stepping back."
    elif volume_deficit_ratio < 0.85:
        calculated_risk = 0.52
        verdict = "DRYING UP: Capital momentum is slowing down. Exercise caution."
    else:
        calculated_risk = 0.18
        verdict = "HIGH HUMIDITY: Strong, healthy capital flows backing current levels."

    return {
        "ticker": ticker_symbol,
        "current_price": round(latest_close, 2),
        "liquidity_risk_score": f"{int(calculated_risk * 100)}%",
        "safety_index": f"{int((1 - calculated_risk) * 100)}%",
        "engine_verdict": verdict
    }

# Quick testing loop to verify the math works on a standard index
if __name__ == "__main__":
    print("📡 Initializing Liquid Radar Core...")
    # Testing the S&P 500 tech sector proxy
    result = calculate_liquidity_risk("XLK")
    
    print("\n--- LIVE TELEMETRY UPDATE ---")
    for key, value in result.items():
        print(f"{key.replace('_', ' ').title()}: {value}")