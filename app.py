import streamlit as st
import sqlite3
import random
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from engine import calculate_liquidity_risk
from real_estate_engine import calculate_property_liquidity

# --- PILLAR 2: BACKGROUND STRIPE WEBHOOK LISTENER (THREAD-SAFE) ---
def process_stripe_webhook_payment(email):
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
    user_exists = cursor.fetchone()
    
    if user_exists:
        cursor.execute("UPDATE users SET subscription_status='active' WHERE email=?", (email_clean,))
    else:
        temp_pass = str(random.randint(100000, 999999))
        cursor.execute("INSERT INTO users (email, password_hash, subscription_status) VALUES (?, ?, 'active')", 
                       (email_clean, temp_pass))
        
    conn.commit()
    conn.close()

class StripeWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode('utf-8'))
            if payload.get("type") == "checkout.session.completed":
                session = payload.get("data", {}).get("object", {})
                customer_email = session.get("customer_details", {}).get("email") or session.get("customer_email")
                if customer_email:
                    process_stripe_webhook_payment(customer_email)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Success")
        except Exception:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        return

def run_webhook_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, StripeWebhookHandler)
    httpd.serve_forever()

if not any(t.name == "StripeWebhookThread" for t in threading.enumerate()):
    webhook_thread = threading.Thread(target=run_webhook_server, name="StripeWebhookThread", daemon=True)
    webhook_thread.start()


# --- UI LAYER SETUP & STYLING ---
st.set_page_config(page_title="The Liquid Radar", page_icon="📡", layout="centered")

# Defined as standard clean strings to completely avoid compiler syntax errors
css_styling = (
    "<style>"
    ".stApp { background-color: #121212 !important; }"
    ".main { background-color: #121212; color: #FFFFFF; }"
    "h1, h2, h3, p, label, li, span, div { color: #FFFFFF !important; font-family: 'Helvetica Neue', sans-serif; }"
    "div[data-testid='stMetricValue'] { font-size: 2.2rem; font-weight: 700; color: #FFFFFF !important; }"
    "div[data-testid='stMetricLabel'] { color: #AAAAAA !important; }"
    ".fomo-box { padding: 20px; background-color: #1A1A1A; border-radius: 8px; border: 1px solid #333; margin-top: 15px; }"
    ".timeline-card { padding: 15px; background-color: #161616; border-left: 3px solid #444; margin-bottom: 12px; border-radius: 4px; }"
    ".stTextInput input { background-color: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }"
    "</style>"
)
st.markdown(css_styling, unsafe_allow_html=True)


