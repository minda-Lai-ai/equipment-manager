# pages/login.py

import streamlit as st
import time
from firebase_init import get_firestore_client
import json
import firebase_admin
from firebase_admin import firestore
# 關鍵修正：從 google.api_core 匯入異常，這在 Streamlit 環境中更穩定
from google.api_core.exceptions import PermissionDenied, GoogleAPICallError, NotFound, InternalServerError

# 頁面配置
st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 獲取 Firestore 客戶端（使用快取且帶錯誤診斷）
try:
    db = get_firestore_client()
except Exception:
    st.stop()


# ----------------------------------------
# 👤 登入區塊
# ----------------------------------------
st.subheader("使用者登入")
email_login = st.text_input("Email (登入)", key="email_login")
password_login = st.text_input("密碼 (登入)", type="password", key="password_login")

if st.button("登入", use_container_width=True):
    if not email_login or not password_login:
        st.error("❌ 請輸入完整的 Email 和密碼。")
    else:
        try:
            # 嘗試執行 Firestore 讀取操作
            user_ref = db.collection("users").document(email_login)
            user_doc = user_ref.get() # 這裡可能會卡住或失敗

            if user_doc.exists:
                user_data = user_doc.to_dict()
                
                # --- 除錯資訊 ---
                st.info(f"💡 嘗試登入 Email: {email_login}")
                st.info(f"💡 從 Firestore 讀取到的文件內容 (用於除錯): {json.dumps(user_data, ensure_ascii=False, indent=2)}")
                # --- 除錯資訊 ---

                # 密碼比對
                if user_data.get("password") == password_login:
                    st.session_state["user"] = {
                        "email": email_login,
                        "name": user_data.get("name", email_login.split('@')[0]), 
                        "role": user_data.get("role", "user")
                    }
                    st.success("✅ 登入成功，正在導向主頁...")
                    time.sleep(0.5)
                    st.switch_page("main_dashboard.py")
                else:
                    db_password = user_data.get("password", "")
                    st.error(f"❌ 登入失敗：密碼錯誤。 (輸入長度: {len(password_login)}, 資料庫長度: {len(db_password)})")
            else:
                st.error("❌ 登入失敗：此帳號在 Firestore 的 users collection 中不存在。")
        
        # 捕捉 Firestore 操作特定的錯誤 (使用更通用的 API 異常)
        except PermissionDenied:
            st.error("❌ 登入失敗：Firestore 拒絕了操作。請檢查您的 **Firestore 安全規則**。")
        except GoogleAPICallError as e:
            st.error(f"❌ 網路連線或 API 呼叫錯誤。請檢查部署環境的網路狀態或金鑰。錯誤詳情: {e}")
        except InternalServerError:
            st.error("❌ 登入失敗：Google 服務內部錯誤。請稍後再試。")
        except Exception as e:
            st.error(f"❌ 登入時發生未預期錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")

st.markdown("---")

# ----------------------------------------
# 🆕 註冊新帳號 (測試用) 區塊
# ----------------------------------------
with st.expander("🆕 註冊新帳號 (測試用)"):
    email_reg = st.text_input("Email (註冊)", key="email_reg")
    password_reg = st.text_input("密碼 (註冊)", type="password", key="password_reg")
    name_reg = st.text_input("您的姓名", key="name_reg")
    role_reg = st.selectbox("角色權限", ["user", "admin", "guest"], key="role_reg", index=0)

    if st.button("註冊新帳號", use_container_width=True):
        if not email_reg or not password_reg or not name_reg:
            st.error("❌ 請輸入完整的 Email、密碼和姓名。")
        else:
            try:
                new_user_ref = db.collection("users").document(email_reg)
                
                if new_user_ref.get().exists:
                    st.warning("⚠️ 此 Email 帳號已存在，請直接登入或使用其他 Email 註冊。")
                else:
                    # 寫入新使用者資料
                    new_user_ref.set({
                        "email": email_reg,
                        "password": password_reg,
                        "name": name_reg,
                        "role": role_reg,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    st.success(f"✅ 帳號註冊成功！Email: {email_reg}，請使用此帳號登入。")
            except PermissionDenied:
                st.error("❌ 註冊失敗：Firestore 拒絕了操作。請檢查您的 **Firestore 安全規則**。")
            except GoogleAPICallError as e:
                st.error(f"❌ 網路連線或 API 呼叫錯誤。錯誤詳情: {e}")
            except InternalServerError:
                st.error("❌ 註冊失敗：Google 服務內部錯誤。請稍後再試。")
            except Exception as e:
                st.error(f"❌ 註冊時發生未預期錯誤。錯誤類型: {type(e).__name__}，詳情: {e}")

