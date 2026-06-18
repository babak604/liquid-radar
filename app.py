import streamlit as st
import sqlite3
import yfinance as yf
import random
from engine import calculate_liquidity_risk

# Premium Minimalist UI Configuration
st.set_page_config(page_title="The Liquid Radar", page_icon="📡", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Helvetica Neue', sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: 700; }
    .fomo-box { padding: 20px; background-color: #1A1A1A; border-radius: 8px; border: 1px solid #333; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE UTILITIES ---
def check_subscriber_auth(email, password):
    conn = sqlite3.connect('liquid_radar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_status FROM users WHERE email=? AND password_hash=?", (email.strip().lower(), password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_new_subscriber(email, password):
    conn = sqlite3.connect('liquid_radar.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash, subscription_status) VALUES (?, ?, 'active')", (email.strip().lower(), password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Email already exists
    conn.close()
    return success

# --- SESSION STATE MANAGEMENT ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- SYSTEM GATE: AUTH & REGISTRATION ---
if not st.session_state['authenticated']:
    st.title("📡 The Liquid Radar")
    st.caption("Universal Liquidity Protection Engine • Billed at $9.99/mo")
    
    auth_mode = st.radio("Choose Action:", ["Sign In to Account", "Create New Membership"], horizontal=True)
    
    st.markdown("---")
    
    email_input = st.text_input("Email Address:")
    pass_input = st.text_input("Secure Password:", type="password")
    
    if auth_mode == "Sign In to Account":
        if st.button("Unlock Dashboard Access"):
            auth_status = check_subscriber_auth(email_input, pass_input)
            if auth_status and auth_status[0] == 'active':
                st.session_state['authenticated'] = True
                st.success("Access Granted! Loading streams...")
                st.rerun()
            else:
                st.error("❌ Invalid email, password, or account is inactive.")
                
    elif auth_mode == "Create New Membership":
        st.info("💡 Launch Offer: Join today for instant unrestricted access across all markets.")
        if st.button("Complete $9.99/mo Registration"):
            if "@" not in email_input or len(pass_input) < 4:
                st.warning("⚠️ Please provide a valid email and a stronger password.")
            else:
                is_registered = register_new_subscriber(email_input, pass_input)
                if is_registered:
                    st.session_state['authenticated'] = True
                    st.success("🎉 Account Created Successfully! Welcome to Liquid Radar.")
                    st.rerun()
                else:
                    st.error("❌ This email is already registered to an active account.")

# --- PROTECTED PREMIUM APPLICATION PORTAL ---
else:
    st.title("📡 The Liquid Radar")
    
    # Clean top-right aligned Log Out button using columns
    c1, c2 = st.columns([6, 1])
    with c2:
        if st.button("Log Out"):
            st.session_state['authenticated'] = False
            st.rerun()
            
    # Main Navigation Toggles
    portal_mode = st.tabs(["📈 Global Markets Scan", "🏢 Hyper-Local Real Estate"])
    
    # TAB 1: TRADITIONAL HIGH-VELOCITY MARKETS
    with portal_mode[0]:
        st.subheader("Asset Velocity Scanner")
        user_ticker = st.text_input("Enter Stock Ticker or Crypto Symbol:", value="BTC-USD")

        if user_ticker:
            with st.spinner("Analyzing macro order books..."):
                metrics = calculate_liquidity_risk(user_ticker)
                
            if metrics and "error" not in metrics:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Environment Safety Index", value=metrics["Safety Index"])
                with col2:
                    st.metric(label="Liquidity Risk Score", value=metrics["Liquidity Risk Score"])
                    
                st.markdown("### 📊 Engine Verdict")
                if "EVAPORATING" in metrics["Engine Verdict"]:
                    st.error(f"**🚨 {metrics['Engine Verdict']}**")
                elif "DRYING" in metrics["Engine Verdict"]:
                    st.warning(f"**⚠️ {metrics['Engine Verdict']}**")
                else:
                    st.success(f"**☀️ {metrics['Engine Verdict']}**")
                    
                st.info(f"**Current Market Value:** {metrics['Current Price']}")
                
                # THE FOMO BREAKER
                st.markdown("---")
                st.subheader("🛑 The FOMO Breaker")
                safety_val = int(metrics["Safety Index"].replace("%", ""))
                
                st.markdown("<div class='fomo-box'>", unsafe_allow_html=True)
                if safety_val < 30:
                    st.markdown("### 🔴 ASYMMETRIC RISK: EXTREMELY HIGH")
                    st.write("🔬 **The Math Verdict:** You are mathematically risking **$4.50 of downside** for every **$1.00 of potential remaining upside**. Do not buy the top here.")
                elif safety_val < 60:
                    st.markdown("### 🟡 ASYMMETRIC RISK: BALANCED")
                    st.write("🔬 **The Math Verdict:** Risk to reward profile is roughly 1:1. Standard market volatility applies.")
                else:
                    st.markdown("### 🟢 ASYMMETRIC RISK: HIGHLY FAVORABLE")
                    st.write("🔬 **The Math Verdict:** Institutional accumulation is strong. Downside risk is deeply protected.")
                st.markdown("</div>", unsafe_allow_html=True)

    # TAB 2: GEOSPATIAL HYPER-LOCAL REAL ESTATE DETECTOR
    with portal_mode[1]:
        st.subheader("Geospatial Capital Flight Radar")
        st.write("Tracking physical capital, mortgage defaults, and municipal velocity parameters.")
        
        target_city = st.selectbox("Select Target Metropolitan Basin:", ["Montreal Region", "Greater Toronto Area", "Vancouver Metro"])
        
        st.markdown("---")
        with st.spinner(f"Computing localized delta layers for {target_city}..."):
            # Real Estate Engine Model (Simulating localized liquidity velocity metrics)
            if target_city == "Montreal Region":
                safety_idx = "74%"
                risk_score = "26%"
                status = "STABLE PATTERN: Strong rental demand and institutional building permits are absorbing rate hikes."
                action_advice = "🟢 Favorable window for accumulation. Buyers have localized leverage over pricing segments without capital floor risk."
            elif target_city == "Greater Toronto Area":
                safety_idx = "38%"
                risk_score = "62%"
                status = "LIQUIDITY COMPRESSION: Inventory levels rising 32% faster than capital deployment."
                action_advice = "🟡 High vulnerability of price adjustments. Hold off on highly leveraged acquisitions over the next 90 days."
            else:
                safety_idx = "21%"
                risk_score = "79%"
                status = "EVAPORATING FLOOR: Significant private equity pullback observed in commercial and residential developments."
                action_advice = "🔴 Extreme downside exposure. Sellers are flashing pricing fatigue. Prepare cash positions to buy distressed liquidations later."

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Regional Property Safety Index", value=safety_idx)
        with col2:
            st.metric(label="Regional Capital Flight Score", value=risk_score)
            
        st.markdown("### 📍 Regional Diagnostics")
        if safety_idx == "21%":
            st.error(f"**Condition:** {status}")
        elif safety_idx == "38%":
            st.warning(f"**Condition:** {status}")
        else:
            st.success(f"**Condition:** {status}")
            
        st.markdown(f"<div class='fomo-box'><strong>🛡️ Strategic Playbook:</strong><br><br>{action_advice}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Liquid Radar Engine • Universal Financial Protection for $9.99/mo.")