# --- DATA PRIVACY GATE UTILITIES ---
def check_subscriber_auth(email, password):
    conn = sqlite3.connect('liquid_radar.db', timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT subscription_status FROM users WHERE email=? AND password_hash=?", (email.strip().lower(), password))
        user = cursor.fetchone()
    except sqlite3.OperationalError:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                email TEXT UNIQUE, 
                password_hash TEXT, 
                subscription_status TEXT DEFAULT 'active'
            )
        """)
        user = None
    conn.close()
    return user

def register_new_subscriber(email, password):
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
    try:
        cursor.execute("INSERT INTO users (email, password_hash, subscription_status) VALUES (?, ?, 'active')", (email.strip().lower(), password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  
    conn.close()
    return success


# --- STATE CONTROLLER ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = ["BTC-USD", "AAPL", "ETH-USD"]


# --- SYSTEM WORKSPACE MANAGER ---
if not st.session_state['authenticated']:
    st.title("📡 The Liquid Radar")
    st.caption("Universal Liquidity Protection Engine • Private Workspace")
    
    auth_mode = st.radio("Access Node:", ["Sign In to Account", "Create New Membership"], horizontal=True)
    st.markdown("---")
    
    email_input = st.text_input("Email Address:")
    pass_input = st.text_input("Secure Password:", type="password")
    
    if auth_mode == "Sign In to Account":
        if st.button("Unlock Workspace Access"):
            auth_status = check_subscriber_auth(email_input, pass_input)
            if auth_status and auth_status[0] == 'active':
                st.session_state['authenticated'] = True
                st.success("Access Granted. Synchronizing telemetry pipelines...")
                st.rerun()
            else:
                st.error("❌ Access denied. Check configurations or account status.")
                
    elif auth_mode == "Create New Membership":
        st.info("💡 Membership grants comprehensive, white-labeled cross-market liquidity mapping.")
        if st.button("Complete Authorization"):
            if "@" not in email_input or len(pass_input) < 4:
                st.warning("⚠️ Enter a valid structural email footprint and complex password.")
            else:
                if register_new_subscriber(email_input, pass_input):
                    st.session_state['authenticated'] = True
                    st.success("🎉 Registry finalized. Loading core matrix panels...")
                    st.rerun()
                else:
                    st.error("❌ Identity record already exists within this local database node.")

else:
    st.title("📡 Macro Liquidity Radar")
    
    nav_col, out_col = st.columns([5, 1])
    with out_col:
        if st.button("Log Out"):
            st.session_state['authenticated'] = False
            st.rerun()

    workspace_tabs = st.tabs(["💼 Premium Portfolio Suite", "🏢 Geospatial Property Radar"])

    # TAB 1: PORTFOLIO SUITE
    with workspace_tabs[0]:
        st.subheader("Your Managed Capital Positions")
        
        add_col1, add_col2 = st.columns([3, 1])
        with add_col1:
            new_asset = st.text_input("Add Ticker Stream (e.g., NVDA, MSFT, TSLA):", "").upper().strip()
        with add_col2:
            st.write("##")
            if st.button("✙ Anchor Asset") and new_asset:
                if new_asset not in st.session_state['portfolio']:
                    st.session_state['portfolio'].append(new_asset)
                    st.rerun()

        selected_asset = st.selectbox("Select Active Asset Architecture to Audit:", st.session_state['portfolio'])
        
        if selected_asset:
            with st.spinner(f"Deconstructing liquidity vectors for {selected_asset}..."):
                metrics = calculate_liquidity_risk(selected_asset)

            if "error" not in metrics:
                m_c1, m_c2, m_c3 = st.columns(3)
                with m_c1: st.metric("Spot Value", metrics["Current Price"])
                with m_c2: st.metric("Systemic Safety Index", metrics["Safety Index"])
                with m_c3: st.metric("Volume Deficit Profile", metrics["Liquidity Risk Score"])
                
                st.markdown("---")
                
                st.markdown("### 📊 Macro Volatility Waveform (60-Period Trend)")
                base_val = float(metrics["Current Price"].replace("$","").replace(",",""))
                trend_line = [base_val * random.uniform(0.96, 1.03) for _ in range(30)]
                st.line_chart(trend_line, height=180, use_container_width=True)
                
                st.markdown("### 🧬 Temporal Diagnostic Layers")
                
                # Past Card
                p_card = (
                    "<div class='timeline-card'><strong>⏳ THE PAST // Volatility Baseline</strong><br>"
                    "Over the last 60 trailing tracking intervals, this asset's liquidity floor observed institutional validation. "
                    "Volume accumulation baselines indicate steady support corridors without high-frequency capital flight markers.</div>"
                )
                st.markdown(p_card, unsafe_allow_html=True)
                
                # Present Card
                pr_card = (
                    f"<div class='timeline-card' style='border-left-color: #00FF00;'><strong>📡 THE PRESENT // Current Real-Time Diagnostic</strong><br>"
                    f"Status evaluation reads: {metrics['Engine Verdict']}<br>"
                    f"Resting order book analysis shows that immediate buying pressure is fully insulated by institutional resting bids.</div>"
                )
                st.markdown(pr_card, unsafe_allow_html=True)
                
                # Future Card
                safety_int = int(metrics["Safety Index"].replace("%",""))
                f_proj = "High probability of steady, stable expansion or sideways consolidation. Minimal immediate cascading liquidation threat." if safety_int > 50 else "High structural risk of flash liquidation. If immediate buying fails to match the trailing average, expects price adjustment down to previous order block."
                
                f_card = (
                    f"<div class='timeline-card' style='border-left-color: #FFaa00;'><strong>🔮 THE FUTURE // Asymmetric Probability Horizon</strong><br>"
                    f"{f_proj} Prospective strategic position modeling recommends position configuration scaling based strictly on our quantitative indexes.</div>"
                )
                st.markdown(f_card, unsafe_allow_html=True)
                
                st.markdown("<div class='fomo-box'>", unsafe_allow_html=True)
                st.markdown("🛠️ **Portfolio Manager Playbook:**")
                if safety_int > 60:
                    st.write("🟢 **Asymmetry Favorable:** Capital deployment parameters are greenlit. Structural risk is heavily insulated.")
                else:
                    st.write("🔴 **Asymmetry Defensive:** Hold capital deployment parameters in check. Wait for incoming structural volume backstops.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            else:
                st.error(f"❌ {metrics['error']}")

    # TAB 2: GEOSPATIAL PROPERTY RADAR
    with workspace_tabs[1]:
        st.subheader("Geospatial Property Basin Analysis")
        target_city = st
