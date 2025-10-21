# pages/login.py
import streamlit as st
import time
from firebase_init import get_firestore_client # 引用快取後的 client

# 設定頁面配置
st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 嘗試取得 Firestore 實例
db = get_firestore_client()  

# --------------------
# 登入區塊
# --------------------
st.subheader("使用者登入")

email = st.text_input("Email", key="login_email")
password = st.text_input("密碼", type="password", key="login_password")

if st.button("登入", use_container_width=True):
    if not email or not password:
        st.error("請輸入 Email 和密碼")
    else:
        user_ref = db.collection("users").document(email)
        try:
            user_doc = user_ref.get()
            
            # --- 除錯資訊 ---
            st.info(f"💡 正在嘗試讀取文件 ID: {email}")
            # --- 除錯資訊 ---

            if user_doc.exists:
                user_data = user_doc.to_dict()

                # --- 除錯資訊 ---
                st.info(f"💡 從 Firestore 讀取到的文件內容 (用於比對): {json.dumps(user_data, indent=2)}")
                # --- 除錯資訊 ---
                
                # 密碼比對 (注意：此處為明文比對，應使用 Firebase Auth 改善)
                if user_data.get("password") == password:
                    st.session_state["user"] = {
                        "email": email,
                        "name": user_data.get("name", "未命名"),
                        "role": user_data.get("role", "user")
                    }
                    st.success("✅ 登入成功，正在導向主頁…")
                    time.sleep(1) 
                    st.switch_page("main_dashboard.py") # 導向主入口檔案

                else:
                    st.error("❌ 登入失敗：密碼錯誤。")
            else:
                st.error("❌ 登入失敗：此帳號在 Firestore 的 users collection 中不存在。")

        except Exception as e:
            st.error(f"❌ 登入時發生 Firestore 錯誤：{e}")


st.markdown("---")

# --------------------
# 註冊區塊 (測試用，可選)
# --------------------
with st.expander("註冊新帳號 (測試用，僅適用於手動密碼管理)"):
    st.warning("⚠️ 安全性警示：此註冊功能將密碼儲存為明文。正式環境請使用 Firebase Authentication。")
    new_email = st.text_input("新 Email (帳號)", key="reg_email")
    new_password = st.text_input("新密碼", type="password", key="reg_password")
    new_name = st.text_input("您的姓名", key="reg_name")
    new_role = st.selectbox("角色", ["user", "admin"], key="reg_role")

    if st.button("註冊", key="register_button", use_container_width=True):
        if not new_email or not new_password:
            st.error("Email 和密碼不能為空")
        else:
            new_user_ref = db.collection("users").document(new_email)
            
            if new_user_ref.get().exists:
                st.warning(f"此 Email 帳號 ({new_email}) 已存在。")
            else:
                try:
                    new_user_data = {
                        "email": new_email,
                        "password": new_password, # 密碼以明文儲存 (不安全)
                        "name": new_name,
                        "role": new_role
                    }
                    new_user_ref.set(new_user_data)
                    st.success(f"✅ 註冊成功！請使用 {new_email} 登入。")
                except Exception as e:
                    st.error(f"❌ 註冊時發生 Firestore 錯誤：{e}")
