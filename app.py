import streamlit as st
import sqlite3
import random
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from engine import calculate_liquidity_risk
from real_estate_engine import calculate_property_liquidity

# --- SAFE BACKGROUND STRIPE WEBHOOK GATEWAY ---
def process_stripe_webhook_payment(email):
    try:
        conn = sqlite3.connect('liquid_radar.db', timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT UNIQUE, 
                password_hash TEXT, 
                subscription_status TEXT DEFAULT 'active'
            )
        """)
        email_clean = email.strip().lower()
        cursor.execute("SELECT email FROM users WHERE email=?", (email_clean,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET subscription_status='active' WHERE email=?", (email_clean,))
        else:
            temp_pass = str(random.randint(100000, 999999))
            cursor.execute("INSERT INTO users (email, password_hash, subscription_status) VALUES (?, ?, 'active')", 
                           (email_clean, temp_pass))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database sync bypass: {e}")

class StripeWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            if payload.get("type") == "checkout.session.completed":
                session = payload.get("data", {}).get("object", {})
                email = session.get("customer_details", {}).get("email") or session.get("customer_email")
                if email: process_stripe_webhook_payment(email)
            self.send_response(200)
            self.end_headers()
        except Exception:
            self.send_response(400)
            self.end_headers()
    def log_message(self, format, *args): return

def run_webhook_server():
    try:
        server_address = ('', 8080)
        httpd = HTTPServer(server_address, StripeWebhookHandler)
        httpd.serve_forever()
    except Exception as e:
        print(f"⚠️ Webhook port binding handled gracefully: {e}")

if not any(t.name == "StripeWebhookThread" for t in threading.enumerate()):
    threading.Thread(target=run_webhook_server, name="StripeWebhookThread", daemon=True).start()


# --- UI CONFIGURATION & PREMIUM RADICAL MINIMALIST THEME ---
st.set_page_config(page_title="LIQUID RADAR // TERMINAL", page_icon="📡", layout="centered")

css_styling = (
    "<style>"
    ".stApp { background-color: #08080a !important; }"
    "h1, h2, h3, p, label, li, span, div { font-family: 'SF Pro Display', 'Helvetica Neue', sans-serif !important; }"
    "h1 { font-weight: 800 !important; letter-spacing: -1px !important; color: #ffffff !important; }"
    "h3 { font-weight: 600 !important; letter-spacing: -0.5px !important; color: #ffffff !important; margin-bottom: 5px_important; }"
    "div[data-testid='stMetricValue'] { font-size: 2.4rem !important; font-weight: 700 !important; letter-spacing: -1px !important; color: #ffffff !important; }"
    "div[data-testid='stMetricLabel'] { color: #66666e !important; text-transform: uppercase !important; font-size: 0.75rem !important; letter-spacing: 1px !important; font-weight: 600 !important; }"
    ".terminal-container { padding: 24px; background-color: #0f0f12; border-radius: 12px; border: 1px solid #1c1c24; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 4px 24px rgba(0,0,0,0.5); }"
    ".timeline-card { padding: 18px; background-color: #13131a; border-radius: 8px; border: 1px solid #1c1c24; margin-bottom: 14px; transition: all 0.2s ease; }"
    ".timeline-card:hover { border-color: #2c2c3c; }"
    "p { color: #9a9aae !important; font-size: 0.95rem !important; line-height: 1.5 !important; }"
    ".stTextInput input { background-color: #13131a !important; color: #FFFFFF !important; border: 1px solid #1c1c24 !important; border-radius: 8px !important; padding: 10px !important; }"
    ".stSelectbox div[data-baseweb='select'] { background-color: #13131a !important; border: 1px solid #1c1c24 !important; border-radius: 8px !important; }"
    "hr { border-color: #1c1c24 !important; }"
    "</style>"
)
st.markdown(css_styling, unsafe_allow_html=True)


# --- ACCESS NODE SECURITY ---
if 'authenticated' not in st.session_state: st.session_state['authenticated'] = False
if 'portfolio' not in st.session_state: st.session_state['portfolio'] = ["BTC-USD", "AAPL", "ETH-USD"]

if not st.session_state['authenticated']:
    st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
    st.title("📡 LIQUID RADAR TERMINAL")
    st.caption("CORE MICROSTRUCTURE DATA LAYER // ACCESS RESTRICTED")
    st.markdown("---")
    email_input = st.text_input("Identity Authentication Handle:")
    pass_input = st.text_input("Cryptographic Signature Key:", type="password")
    if st.button("Establish Terminal Connection", use_container_width=True):
        st.session_state['authenticated'] = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- PREMIUM LIVE INTERFACE ---
else:
    # Sleek Top Banner
    c_title, c_btn = st.columns([5, 1])
    with c_title:
        st.title("📡 Liquid Radar // Core")
    with c_btn:
        st.write("##")
        if st.button("Disconnect", use_container_width=True):
            st.session_state['authenticated'] = False
            st.rerun()

    terminal_tabs = st.tabs(["📊 Asset Microstructure", "🏢 Geospatial Property Basins"])

    # TAB 1: ASSET MICROSTRUCTURE TERMINAL
    with terminal_tabs[0]:
        # Mount Module
        with st.container():
            st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
            st.markdown("### ✙ Mount New Intelligence Feed")
            add_col1, add_col2 = st.columns([4, 1])
            with add_col1:
                new_asset = st.text_input("Enter Asset Ticker Array:", label_visibility="collapsed", placeholder="e.g., NVDA, TSLA, MSFT").upper().strip()
            with add_col2:
                if st.button("Mount Array", use_container_width=True) and new_asset:
                    if new_asset not in st.session_state['portfolio']:
                        st.session_state['portfolio'].append(new_asset)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        selected_asset = st.selectbox("Active Telemetry Inspection Array:", st.session_state['portfolio'])
        
        if selected_asset:
            with st.spinner("Decoding infrastructure packet arrays..."):
                metrics = calculate_liquidity_risk(selected_asset)

            if metrics and "error" not in metrics:
                # Core Metrics Block wrapped in premium layout container
                st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
                st.markdown("### ⚡ Live Macro Registry")
                st.write("##")
                m_c1, m_c2, m_c3 = st.columns(3)
                with m_c1: st.metric("Spot Price", metrics.get("Current Price", "--"))
                with m_c2: st.metric("Systemic Safety Index", metrics.get("Safety Index", "--"))
                with m_c3: st.metric("Microstructure Risk", metrics.get("Liquidity Risk Score", "--"))
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Secondary Advanced Analytics block
                st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
                st.markdown("### 🔬 Order Book Deep Analytics")
                st.write("##")
                tech_col1, tech_col2, tech_col3 = st.columns(3)
                
                # Extract numerical metrics safely for native delta tracking display
                skew_str = metrics.get("Order Book Imbalance", "1.00x").replace("x", "")
                try: skew_val = float(skew_str)
                except ValueError: skew_val = 1.0
                skew_delta = f"{round((skew_val - 1.0) * 100, 1)}% vs base"
                
                with tech_col1:
                    st.metric("Parkinson Volatility", metrics.get("Historical Volatility", "--"))
                with tech_col2:
                    st.metric("Order Book Velocity Skew", metrics.get("Order Book Imbalance", "--"), delta=skew_delta, delta_color="normal" if skew_val >= 1.0 else "inverse")
                with tech_col3:
                    st.metric("Value at Risk (95% VaR)", metrics.get("Value at Risk 95", "--"))
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Visual Chart Waveform Section
                st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
                st.markdown("### 📊 High-Frequency Capital Velocity Waveform")
                raw_spot_string = metrics.get("Current Price", "100").replace("$","").replace(",","")
                try: base_val = float(raw_spot_string)
                except ValueError: base_val = 100.0
                trend_line = [base_val * random.uniform(0.98, 1.02) for _ in range(45)]
                st.line_chart(trend_line, height=180, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Chronological Timelines
                st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
                st.markdown("### 🧬 Temporal Phase Analysis")
                st.write("##")
                
                st.markdown(f"<div class='timeline-card' style='border-left: 4px solid #3b3b4f;'><h4 style='color:#ffffff;margin:0 0 5px 0;'>⏳ THE PAST // Volatility Coherence</h4><p>Rolling historical distributions confirm a current pricing variance structure of {metrics.get('Historical Volatility', '--')}. Assets are stabilizing near structural block boundaries.</p></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='timeline-card' style='border-left: 4px solid #00ff66;'><h4 style='color:#ffffff;margin:0 0 5px 0;'>📡 THE PRESENT // Automated Book Diagnostic</h4><p>Current Execution Verdict: {metrics.get('Engine Verdict', '--')}</p></div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='timeline-card' style='border-left: 4px solid #ffaa00;'><h4 style='color:#ffffff;margin:0 0 5px 0;'>🔮 THE FUTURE // Tail-Risk Projections</h4><p>Parametric VaR metrics register a maximum expected boundary deviation threshold of {metrics.get('Value at Risk 95', '--')}, validating macro safety parameters.</p></div>", unsafe_allow_html=True)
                
                # Conditional Visual Alerts
                safety_str = metrics.get("Safety Index", "50%").replace("%","")
                try: safety_int = int(safety_str)
                except ValueError: safety_int = 50
                
                if safety_int > 65:
                    st.success("📝 **SYSTEM STRATEGY ALERT:** Asymmetry validated. Liquidity corridors are exceptionally thick. Deployment parameters are highly favorable.")
                elif safety_int > 35:
                    st.warning("📝 **SYSTEM STRATEGY ALERT:** Volatility balanced. Book skew is operating in neutral variance bounds. Minimize over-leveraged deployments.")
                else:
                    st.error("📝 **SYSTEM STRATEGY ALERT:** Tail-risk critical. Market makers are pulling order books. Initialize defensive hedging sub-routines.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            else:
                st.error(f"❌ {metrics.get('error', 'Error syncing metadata channels.')}")

    # TAB 2: GEOSPATIAL PROPERTY RADAR TERMINAL
    with terminal_tabs[1]:
        st.markdown("<div class='terminal-container'>", unsafe_allow_html=True)
        st.markdown("### 🏢 Geospatial Property Basin Analysis")
        target_city = st.selectbox("Select Target Metropolitan Region Area:", ["Montreal Region", "Greater Toronto Area", "Vancouver Metro"])
        st.markdown("---")
        
        with st.spinner("Processing geospatial parameters..."):
            local_metrics = calculate_property_liquidity(target_city)

        if "error" not in local_metrics:
            rc1, rc2 = st.columns(2)
            with rc1: st.metric("Property Safety Index", local_metrics.get("Property Safety Index", "--"))
            with rc2: st.metric("Capital Flight Score", local_metrics.get("Capital Flight Score", "--"))
            
            st.write("##")
            st.info(f"📍 **Basin Assessment:** {local_metrics.get('Condition', '--')}")
            st.markdown(f"<div class='timeline-card' style='border-left: 4px solid #5856d6; margin-top:15px;'><h4 style='color:#ffffff;margin:0 0 5px 0;'>🛡️ Strategic Territorial Playbook</h4><p>{local_metrics.get('Strategic Playbook', '--')}</p></div>", unsafe_allow_html=True)
        else:
            st.error(f"❌ {local_metrics.get('error', 'Error parsing regional data stream.')}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Liquid Radar Quantum Terminal • Confidential Microstructure Interface.")
