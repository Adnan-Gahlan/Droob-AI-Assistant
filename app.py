import streamlit as st
import google.generativeai as genai
import os
import re

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="دروب الياسين | المساعد الذكي", page_icon="✈️", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Tajawal', sans-serif; }
    .main-header { font-size: 3rem; color: #1E3A8A; text-align: center; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); margin-bottom: 0px;}
    .sub-header { font-size: 1.3rem; color: #D97706; text-align: center; margin-top: 5px; margin-bottom: 30px; font-weight: 500;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. محرك التوجيه الذكي
# ==========================================
def get_fast_reply(text):
    text_clean = text.strip()
    if re.search(r'(سلام|السلام عليكم|مرحبا|هلا|صباح الخير|مساء الخير)', text_clean):
        return "وعليكم السلام ورحمة الله وبركاته! يا حياك الله في مكتب دروب الياسين. كيف أقدر أسهل سفرك اليوم؟ 😊✈️"
    if re.search(r'(كيف حالك|اخبارك|كيفك|شلونك|ايش الاخبار|كيف الحال)', text_clean):
        return "الحمد لله بخير ونعمة! أنت كيف حالك يا غالي؟ عساني أقدر أخدمك في ترتيب رحلتك اليوم 🌍"
    return None

# ==========================================
# 3. قراءة البيانات
# ==========================================
@st.cache_data
def load_knowledge_base():
    file_path = "travel_data.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "تنبيه للموظف: ملف الأسعار غير موجود."

knowledge_base_text = load_knowledge_base()

# ==========================================
# 4. محرك الذكاء الاصطناعي
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("تنبيه: مفتاح API غير متوفر في إعدادات السيرفر.")

system_instruction = f"""
أنت مساعد افتراضي ذكي وموظف خدمة عملاء محترف تعمل لدى مكتب 'دروب الياسين للسفريات والسياحة' في اليمن.
لديك قاعدة بيانات رسمية تحتوي على أسعار المكتب. استخرج إجاباتك وأسعارك من هذا النص فقط:
---------------------------
{knowledge_base_text}
---------------------------
قواعد صارمة جداً:
1. لا تستخدم اللغة الإنجليزية أبداً.
2. استخرج السعر بدقة من النص. إذا كان غير موجود، اعتذر بلباقة وحول الطلب للموظف.
3. لا تخترع أسعاراً من خارج الملف.
"""

@st.cache_resource
def load_ai_model(_instruction):
    return genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=_instruction)

model = load_ai_model(system_instruction)

# ==========================================
# تهيئة الذاكرة (تم إصلاح الترتيب هنا لتجنب الخطأ)
# ==========================================
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": "يا حياكم الله! 🙋‍♂️ أنا المساعد الذكي لمكتب دروب الياسين. كيف أقدر أخدمك اليوم؟"}
    ]

# ==========================================
# 5. الشريط الجانبي
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color:#1E3A8A;'>دروب الياسين 🌍</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2059/2059043.png", width=120, use_container_width=True)
    st.markdown("---")
    st.success("🟢 النظام متصل ومستقر")
    st.markdown("### 💡 أسئلة شائعة:")
    if st.button("✈️ عروض الطيران"):
        st.session_state.quick_prompt = "ايش عروض الطيران اللي عندكم؟"
    if st.button("🕋 باقات العمرة"):
        st.session_state.quick_prompt = "بكم باقات العمرة؟"
    
    st.markdown("---")
    # زر التحميل المصلح
    if len(st.session_state.messages) > 1:
        chat_history_text = "تفاصيل استفساراتك من مكتب دروب الياسين:\n\n"
        for msg in st.session_state.messages[1:]:
            role = "العميل" if msg["role"] == "user" else "الموظف الآلي"
            chat_history_text += f"{role}: {msg['content']}\n"
        
        st.download_button(
            label="📥 تحميل تفاصيل المحادثة (إيصال)",
            data=chat_history_text,
            file_name="Droob_Booking_Details.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==========================================
# 6. الواجهة الرئيسية
# ==========================================
st.markdown("<p class='main-header'>✈️ المساعد الذكي لخدمة العملاء</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>خطط لرحلتك القادمة بثقة وسهولة</p>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("اكتب استفسارك هنا...")
if "quick_prompt" in st.session_state:
    user_input = st.session_state.quick_prompt
    del st.session_state.quick_prompt

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        fast_reply = get_fast_reply(user_input)
        
        if fast_reply:
            message_placeholder.markdown(fast_reply)
            st.session_state.messages.append({"role": "assistant", "content": fast_reply})
        else:
            with st.spinner("جاري فحص قاعدة البيانات... 🔍"):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    reply = response.text
                    message_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    message_placeholder.error("⚠️ عذراً، هناك مشكلة في الاتصال. يرجى المحاولة لاحقاً.")
