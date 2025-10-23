import streamlit as st
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def log_user_action(username, action):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

# 僅限管理員進入，否則阻擋    
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入，請先登入。")
    st.stop()
if st.session_state.get("role") != "管理員":
    st.error("權限不足：僅限管理員！")
    st.stop()

st.title("🛡️ 帳號管理中心")
conn = sqlite3.connect("users.db")
c = conn.cursor()

# --- 新增帳號 ---
with st.expander("➕ 新增使用者"):
    new_username = st.text_input("新帳號", key="add_user")
    new_pw = st.text_input("新密碼", type="password", key="add_pw")
    new_role = st.selectbox("角色", ["一般使用者", "管理員"], key="add_role")
    if st.button("新增"):
        c.execute("SELECT 1 FROM users WHERE username = ?", (new_username,))
        if c.fetchone():
            st.warning("帳號已存在")
        elif not new_username or not new_pw:
            st.warning("請填帳號密碼")
        else:
            c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                      (new_username, hash_password(new_pw), new_role))
            conn.commit()
            log_user_action(st.session_state["username"], f"新增用戶({new_username})")
            st.success("新增成功！")


st.markdown("---")
st.subheader("使用者列表與維護")

users = c.execute("SELECT username, role FROM users").fetchall()
for username, role in users:
    st.write(f"帳號：{username}　|　角色：{role}")
    if username != st.session_state["username"]:
        with st.expander(f"管理 [{username}]"):
            # 修改密碼
            ch_pw = st.text_input("新密碼", type="password", key=f"pw_{username}")
            if st.button("修改密碼", key=f"chg_{username}"):
                if not ch_pw:
                    st.warning("請輸入新密碼")
                else:
                    c.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_password(ch_pw), username))
                    conn.commit()
                    log_user_action(st.session_state["username"], f"修改 {username} 密碼")
                    st.success("密碼已變更")
            # 刪除帳號
            if st.button("刪除此帳號", key=f"del_{username}"):
                c.execute("DELETE FROM users WHERE username=?", (username,))
                conn.commit()
                log_user_action(st.session_state["username"], f"刪除 {username}")
                st.success("此帳號已刪除")

st.markdown("---")
st.subheader("🔎 使用者動作紀錄")
logs = c.execute(
    "SELECT username, action, timestamp FROM user_logs ORDER BY timestamp DESC LIMIT 200"
).fetchall()
for l_username, l_action, l_time in logs:
    st.write(f"{l_time} - {l_username} - {l_action}")

conn.close()
