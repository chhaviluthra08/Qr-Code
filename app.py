import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, date
import os
import qrcode
import io
from PIL import Image



DB_name = "QrApp.db"

def get_conn():
    return sqlite3.connect(DB_name, check_same_thread = False)

#-----------------CREATING TABLES--------------------#


def create_tables():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEST UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user'
            )
            """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS qrs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            qr_text TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts(
        username TEXT,
        attempt_time TEXT
    )
    """)
    conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def record_failed_attempt(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO login_attempts(username, attempt_time) VALUES (?, ?)",
                (username, datetime.now().isoformat()))
    conn.commit()

def failed_attempts_today(username):
    conn = get_conn()
    cur = conn.cursor()
    today = date.today().isoformat()
    cur.execute("""
    SELECT COUNT(*) FROM login_attempts 
    WHERE username = ? AND DATE(attempt_time) = ?
    """, (username, today))
    return cur.fetchone()[0]

#----------------AUTH SYSTEM--------------#

def register_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    try:
        username = username.strip().lower()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hash_password(password)))
        conn.commit()
        print("✅ Registered:", username)
        return True
    except sqlite3.IntegrityError as e:
        print("❌ IntegrityError:", e)
        return False
    except Exception as e:
        print("❌ Other Error during registration:", e)
        return False

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    try: 
        cur.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                (username, hash_password(password)))
        return cur.fetchone()
    except Exception as e:
        print("Login error: ", e)
        return None

# --------------- SESSION SETUP ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.role = None

# --------------- UI ----------------------#
create_tables()
#using html we align the headings to the center
st.markdown(
    """
    <h1 style='text-align: center; color: #3E2723; font-size: 48px;'>
        QR CODE APP
    </h1>
    """,
    unsafe_allow_html=True
)
#we use break tags to provid some space in between heading and form
st.markdown("""
    <br><br>
    """,
    unsafe_allow_html=True)

menu = st.sidebar.selectbox("Navigation", ["Login", "Register"])

if menu == "Register":
    st.markdown("""
    <h1 style='text-align: center; color: #3E2723; font-size: 28px;'>
        Register
    </h1>
    """,
    unsafe_allow_html=True
    )
    new_user = st.text_input("Username(NO CAPITAL LETTERS)")
    new_user = new_user.strip()
    new_pass = st.text_input("Password", type ="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("Account Created!! Now Log in.")
        else:
            st.error("Username exists!") 
elif menu == "Login":
    st.markdown("""
    <h1 style='text-align: center; color: #3E2723; font-size: 28px;'>
        Login
    </h1>
    """,
    unsafe_allow_html=True
    )
    user = st.text_input("Username")
    user = user.strip()
    passwd = st.text_input("Password", type = "password")
    if st.button("Login"):
        if failed_attempts_today(user) >= 5:
            st.error("Too many failed attempts today. Try Again tomorrow.")
        else:
            # View existing usernames for debug
            if user == "admin" and passwd == "_root_101_":
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("SELECT username FROM users")
                all_users = cur.fetchall()
                st.markdown("### Existing Users in DB")
                st.write([user[0] for user in all_users])
            result = login_user(user, passwd)
            if result:
                st.session_state.logged_in = True
                st.session_state.username = result[1]
                st.session_state.user_id = result[0]
                st.session_state.role = result[3]
                st.success(f"Welcome, {user}!")
            else:
                st.error("Invalid credentials.")
                record_failed_attempt(user)


if st.session_state.logged_in:
    #-------------- Generate Qr ------------------#
    if st.session_state.role != "admin":
        #horizontal line
        st.markdown("""
        <br><hr><br>
        """,
        unsafe_allow_html=True)
    
        #title
        st.markdown(
        """
        <h1 style='text-align: center; color: #3E2723; font-size: 38px;'>
            Qr Code Dashboard
        </h1>
        """,
        unsafe_allow_html=True
        )
        #space
        st.markdown("""
        <br><br>
        """,
        unsafe_allow_html=True)
        st.markdown("""
        <h1 style='text-align: center; color: #3E2723; font-size: 28px;'>
            Generate a Qr
        </h1>
        """,
        unsafe_allow_html=True
        )
        qr_text = st.text_input("Enter a text or link to generate a QrCode")
        save_qr = st.checkbox("Save this Qr to my history")
    
        if st.button("Generate Qr Code"):
            if qr_text.strip() == "":
                st.warning("Please enter something to generate Qr Code")
            else:
                #generate qr code (PIL Image)
                qr = qrcode.make(qr_text)
                #Convert PIL image to bytes for streamlit display
                img_buffer = io.BytesIO()
                qr.save(img_buffer, format = 'PNG')
                img_buffer.seek(0)
                st.image(img_buffer, caption = "Your Qr Code")
            
                if save_qr:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO qrs(user_id, qr_text, created_at) VALUES (?, ?, ?)",
                                (st.session_state.user_id, qr_text, datetime.now().isoformat()))
                    conn.commit()
                    st.success("Qr Code saved successfully!")
    
#-------------------- Qr History Viewer -------------------- #
st.markdown("""
    <br><hr><br>
    """,
    unsafe_allow_html=True)
st.markdown(
    """
    <h1 style='text-align: center; color: #3E2723; font-size: 38px;'>
        Qr Code History
    </h1>
    """,
    unsafe_allow_html=True
)

conn = get_conn()
cur = conn.cursor()



def display_qr_as_image(text):
    # Generate QR as bytes
    qr_img = qrcode.make(text)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    st.image(buf, width=200)

if st.session_state.role == "admin":
    st.info("Admin Mode: Showing all users' Qr History")
    cur.execute("""
        SELECT qrs.id, users.username, qrs.qr_text, qrs.created_at
        FROM qrs
        JOIN users ON qrs.user_id = users.id
        ORDER BY qrs.created_at DESC
    """)
    records = cur.fetchall()

    for id, user, text, time in records:
        st.markdown(f"**User:** `{user}`")
        st.markdown(f"`{text}`")
        display_qr_as_image(text)
        st.markdown(f"_`{time}`_")
        st.markdown("___")

    # Add delete button
    delete_button_key = f"delete_{id}"
    
    # Inside your delete logic:
    if st.button("🗑️ Delete", key=delete_button_key):
        cur.execute("DELETE FROM qrs WHERE id = ?", (id,))
        conn.commit()
        st.success("QR Code deleted successfully!")
    
        # Trigger a rerun without importing anything
        st.session_state["_rerun_flag"] = not st.session_state.get("_rerun_flag", False)
        st.experimental_set_query_params(rerun=str(st.session_state["_rerun_flag"]))  
        st.markdown("___")
else:
    cur.execute("""
        SELECT qr_text, created_at FROM qrs
        WHERE user_id = ? ORDER BY created_at DESC
    """, (st.session_state.user_id,))
    records = cur.fetchall()
    if not records:
        st.info("No Qr Codes saved yet.")
    else:
        for text, time in records:
            st.markdown(f"`{text}`")
            display_qr_as_image(text)
            st.markdown(f"_{time}_")
            st.markdown("___")
    