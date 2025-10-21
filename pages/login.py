# pages/login.py
import streamlit as st
import time
from firebase_init import get_firestore_client
import json
import firebase_admin

# 頁面配置
st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 獲取 Firestore 客戶端（使用快取且帶錯誤診斷）
try:
    db = get_firestore_client()
except firebase_admin.exceptions.AppError:
    # 這是為了確保當 get_firestore_client 執行 st.stop() 時，下面的代碼不會嘗試執行。
    # 實際錯誤訊息會在 firebase_init.py 中被顯示。
    st.stop()


# ----------------------------------------
# 👤 登入區塊
# ----------------------------------------
st.subheader("使用者登入")
email_login = st.text_input("Email (登入)", key="email_login")
password_login = st.text_input("密碼 (登入)", type="password", key="password_login")

if st.button("登入", use_container_width=True):
    if not db:
        st.error("❌ 登入失敗：Firestore 客戶端未初始化。請檢查上面的連線錯誤。")
    elif not email_login or not password_login:
        st.error("❌ 請輸入完整的 Email 和密碼。")
    else:
        user_ref = db.collection("users").document(email_login)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # --- 最終診斷關鍵點 ---
            st.info(f"💡 嘗試登入 Email: {email_login}")
            st.info(f"💡 從 Firestore 讀取到的文件內容 (用於除錯): {json.dumps(user_data, ensure_ascii=False, indent=2)}")
            # --- 最終診斷關鍵點 ---

            # 密碼比對 (注意：這是明文比對，極度不安全)
            if user_data.get("password") == password_login:
                st.session_state["user"] = {
                    "email": email_login,
                    # 避免在 name 欄位不存在時出錯
                    "name": user_data.get("name", email_login.split('@')[0]), 
                    "role": user_data.get("role", "user")
                }
                st.success("✅ 登入成功，正在導向主頁...")
                time.sleep(0.5)
                # 導向主頁 (假設主頁是 main_dashboard.py)
                st.switch_page("main_dashboard.py")
            else:
                # 錯誤診斷：如果密碼長度不匹配，可能是隱藏字元
                db_password = user_data.get("password", "")
                st.error(f"❌ 登入失敗：密碼錯誤。 (輸入長度: {len(password_login)}, 資料庫長度: {len(db_password)})")
        else:
            st.error("❌ 登入失敗：此帳號在 Firestore 的 users collection 中不存在。")

st.markdown("---")

# ----------------------------------------
# 🆕 註冊新帳號 (測試用) 區塊
# ----------------------------------------
with st.expander("🆕 註冊新帳號 (測試用)"):
    email_reg = st.text_input("Email (註冊)", key="email_reg")
    password_reg = st.text_input("密碼 (註冊)", type="password", key="password_reg")
    name_reg = st.text_input("您的姓名", key="name_reg")
    
    # 預設角色為 user
    role_reg = st.selectbox("角色權限", ["user", "admin", "guest"], key="role_reg", index=0)

    if st.button("註冊新帳號", use_container_width=True):
        if not db:
            st.error("❌ 註冊失敗：Firestore 客戶端未初始化。")
        elif not email_reg or not password_reg or not name_reg:
            st.error("❌ 請輸入完整的 Email、密碼和姓名。")
        else:
            new_user_ref = db.collection("users").document(email_reg)
            
            if new_user_ref.get().exists:
                st.warning("⚠️ 此 Email 帳號已存在，請直接登入或使用其他 Email 註冊。")
            else:
                try:
                    # 寫入新使用者資料（明文密碼，再次提醒：極度不安全）
                    new_user_ref.set({
                        "email": email_reg,
                        "password": password_reg, # ⚠️ 這是明文密碼，強烈建議使用 Firebase Auth
                        "name": name_reg,
                        "role": role_reg,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    st.success(f"✅ 帳號註冊成功！Email: {email_reg}，請使用此帳號登入。")
                except Exception as e:
                    st.error(f"❌ 註冊失敗：寫入 Firestore 時發生錯誤。請檢查 Firestore 規則。錯誤詳情: {e}")

st.markdown("---")
st.caption("🚨 **安全提醒：** 本應用程式的登入機制將密碼以明文形式儲存在 Firestore 中。這在生產環境下**極度不安全**。建議切換到 Firebase Authentication 或 Streamlit Authenticator。")
