import streamlit as st
import hashlib
from supabase import create_client

# 權限檢查
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("尚未登入或登入已逾時，請回主畫面重新登入。")
    st.stop()
if st.session_state.get("role") != "管理員":
    st.error("權限不足：僅限管理員！")
    st.stop()

@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

st.title("🛡️ 帳號管理中心")

# 新增使用者
with st.expander("➕ 新增使用者"):
    new_username = st.text_input("新帳號", key="add_user")
    new_pw = st.text_input("新密碼", type="password", key="add_pw")
    new_role = st.selectbox("角色", ["一般使用者", "管理員"], key="add_role")
    if st.button("新增"):
        try:
            supabase.table("users").insert({
                "username": new_username,
                "password_hash": hash_password(new_pw),
                "role": new_role
            }).execute()
            st.success("新增成功！")
        except Exception as e:
            st.error(f"新增失敗：{e}")

# 使用者列表
st.markdown("---")
st.subheader("使用者列表與維護")
users = supabase.table("users").select("*").execute().data

for user in users:
    username = user["username"]
    role = user["role"]
    st.write(f"帳號：{username}　|　角色：{role}")
    if username != st.session_state["username"]:
        with st.expander(f"管理 [{username}]"):
            ch_pw = st.text_input("新密碼", type="password", key=f"pw_{username}")
            if st.button("修改密碼", key=f"chg_{username}"):
                supabase.table("users").update({
                    "password_hash": hash_password(ch_pw)
                }).eq("username", username).execute()
                st.success("密碼已變更")
            if st.button("刪除此帳號", key=f"del_{username}"):
                supabase.table("users").delete().eq("username", username).execute()
                st.success("此帳號已刪除")

# 操作紀錄
st.markdown("---")
st.subheader("🔎 使用者動作紀錄")
logs = supabase.table("user_logs").select("*").order("timestamp", desc=True).limit(200).execute().data
for log in logs:
    st.write(f"{log['timestamp']} - {log['username']} - {log['action']}")
