import streamlit as st
from firebase_init import get_firestore

st.set_page_config(page_title="🔐 使用者登入", layout="centered")
st.title("🔐 使用者登入")

# 🚨 安全性警告 (強烈建議您閱讀並修改此處)
st.warning(
    "⚠️ **安全警告：** 您目前是以手動方式將使用者密碼直接存入 Firestore，"
    "這是一個**嚴重的安全風險**。在生產環境中，**強烈建議**您改用 **Firebase Authentication** "
    "服務來安全地處理使用者登入和密碼雜湊。"
)

db = get_firestore()  # ✅ 取得 Firestore 實例

# --- 登入表單 ---
st.header("🔑 登入")
with st.form("login_form"):
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("密碼", type="password", key="login_password")
    login_button = st.form_submit_button("登入")

if login_button:
    if not login_email or not login_password:
        st.error("❌ Email 和密碼皆為必填。")
    else:
        # 核心登入邏輯：檢查 Firestore 文件
        user_ref = db.collection("users").document(login_email)
        try:
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                
                # 手動密碼驗證 (請注意此處的安全性風險)
                if user_data.get("password") == login_password:
                    # 登入成功，設定 Session State
                    st.session_state["user"] = {
                        "email": login_email,
                        "name": user_data.get("name", "未命名使用者"),
                        "role": user_data.get("role", "user")
                    }
                    st.success("✅ 登入成功，正在導向主頁…")
                    
                    # 使用 Streamlit 的 Page Title 來導向，確保主頁檔案存在
                    st.switch_page("🧭 設備管理主控面板")
                else:
                    st.error("❌ 登入失敗，密碼錯誤。")
            else:
                st.error("❌ 登入失敗，此帳號不存在。")
        except Exception as e:
            st.error(f"❌ 登入時發生 Firestore 錯誤: {e}")


st.markdown("---")

# --- 註冊區塊 (僅供測試用) ---
st.header("🆕 註冊新帳號 (測試用)")
with st.expander("點擊展開註冊表單"):
    with st.form("register_form"):
        reg_email = st.text_input("Email (作為帳號)", key="reg_email")
        reg_password = st.text_input("密碼", type="password", key="reg_password")
        reg_name = st.text_input("名稱", key="reg_name", value="測試用戶")
        register_button = st.form_submit_button("註冊")

    if register_button:
        if not reg_email or not reg_password:
            st.error("Email 和密碼皆為必填。")
        else:
            new_user_ref = db.collection("users").document(reg_email)
            if new_user_ref.get().exists:
                st.error("❌ 註冊失敗，此 Email 已經存在。")
            else:
                try:
                    new_user_ref.set({
                        "email": reg_email,
                        "password": reg_password, # 🚨 密碼以明文儲存，強烈不建議用於生產環境
                        "name": reg_name,
                        "role": "user",
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                    st.success(f"🎉 帳號 {reg_email} 註冊成功！您現在可以登入了。")
                except Exception as e:
                    st.error(f"❌ 註冊時發生 Firestore 錯誤: {e}")
