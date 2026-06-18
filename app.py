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
    """
    Automated database execution layer.
    Asynchronously intercepts Stripe checkout signals and provisions access.
    """
    conn = sqlite3.connect('liquid_radar.db', timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       email TEXT UNIQUE, 
                       password_hash TEXT, 
                       subscription_status TEXT DEFAULT 'active')''')
    
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

st.markdown("""
    <style>
    .stApp { background-color: #121212 !important; }
    .main { background-color: #121212; color: #FFFFFF; }
    h1, h2, h3, p, label, li, span, div { color: #FFFFFF !important; font-family: 'Helvetica Neue', sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 2.2rem; font-weight: 700; color: #FFFFFF !important; }
    div[data-testid="stMetricLabel"] { color: #AAAAAA !important; }
    .fomo-box { padding: 20px; background-color: #1A1A1A; border-radius: 8px; border: 1px solid #333; margin-top: 15px; }
    .timeline-card { padding: 15px; background-color: #161616; border-left: 3px solid #444; margin-bottom: 12px; border-radius: 4px; }
    .stTextInput input { background-color: #1A1A1A !important; color: #FFFFFF !important; border: 1px solid #333 !important; }
    </style>
    """, unsafe_allow_html=True)


# --- DATA PRIVACY GATE UTILITIES ---
def check_subscriber_auth(email, password):
    conn = sqlite3.connect('liquid_radar.db', timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT subscription_status FROM users WHERE email=? AND password_hash=?", (email.strip().lower(), password))
        user = cursor.fetchone()
    except sqlite3.OperationalError:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE
