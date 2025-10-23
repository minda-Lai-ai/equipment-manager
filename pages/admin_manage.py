import streamlit as st
import sqlite3
import hashlib

# 權限檢查：非管理員自動跳出
if "authenticated" not in st.session_state or not st.session_state["authenticated"] or st.session_state["role"] != "管理員":
    st.error("未授權！僅限管理員使用本頁面。")
    st.stop()

def hash_password(pw):
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()

def log_user_action(username, action):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

st.title("🛡️ 帳號管理中心")
st.markdown("您可以管理所有使用者帳號密碼、刪除帳號並查詢操作紀錄。")

conn = sqlite3.connect("users.db")
c = conn.cursor()
users = c.execute("SELECT username, role FROM users").fetchall()

st.markdown("#### 帳號列表")
for username, role in users:
    st.write(f"帳號：{username} | 角色：{role}")
    if username != st.session_state["username"]:
        new_pw = st.text_input(f"新密碼（{username}）", key=f"pw_{username}")
        if st.button(f"修改密碼_{username}"):
            c.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_password(new_pw), username))
            conn.commit()
            log_user_action(st.session_state["username"], f"管理員修改密碼 {username}")
            st.success(f"{username} 密碼已更新")
        if st.button(f"刪除帳號_{username}"):
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            log_user_action(st.session_state["username"], f"管理員刪除帳號 {username}")
            st.success(f"已刪除帳號 {username}")

st.markdown("---")
st.markdown("#### 使用者操作紀錄")
logs = c.execute("SELECT username, action, timestamp FROM user_logs ORDER BY timestamp DESC LIMIT 200").fetchall()
for l_username, l_action, l_time in logs:
    st.write(f"{l_time} - {l_username} - {l_action}")
conn.close()
