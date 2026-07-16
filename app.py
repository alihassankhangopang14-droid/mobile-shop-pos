# -*- coding: utf-8 -*-
"""
Ali Mobiles & Communication - Super POS System
یہ ایک مکمل موبائل شاپ POS سسٹم ہے جس میں انوینٹری، سیلز، ریپیرنگ کھاتہ،
ایزی پیسہ/جاز کیش کیش بک، اور پرنٹ ایبل رسید شامل ہیں۔
Run: streamlit run app.py
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components
import urllib.parse

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Ali Mobiles & Communication - POS",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "ali_mobiles_pos.db"

# ============================================================
# CUSTOM CSS (RTL support + Navy/Gold Theme)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');

    .urdu-text {
        font-family: 'Noto Nastaliq Urdu', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        background: linear-gradient(135deg, #0a1a3a 0%, #1e3a6e 55%, #3a1e6e 100%);
        padding: 26px 30px;
        border-radius: 14px;
        border: 2px solid #f5d67e;
        margin-bottom: 18px;
        text-align: center;
    }
    .main-header h1 {
        color: #f5d67e;
        margin: 0;
        font-size: 40px;
        font-weight: 900;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }
    .main-header .header-sub {
        color: #ffffff;
        margin: 8px 0 0 0;
        font-size: 16px;
        font-weight: 600;
    }
    h2, h3 { font-weight: 800 !important; }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 700 !important;
    }
    .stButton > button {
        font-weight: 700;
        font-size: 15px;
        border-radius: 10px;
        padding: 10px 0;
    }
    .nav-tile {
        border-radius: 14px;
        padding: 22px 10px 14px 10px;
        text-align: center;
        margin-bottom: 6px;
    }
    .nav-tile-icon {
        font-size: 42px;
        line-height: 1;
    }
    .nav-tile-label {
        color: #ffffff;
        font-size: 19px;
        font-weight: 800;
        margin-top: 8px;
    }
    /* Big colorful clickable nav tiles (the first two horizontal blocks on the page) */
    div[data-testid="stHorizontalBlock"]:nth-of-type(-n+2) button {
        min-height: 100px;
        font-size: 21px !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        border: 2px solid rgba(255,255,255,0.25) !important;
        white-space: pre-line !important;
    }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(1) button { background:#1e3a6e !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(2) button { background:#0a5c36 !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(1) div[data-testid="column"]:nth-of-type(3) button { background:#8a4b00 !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(1) button { background:#5c1e6e !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(2) button { background:#7a1f1f !important; }
    div[data-testid="stHorizontalBlock"]:nth-of-type(2) div[data-testid="column"]:nth-of-type(3) button { background:#1f6e5c !important; }
    .metric-card {
        background: #101a2e;
        border: 1px solid #26324a;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        color: #f5d67e;
    }
    .status-pending { background:#4a3b00; color:#ffd85e; padding:3px 10px; border-radius:12px; font-size:12px; }
    .status-ready { background:#00304a; color:#5ec9ff; padding:3px 10px; border-radius:12px; font-size:12px; }
    .status-delivered { background:#0a3d1f; color:#6fe08a; padding:3px 10px; border-radius:12px; font-size:12px; }
    .receipt-box {
        background: white;
        color: black;
        padding: 25px;
        border-radius: 8px;
        max-width: 420px;
        margin: auto;
        font-family: 'Noto Nastaliq Urdu', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATABASE LAYER
# ============================================================
def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mobiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT, customer_cnic TEXT, customer_phone TEXT,
            brand TEXT, model TEXT, imei1 TEXT UNIQUE, imei2 TEXT,
            condition TEXT, purchase_price REAL, selling_price REAL,
            status TEXT DEFAULT 'Available',
            actual_selling_price REAL DEFAULT 0,
            buyer_name TEXT, buyer_phone TEXT,
            purchase_date TEXT, sale_date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT, customer_phone TEXT,
            device_model TEXT, fault_description TEXT,
            estimated_cost REAL, advance_paid REAL, balance REAL,
            delivery_date TEXT, repair_status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cashbook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, amount REAL, description TEXT, entry_date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------ Mobiles (Inventory) ------------------
def add_mobile(data):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO mobiles (customer_name, customer_cnic, customer_phone, brand, model,
                imei1, imei2, condition, purchase_price, selling_price, status,
                actual_selling_price, purchase_date)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (data['customer_name'], data['customer_cnic'], data['customer_phone'],
              data['brand'], data['model'], data['imei1'], data['imei2'], data['condition'],
              data['purchase_price'], data['selling_price'], 'Available', 0,
              datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        return True, "سٹاک ریکارڈ محفوظ ہو گیا ہے!"
    except sqlite3.IntegrityError:
        return False, "خرابی: یہ IMEI پہلے سے انوینٹری میں موجود ہے!"
    finally:
        conn.close()

def get_inventory():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM mobiles ORDER BY id DESC", conn)
    conn.close()
    return df

def sell_mobile(mobile_id, actual_price, buyer_name, buyer_phone):
    conn = get_conn()
    conn.execute("""
        UPDATE mobiles SET status='Sold', actual_selling_price=?, buyer_name=?, buyer_phone=?, sale_date=?
        WHERE id=?
    """, (actual_price, buyer_name, buyer_phone, datetime.now().strftime("%Y-%m-%d %H:%M"), mobile_id))
    conn.commit()
    conn.close()

def delete_mobile(mobile_id):
    conn = get_conn()
    conn.execute("DELETE FROM mobiles WHERE id=?", (mobile_id,))
    conn.commit()
    conn.close()

def add_direct_sale(data):
    """Adds and immediately marks as sold a mobile that was NOT previously in inventory
    (e.g. a phone brought in by someone else, sold on the spot)."""
    conn = get_conn()
    imei = data['imei1'].strip() if data.get('imei1') else ""
    if not imei:
        imei = f"DIRECT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("""
        INSERT INTO mobiles (customer_name, customer_cnic, customer_phone, brand, model,
            imei1, imei2, condition, purchase_price, selling_price, status,
            actual_selling_price, buyer_name, buyer_phone, purchase_date, sale_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ("", "", "", data['brand'], data['model'], imei, "", data['condition'],
          data['cost_price'], data['selling_price'], 'Sold', data['selling_price'],
          data['buyer_name'], data['buyer_phone'], now, now))
    conn.commit()
    conn.close()

# ------------------ Repairs ------------------
def add_repair(data):
    balance = data['estimated_cost'] - data['advance_paid']
    conn = get_conn()
    conn.execute("""
        INSERT INTO repairs (customer_name, customer_phone, device_model, fault_description,
            estimated_cost, advance_paid, balance, delivery_date, repair_status, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (data['customer_name'], data['customer_phone'], data['device_model'],
          data['fault_description'], data['estimated_cost'], data['advance_paid'],
          balance, str(data['delivery_date']), 'Pending',
          datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_repairs():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM repairs ORDER BY id DESC", conn)
    conn.close()
    return df

def update_repair_status(repair_id, status):
    conn = get_conn()
    conn.execute("UPDATE repairs SET repair_status=? WHERE id=?", (status, repair_id))
    conn.commit()
    conn.close()

def delete_repair(repair_id):
    conn = get_conn()
    conn.execute("DELETE FROM repairs WHERE id=?", (repair_id,))
    conn.commit()
    conn.close()

# ------------------ Cashbook ------------------
def add_cash_entry(entry_type, amount, description):
    conn = get_conn()
    conn.execute("""
        INSERT INTO cashbook (type, amount, description, entry_date) VALUES (?,?,?,?)
    """, (entry_type, amount, description, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def get_cashbook():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM cashbook ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_cash_entry(entry_id):
    conn = get_conn()
    conn.execute("DELETE FROM cashbook WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()

# ------------------ Dashboard Stats ------------------
def get_stats():
    inv = get_inventory()
    rep = get_repairs()
    cash = get_cashbook()

    stock_value = inv[inv['status'] == 'Available']['purchase_price'].sum() if not inv.empty else 0
    total_items = len(inv[inv['status'] == 'Available']) if not inv.empty else 0
    total_sales = inv[inv['status'] == 'Sold']['actual_selling_price'].sum() if not inv.empty else 0
    sales_profit = (inv[inv['status'] == 'Sold']['actual_selling_price'] -
                     inv[inv['status'] == 'Sold']['purchase_price']).sum() if not inv.empty else 0

    active_repairs = len(rep[rep['repair_status'] != 'Delivered']) if not rep.empty else 0
    repair_revenue = rep[rep['repair_status'] == 'Delivered']['estimated_cost'].sum() if not rep.empty else 0

    if not cash.empty:
        easypaisa_in = cash[cash['type'].str.contains('CashIn', na=False)]['amount'].sum()
        easypaisa_out = cash[cash['type'].str.contains('CashOut', na=False)]['amount'].sum()
        expenses = cash[cash['type'] == 'Shop Expense']['amount'].sum()
    else:
        easypaisa_in = easypaisa_out = expenses = 0

    total_profit = sales_profit + repair_revenue - expenses

    return {
        "total_items": total_items, "stock_value": stock_value, "total_sales": total_sales,
        "total_profit": total_profit, "active_repairs": active_repairs,
        "repair_revenue": repair_revenue, "easypaisa_balance": easypaisa_in - easypaisa_out,
        "expenses": expenses
    }

# ============================================================
# PRINTABLE RECEIPT COMPONENT
# ============================================================
def show_receipt(title, client, phone, item_desc, price, extra=""):
    receipt_html = f"""
    <div class="receipt-box" id="receipt">
        <div style="text-align:center; border-bottom:1px solid #ccc; padding-bottom:12px; margin-bottom:12px;">
            <h2 style="margin:0;">Ali Mobiles & Communication</h2>
            <p style="font-size:11px; color:#666; margin:2px 0;">Dhok Kala Khan, Shamsabad, Rawalpindi</p>
            <p style="font-size:11px; color:#666; margin:2px 0;">Phone: 0302-9401314</p>
        </div>
        <p style="text-align:center; font-weight:bold; text-decoration:underline;">{title}</p>
        <p><b>گاہک کا نام:</b> {client}</p>
        <p><b>موبائل نمبر:</b> {phone}</p>
        <p><b>تفصیل:</b> {item_desc}</p>
        {f"<p><b>اضافی معلومات:</b> {extra}</p>" if extra else ""}
        <p style="text-align:right; font-weight:bold; font-size:16px; border-top:1px solid #ccc; padding-top:8px;">
            کل رقم: PKR {price:,.0f}
        </p>
        <p style="text-align:center; font-size:11px; color:#888; font-style:italic;">
            آنے کا شکریہ! خریداری یا مرمت شدہ موبائل کی وارنٹی چیک کریں۔
        </p>
    </div>
    <div style="text-align:center; margin-top:10px;">
        <button onclick="window.print()"
            style="background:#1e3a6e; color:white; border:none; padding:8px 20px; border-radius:6px; cursor:pointer;">
            🖨️ پرنٹ کریں
        </button>
    </div>
    """
    components.html(receipt_html, height=420, scrolling=True)

# ============================================================
# WHATSAPP MESSAGE BUILDER
# ============================================================
def build_repair_whatsapp_message(customer_name, device_model, fault_description,
                                    estimated_cost, advance_paid, balance):
    message = (
        f"السلام علیکم محترم کسٹمر!\n\n"
        f"*علی موبائلز اینڈ کمیونیکیشن* 📱\n"
        f"آپ کا موبائل ریپیئرنگ آرڈر درج کر لیا گیا ہے۔\n\n"
        f"👤 *گاہک:* {customer_name}\n"
        f"📱 *موبائل ماڈل:* {device_model}\n"
        f"🛠️ *خرابی/مسئلہ:* {fault_description}\n"
        f"💰 *کل ریٹ:* PKR {estimated_cost:,.0f}\n"
        f"💵 *ایڈوانس رقم:* PKR {advance_paid:,.0f}\n"
        f"🔴 *بقایا رقم:* PKR {balance:,.0f}\n\n"
        f"⚠️ *نوٹ:* موبائل کھولتے وقت اگر کوئی اضافی خرابی نکلی تو اس کے چارجز اوپر دی گئی رقم میں شامل نہیں ہوں گے اور علیحدہ سے لاگو ہوں گے۔\n\n"
        f"شکریہ! جیسے ہی آپ کا فون تیار ہوگا، آپ کو مطلع کر دیا جائے گا۔"
    )
    return message

def build_purchase_whatsapp_message(customer_name, brand, model, purchase_price):
    message = (
        f"السلام علیکم محترم!\n\n"
        f"*علی موبائلز اینڈ کمیونیکیشن* 📱\n"
        f"یہ تصدیق ہے کہ آپ نے اپنا موبائل ہمیں فروخت کیا ہے۔\n\n"
        f"👤 *فروخت کنندہ:* {customer_name}\n"
        f"📱 *موبائل:* {brand} {model}\n"
        f"💰 *وصول شدہ رقم:* PKR {purchase_price:,.0f}\n"
        f"📅 *تاریخ:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"شکریہ! علی موبائلز اینڈ کمیونیکیشن پر بھروسہ کرنے کا شکریہ۔"
    )
    return message

def build_sale_whatsapp_message(buyer_name, brand, model, price):
    message = (
        f"السلام علیکم محترم کسٹمر!\n\n"
        f"*علی موبائلز اینڈ کمیونیکیشن* 📱\n"
        f"یہ تصدیق ہے کہ آپ نے یہ موبائل ہم سے خریدا ہے۔\n\n"
        f"👤 *خریدار:* {buyer_name}\n"
        f"📱 *موبائل:* {brand} {model}\n"
        f"💰 *ادا شدہ رقم:* PKR {price:,.0f}\n"
        f"📅 *تاریخ:* {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"شکریہ! خریداری کی رسید محفوظ رکھیں۔ کسی بھی مسئلے کی صورت میں رابطہ کریں۔"
    )
    return message

def whatsapp_send_link(phone, message):
    """Builds a wa.me deep link. Returns None if phone number looks invalid."""
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if not digits:
        return None
    # Convert local Pakistani numbers (03xx...) to international format (923xx...)
    if digits.startswith("0"):
        digits = "92" + digits[1:]
    elif not digits.startswith("92"):
        digits = "92" + digits
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{digits}?text={encoded_message}"

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
# ============================================================
# SESSION STATE FOR NAVIGATION
# ============================================================
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# ============================================================
# SIDEBAR (shop info only — navigation lives on the main page)
# ============================================================
st.sidebar.markdown("### 📱 Ali Mobiles")
st.sidebar.caption("& Communication")
st.sidebar.markdown("---")
st.sidebar.markdown("**Proprietor:** علی حسن (Ali Hassan)")
st.sidebar.markdown("📞 0302-9401314")
st.sidebar.markdown("📍 Shamsabad, Rawalpindi")

# ============================================================
# BIG COLORFUL HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>📱 علی موبائلز اینڈ کمیونیکیشن</h1>
    <p class="header-sub">Ali Mobiles &amp; Communication — مکمل موبائل شاپ POS سسٹم</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# BIG TILE MENU — always visible on the front page, no sidebar needed
# ============================================================
NAV_ITEMS = [
    ("dashboard", "📊\nڈیش بورڈ"),
    ("purchase", "➕\nخریداری"),
    ("sell", "💵\nفروخت کریں"),
    ("inventory", "📋\nانوینٹری"),
    ("repair", "🛠️\nریپیرنگ کھاتہ"),
    ("cashbook", "💰\nایزی پیسہ/کھاتہ"),
]

row1 = st.columns(3)
row2 = st.columns(3)
tile_cols = row1 + row2
for col, (key, label) in zip(tile_cols, NAV_ITEMS):
    with col:
        if st.button(label, key=f"navbtn_{key}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()

st.markdown("---")

page = st.session_state.current_page

# ============================================================
# PAGE: DASHBOARD
# ============================================================
if page == "dashboard":
    st.subheader("ڈیش بورڈ سمری")
    stats = get_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("کل فروخت (Sales)", f"PKR {stats['total_sales']:,.0f}")
    c2.metric("موجودہ اسٹاک مالیت", f"PKR {stats['stock_value']:,.0f}")
    c3.metric("خالص منافع (+ ریپیرنگ)", f"PKR {stats['total_profit']:,.0f}")
    c4.metric("زیرِ کار ریپیرنگ", f"{stats['active_repairs']} Devices")

    c5, c6, c7 = st.columns(3)
    c5.metric("موجودہ اسٹاک تعداد", f"{stats['total_items']} Items")
    c6.metric("ایزی پیسہ/جاز کیش بیلنس", f"PKR {stats['easypaisa_balance']:,.0f}")
    c7.metric("کل اخراجات", f"PKR {stats['expenses']:,.0f}")

    st.markdown("---")
    st.markdown("##### حالیہ ریپیرنگ آرڈرز")
    rep = get_repairs()
    if not rep.empty:
        st.dataframe(
            rep[['customer_name', 'device_model', 'repair_status', 'balance', 'delivery_date']].head(5),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("ابھی کوئی ریپیرنگ ریکارڈ موجود نہیں۔")

# ============================================================
# PAGE: PURCHASE / ADD MOBILE
# ============================================================
elif page == "purchase":
    st.subheader("موبائل خریداری فارم")
    with st.form("purchase_form", clear_on_submit=True):
        st.markdown("**👤 کسٹمر کی معلومات**")
        c1, c2, c3 = st.columns(3)
        customer_name = c1.text_input("کسٹمر کا نام *")
        customer_cnic = c2.text_input("شناختی کارڈ (CNIC)")
        customer_phone = c3.text_input("موبائل نمبر *")

        st.markdown("**📱 موبائل تفصیلات**")
        c4, c5 = st.columns(2)
        brand = c4.text_input("برانڈ *")
        model = c5.text_input("ماڈل *")
        c6, c7 = st.columns(2)
        imei1 = c6.text_input("IMEI 1 *")
        imei2 = c7.text_input("IMEI 2")
        c8, c9, c10 = st.columns(3)
        condition = c8.selectbox("حالت", ["New", "Used"])
        purchase_price = c9.number_input("خرید قیمت (Purchase Price)", min_value=0.0, step=100.0)
        selling_price = c10.number_input("فروخت قیمت (Asking Price)", min_value=0.0, step=100.0)

        submitted = st.form_submit_button("محفوظ کریں (Save Purchase)", use_container_width=True)
        if submitted:
            if not customer_name or not customer_phone or not brand or not model or not imei1:
                st.error("براہ کرم تمام لازمی خانے (*) پُر کریں۔")
            else:
                ok, msg = add_mobile({
                    "customer_name": customer_name, "customer_cnic": customer_cnic,
                    "customer_phone": customer_phone, "brand": brand, "model": model,
                    "imei1": imei1, "imei2": imei2, "condition": condition,
                    "purchase_price": purchase_price, "selling_price": selling_price
                })
                if ok:
                    st.success(msg)
                    st.session_state["last_purchase_wa"] = {
                        "customer_name": customer_name, "customer_phone": customer_phone,
                        "brand": brand, "model": model, "purchase_price": purchase_price
                    }
                else:
                    st.error(msg)

    if st.session_state.get("last_purchase_wa"):
        d = st.session_state["last_purchase_wa"]
        msg = build_purchase_whatsapp_message(d["customer_name"], d["brand"], d["model"], d["purchase_price"])
        link = whatsapp_send_link(d["customer_phone"], msg)
        if link:
            st.link_button("💬 فروخت کنندہ کو تصدیقی پیغام بھیجیں", link, use_container_width=True)
            st.caption("بٹن دبانے سے واٹس ایپ کھلے گا، پیغام پہلے سے لکھا ہوگا — بس Send پر ٹیپ کریں۔")
        if st.button("بند کریں ✖️", key="close_purchase_wa"):
            st.session_state["last_purchase_wa"] = None
            st.rerun()

# ============================================================
# PAGE: SELL MOBILE (dedicated sell flow)
# ============================================================
elif page == "sell":
    st.subheader("موبائل فروخت کریں")

    sale_mode = st.radio(
        "پہلے یہ بتائیں:",
        ["📦 اسٹاک میں سے بیچ رہا ہوں (پہلے سے خریدا ہوا موبائل)",
         "🆕 نیا / باہر کا موبائل بیچ رہا ہوں (اسٹاک میں شامل نہیں)"]
    )
    st.markdown("---")

    # ---------- MODE 1: SELL FROM EXISTING INVENTORY ----------
    if sale_mode.startswith("📦"):
        inv = get_inventory()
        avail = inv[inv['status'] == 'Available'] if not inv.empty else inv

        if avail.empty:
            st.info("ابھی اسٹاک میں کوئی موبائل دستیاب نہیں۔ پہلے 'نیا موبائل خریدیں' سے اندراج کریں۔")
        else:
            options = {
                f"{row['brand']} {row['model']} — IMEI: {row['imei1']} (خرید قیمت: PKR {row['purchase_price']:,.0f})": row['id']
                for _, row in avail.iterrows()
            }
            choice_label = st.selectbox("کون سا موبائل بیچ رہے ہیں؟", list(options.keys()))
            selected_id = options[choice_label]
            selected_row = avail[avail['id'] == selected_id].iloc[0]

            with st.form("stock_sell_form", clear_on_submit=True):
                st.markdown(f"**منتخب موبائل:** {selected_row['brand']} {selected_row['model']}")
                actual_price = st.number_input(
                    "فروخت کی رقم *", min_value=0.0, step=100.0,
                    value=float(selected_row['selling_price'] or 0)
                )
                buyer_name = st.text_input("خریدار کا نام *")
                buyer_phone = st.text_input("خریدار کا موبائل نمبر *")

                submitted = st.form_submit_button("بیچ دیں ✅", use_container_width=True)
                if submitted:
                    if not buyer_name or not buyer_phone or actual_price <= 0:
                        st.error("براہ کرم تمام لازمی خانے (*) پُر کریں۔")
                    else:
                        profit = actual_price - selected_row['purchase_price']
                        sell_mobile(selected_id, actual_price, buyer_name, buyer_phone)
                        st.success(f"فروخت مکمل ہوگئی! خالص منافع: PKR {profit:,.0f}")
                        st.session_state["last_sale_wa"] = {
                            "buyer_name": buyer_name, "buyer_phone": buyer_phone,
                            "brand": selected_row['brand'], "model": selected_row['model'],
                            "price": actual_price
                        }

    # ---------- MODE 2: DIRECT SALE (NOT IN INVENTORY) ----------
    else:
        with st.form("direct_sale_form", clear_on_submit=True):
            st.markdown("**📱 موبائل کی تفصیل**")
            c1, c2 = st.columns(2)
            d_brand = c1.text_input("برانڈ *")
            d_model = c2.text_input("ماڈل *")
            c3, c4 = st.columns(2)
            d_imei = c3.text_input("IMEI (اختیاری)")
            d_condition = c4.selectbox("حالت", ["New", "Used"])

            st.markdown("**💰 رقم کی تفصیل**")
            c5, c6 = st.columns(2)
            d_cost = c5.number_input("آپ کی خرید/لاگت قیمت (Cost Price) *", min_value=0.0, step=100.0)
            d_price = c6.number_input("فروخت کی رقم (Selling Price) *", min_value=0.0, step=100.0)

            st.markdown("**👤 خریدار کی معلومات**")
            c7, c8 = st.columns(2)
            d_buyer_name = c7.text_input("خریدار کا نام *")
            d_buyer_phone = c8.text_input("خریدار کا موبائل نمبر *")

            submitted = st.form_submit_button("فروخت محفوظ کریں ✅", use_container_width=True)
            if submitted:
                if not d_brand or not d_model or not d_buyer_name or not d_buyer_phone or d_price <= 0:
                    st.error("براہ کرم تمام لازمی خانے (*) پُر کریں۔")
                else:
                    profit = d_price - d_cost
                    add_direct_sale({
                        "brand": d_brand, "model": d_model, "imei1": d_imei, "condition": d_condition,
                        "cost_price": d_cost, "selling_price": d_price,
                        "buyer_name": d_buyer_name, "buyer_phone": d_buyer_phone
                    })
                    st.success(f"فروخت محفوظ ہو گئی! خالص منافع: PKR {profit:,.0f}")
                    st.session_state["last_sale_wa"] = {
                        "buyer_name": d_buyer_name, "buyer_phone": d_buyer_phone,
                        "brand": d_brand, "model": d_model, "price": d_price
                    }

    # ---------- SHOW WHATSAPP BUTTON AFTER EITHER MODE ----------
    if st.session_state.get("last_sale_wa"):
        d = st.session_state["last_sale_wa"]
        wa_msg = build_sale_whatsapp_message(d["buyer_name"], d["brand"], d["model"], d["price"])
        wa_link = whatsapp_send_link(d["buyer_phone"], wa_msg)
        st.markdown("---")
        if wa_link:
            st.link_button("💬 خریدار کو تصدیقی پیغام بھیجیں", wa_link, use_container_width=True)
            st.caption("بٹن دبانے سے واٹس ایپ کھلے گا، پیغام پہلے سے لکھا ہوگا — بس Send پر ٹیپ کریں۔")
        else:
            st.warning("خریدار کا موبائل نمبر درست نہیں لگ رہا۔")
        if st.button("بند کریں ✖️", key="close_sale_wa_dedicated"):
            st.session_state["last_sale_wa"] = None
            st.rerun()

# ============================================================
# PAGE: INVENTORY
# ============================================================
elif page == "inventory":
    st.subheader("موبائل انوینٹری اور اسٹاک")

    if st.session_state.get("last_sale_wa"):
        d = st.session_state["last_sale_wa"]
        msg = build_sale_whatsapp_message(d["buyer_name"], d["brand"], d["model"], d["price"])
        link = whatsapp_send_link(d["buyer_phone"], msg)
        with st.container(border=True):
            if link:
                st.link_button("💬 خریدار کو تصدیقی پیغام بھیجیں", link, use_container_width=True)
                st.caption("بٹن دبانے سے واٹس ایپ کھلے گا، پیغام پہلے سے لکھا ہوگا — بس Send پر ٹیپ کریں۔")
            else:
                st.warning("خریدار کا موبائل نمبر درج نہیں ہوا، میسج نہیں بھیجا جا سکتا۔")
            if st.button("بند کریں ✖️", key="close_sale_wa"):
                st.session_state["last_sale_wa"] = None
                st.rerun()

    inv = get_inventory()

    if inv.empty:
        st.info("ابھی انوینٹری میں کوئی موبائل موجود نہیں۔")
    else:
        for _, row in inv.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1.5, 2])
                c1.markdown(f"**{row['customer_name'] or 'N/A'}**")
                c1.caption(row['customer_phone'])
                c2.markdown(f"**{row['brand']} {row['model']}**")
                c2.caption(f"IMEI: {row['imei1']}")
                c3.markdown(f"خرید: PKR {row['purchase_price']:,.0f}")
                if row['status'] == 'Sold':
                    c3.markdown(f"فروخت: PKR {row['actual_selling_price']:,.0f}")

                status_class = "status-delivered" if row['status'] == 'Sold' else "status-ready"
                status_label = "فروخت شدہ" if row['status'] == 'Sold' else "دستیاب"
                c4.markdown(f'<span class="{status_class}">{status_label}</span>', unsafe_allow_html=True)

                with c5:
                    b1, b2, b3 = st.columns(3)
                    if row['status'] == 'Available':
                        if b1.button("بیچیں", key=f"sell_{row['id']}"):
                            st.session_state[f"show_sell_{row['id']}"] = True
                    if b2.button("🖨️", key=f"print_{row['id']}"):
                        st.session_state[f"show_print_{row['id']}"] = True
                    if b3.button("🗑️", key=f"del_{row['id']}"):
                        delete_mobile(row['id'])
                        st.rerun()

                if st.session_state.get(f"show_sell_{row['id']}"):
                    with st.form(f"sell_form_{row['id']}"):
                        st.markdown("**موبائل فروخت کریں**")
                        actual_price = st.number_input("فروخت کی رقم", min_value=0.0,
                                                         value=float(row['selling_price'] or 0))
                        buyer_name = st.text_input("خریدار کا نام")
                        buyer_phone = st.text_input("خریدار کا موبائل نمبر")
                        colA, colB = st.columns(2)
                        if colA.form_submit_button("بیچ دیں ✅"):
                            sell_mobile(row['id'], actual_price, buyer_name, buyer_phone)
                            st.session_state[f"show_sell_{row['id']}"] = False
                            st.session_state["last_sale_wa"] = {
                                "buyer_name": buyer_name, "buyer_phone": buyer_phone,
                                "brand": row['brand'], "model": row['model'], "price": actual_price
                            }
                            st.success("فروخت مکمل ہوگئی!")
                            st.rerun()
                        if colB.form_submit_button("منسوخ کریں"):
                            st.session_state[f"show_sell_{row['id']}"] = False
                            st.rerun()

                if st.session_state.get(f"show_print_{row['id']}"):
                    show_receipt(
                        "موبائل فروخت کی رسید", row['customer_name'], row['customer_phone'],
                        f"{row['brand']} {row['model']}",
                        row['actual_selling_price'] if row['status'] == 'Sold' else row['selling_price']
                    )

# ============================================================
# PAGE: REPAIRING LEDGER
# ============================================================
elif page == "repair":
    st.subheader("🛠️ موبائل ریپیرنگ ریکارڈ اندراج")

    with st.form("repair_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        r_name = c1.text_input("کسٹمر کا نام *")
        r_phone = c2.text_input("فون نمبر *")
        r_model = c3.text_input("موبائل اور ماڈل *")

        r_fault = st.text_area("موبائل کا مسئلہ / خرابی *",
                                placeholder="مثال کے طور پر: ایل سی ڈی ٹوٹ گئی ہے، چارجنگ پورٹ خراب ہے")

        c4, c5, c6 = st.columns(3)
        r_cost = c4.number_input("کل ریٹ طے شدہ *", min_value=0.0, step=100.0)
        r_advance = c5.number_input("ایڈوانس رقم جمع شدہ", min_value=0.0, step=50.0)
        r_delivery = c6.date_input("کب تک لینے آئے گا؟", value=date.today())

        submitted = st.form_submit_button("محفوظ کریں اور رسید تیار کریں", use_container_width=True)
        if submitted:
            if not r_name or not r_phone or not r_model or not r_fault or r_cost <= 0:
                st.error("براہ کرم تمام لازمی خانے (*) پُر کریں۔")
            else:
                add_repair({
                    "customer_name": r_name, "customer_phone": r_phone, "device_model": r_model,
                    "fault_description": r_fault, "estimated_cost": r_cost,
                    "advance_paid": r_advance, "delivery_date": r_delivery
                })
                st.success("ریپیرنگ کا آرڈر کامیابی سے درج ہو گیا ہے!")
                st.session_state["last_repair_wa"] = {
                    "customer_name": r_name, "customer_phone": r_phone, "device_model": r_model,
                    "fault_description": r_fault, "estimated_cost": r_cost,
                    "advance_paid": r_advance, "balance": r_cost - r_advance
                }

    if st.session_state.get("last_repair_wa"):
        d = st.session_state["last_repair_wa"]
        msg = build_repair_whatsapp_message(
            d["customer_name"], d["device_model"], d["fault_description"],
            d["estimated_cost"], d["advance_paid"], d["balance"]
        )
        link = whatsapp_send_link(d["customer_phone"], msg)
        if link:
            st.link_button("💬 کسٹمر کو واٹس ایپ پیغام بھیجیں", link, use_container_width=True)
            st.caption("بٹن دبانے سے واٹس ایپ کھلے گا، پیغام پہلے سے لکھا ہوگا — بس Send پر ٹیپ کریں۔")
        if st.button("بند کریں ✖️", key="close_last_wa"):
            st.session_state["last_repair_wa"] = None
            st.rerun()

    st.markdown("---")
    st.markdown("##### ریپیرنگ آرڈرز کی لسٹ (Active Jobs)")

    rep = get_repairs()
    if rep.empty:
        st.info("ابھی کوئی ریپیرنگ ریکارڈ موجود نہیں۔")
    else:
        status_map = {"Pending": ("کام ہو رہا ہے", "status-pending"),
                      "Ready": ("تیار ہے", "status-ready"),
                      "Delivered": ("گاہک لے گیا", "status-delivered")}
        for _, row in rep.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([2, 2.5, 1.5, 1.5, 2.5])
                c1.markdown(f"**{row['customer_name']}**")
                c1.caption(row['customer_phone'])
                c2.markdown(f"**{row['device_model']}**")
                c2.caption(row['fault_description'])
                c3.markdown(f"⏰ {row['delivery_date']}")
                c4.markdown(f"کل: {row['estimated_cost']:,.0f}")
                c4.markdown(f"بقایا: {row['balance']:,.0f}")

                label, css_class = status_map.get(row['repair_status'], ("نامعلوم", "status-pending"))
                c5.markdown(f'<span class="{css_class}">{label}</span>', unsafe_allow_html=True)

                b1, b2, b3, b4, b5 = st.columns(5)
                if row['repair_status'] == 'Pending':
                    if b1.button("تیار کریں", key=f"ready_{row['id']}"):
                        update_repair_status(row['id'], 'Ready')
                        st.rerun()
                if row['repair_status'] == 'Ready':
                    if b2.button("حوالہ کیا", key=f"delivered_{row['id']}"):
                        update_repair_status(row['id'], 'Delivered')
                        st.rerun()
                if b3.button("🖨️ رسید", key=f"rprint_{row['id']}"):
                    st.session_state[f"show_rprint_{row['id']}"] = True
                if b4.button("💬 واٹس ایپ", key=f"rwa_{row['id']}"):
                    st.session_state[f"show_rwa_{row['id']}"] = True
                if b5.button("🗑️ حذف کریں", key=f"rdel_{row['id']}"):
                    delete_repair(row['id'])
                    st.rerun()

                if st.session_state.get(f"show_rwa_{row['id']}"):
                    wa_msg = build_repair_whatsapp_message(
                        row['customer_name'], row['device_model'], row['fault_description'],
                        row['estimated_cost'], row['advance_paid'], row['balance']
                    )
                    wa_link = whatsapp_send_link(row['customer_phone'], wa_msg)
                    if wa_link:
                        st.link_button("💬 واٹس ایپ پر بھیجیں", wa_link, use_container_width=True)
                    else:
                        st.warning("موبائل نمبر درست نہیں لگ رہا۔")

                if st.session_state.get(f"show_rprint_{row['id']}"):
                    show_receipt(
                        "موبائل ریپیرنگ رسید", row['customer_name'], row['customer_phone'],
                        f"{row['device_model']} ({row['fault_description']})",
                        row['estimated_cost'],
                        extra=f"ایڈوانس: {row['advance_paid']:,.0f} | بقایا: {row['balance']:,.0f}"
                    )

# ============================================================
# PAGE: CASHBOOK
# ============================================================
elif page == "cashbook":
    st.subheader("💰 آمدن و اخراجات کا اندراج")

    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("cash_form", clear_on_submit=True):
            cash_type = st.selectbox("ٹائپ سلیکٹ کریں", [
                "Shop Expense", "EasyPaisa CashIn", "EasyPaisa CashOut",
                "JazzCash CashIn", "JazzCash CashOut"
            ], format_func=lambda x: {
                "Shop Expense": "اخراجات (Shop Expense)",
                "EasyPaisa CashIn": "ایزی پیسہ کیش ان",
                "EasyPaisa CashOut": "ایزی پیسہ کیش آؤٹ",
                "JazzCash CashIn": "جاز کیش کیش ان",
                "JazzCash CashOut": "جاز کیش کیش آؤٹ",
            }[x])
            amount = st.number_input("رقم (Amount)", min_value=0.0, step=50.0)
            description = st.text_input("تفصیل / ریمارکس", placeholder="مثلاً: چائے کا خرچہ یا دکان کا کرایہ")
            if st.form_submit_button("محفوظ کریں", use_container_width=True):
                if amount <= 0 or not description:
                    st.error("رقم اور تفصیل درج کریں۔")
                else:
                    add_cash_entry(cash_type, amount, description)
                    st.success("ٹرانزیکشن ریکارڈ کر دی گئی ہے!")
                    st.rerun()

    with col2:
        st.markdown("##### لین دین کی ہسٹری (Transaction History)")
        cash = get_cashbook()
        if cash.empty:
            st.info("ابھی کوئی ٹرانزیکشن موجود نہیں۔")
        else:
            for _, row in cash.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    color = "🔴" if row['type'] == 'Shop Expense' else "🟢"
                    c1.markdown(f"{color} **{row['type']}**")
                    c1.caption(row['description'])
                    c2.markdown(f"**PKR {row['amount']:,.0f}**")
                    c2.caption(row['entry_date'])
                    if c3.button("🗑️", key=f"cdel_{row['id']}"):
                        delete_cash_entry(row['id'])
                        st.rerun()

st.markdown("---")
st.caption("Ali Mobiles & Communication — Super POS System | Built with Streamlit")
