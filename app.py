import streamlit as st
import google.generativeai as genai
import os
import re

# 1. إعدادات الصفحة والهوية البصرية (Luxury UI/UX)

st.set_page_config(page_title="دروب الياسين | المساعد الذكي", page_icon="✈️", layout="wide")

# استدعاء خط "تجوال" الفخم وتنسيقات CSS احترافية
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Tajawal', sans-serif; }
    .main-header { font-size: 3rem; color: #1E3A8A; text-align: center; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); margin-bottom: 0px;}
    .sub-header { font-size: 1.3rem; color: #D97706; text-align: center; margin-top: 5px; margin-bottom: 30px; font-weight: 500;}
    .stAlert { border-radius: 10px; }
    .chat-status { font-size: 0.9rem; color: #888; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. محرك التوجيه الذكي (الردود اللحظية)

def get_fast_reply(text):
    text_clean = text.strip()
    
    # 1. التقاط التحيات باستخدام التعابير المنطقية
    if re.search(r'(سلام|السلام عليكم|مرحبا|هلا|صباح الخير|مساء الخير)', text_clean):
        return "وعليكم السلام ورحمة الله وبركاته! يا حياك الله في مكتب دروب الياسين. كيف أقدر أسهل سفرك اليوم؟ 😊✈️"
    
    # 2. التقاط السؤال عن الحال
    if re.search(r'(كيف حالك|اخبارك|كيفك|شلونك|ايش الاخبار|كيف الحال)', text_clean):
        return "الحمد لله بخير ونعمة! أنت كيف حالك يا غالي؟ عساني أقدر أخدمك في ترتيب رحلتك اليوم 🌍"
    
    return None

# 3. نظام قراءة قاعدة البيانات (RAG System)

@st.cache_data
def load_knowledge_base():
    file_path = "travel_data.txt"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "تنبيه للموظف: ملف الأسعار (travel_data.txt) غير موجود."

knowledge_base_text = load_knowledge_base()

# 4. محرك الذكاء الاصطناعي (Gemini Brain)
# استدعاء المفتاح بشكل آمن من إعدادات السيرفر
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

system_instruction = f"""
أنت مساعد افتراضي ذكي وموظف خدمة عملاء محترف تعمل لدى مكتب 'دروب الياسين للسفريات والسياحة' في اليمن.
مهمتك الرد على استفسارات العملاء بلباقة، واحترافية، ولهجة يمنية بيضاء مفهومة.

لديك قاعدة بيانات رسمية تحتوي على أسعار المكتب. استخرج إجاباتك وأسعارك من هذا النص فقط:
---------------------------
{knowledge_base_text}
---------------------------

قواعد صارمة جداً:
1. لا تستخدم اللغة الإنجليزية أبداً ولا تظهر كلمات مثل (THOUGHT أو Plan).
2. استخرج السعر بدقة من النص. إذا كان غير موجود، اعتذر بلباقة وحول الطلب للموظف المختص.
3. لا تخترع أسعاراً من خارج الملف.
4. كن منظماً، استخدم نقاطاً للترتيب، وضع إيموجي مناسبة (✈️, 🚌, 🛂, 🕋).
"""

@st.cache_resource
def load_ai_model(_instruction):
    return genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=_instruction
    )

model = load_ai_model(system_instruction)

# 5. الشريط الجانبي (Sidebar & Quick Actions)

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color:#1E3A8A;'>دروب الياسين 🌍</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2059/2059043.png", width=120, use_container_width=True)
    
    st.markdown("---")
    st.success("🟢 النظام متصل ومستقر")
    st.info("📍 اليمن - صنعاء (مذبح)\n\n⏰ 8:00 صباحاً - 8:00 مساءً")
    
    st.markdown("---")
    st.markdown("### 💡 أسئلة شائعة:")
    # أزرار مساعدة للعميل تقوم بكتابة السؤال تلقائياً
    if st.button("✈️ عروض الطيران"):
        st.session_state.quick_prompt = "ايش عروض الطيران اللي عندكم؟"
    if st.button("🕋 باقات العمرة"):
        st.session_state.quick_prompt = "بكم باقات العمرة؟"
    if st.button("🛂 استخراج الجوازات"):
        st.session_state.quick_prompt = "بكم تجديد الجواز المستعجل؟"

# 6. الواجهة الرئيسية للمحادثة
st.markdown("<p class='main-header'>✈️ المساعد الذكي لخدمة العملاء</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>خطط لرحلتك القادمة بثقة وسهولة</p>", unsafe_allow_html=True)

# إدارة الذاكرة والمحادثة
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": "يا حياكم الله! 🙋‍♂️ أنا المساعد الذكي لمكتب دروب الياسين. كيف أقدر أخدمك اليوم؟"}
    ]

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# استقبال السؤال (سواء من المربع أو من الأزرار الجانبية)
user_input = st.chat_input("اكتب استفسارك هنا... (مثال: بكم تذكرة القاهرة؟)")

# تفعيل الإدخال من الأزرار الجانبية
if "quick_prompt" in st.session_state:
    user_input = st.session_state.quick_prompt
    del st.session_state.quick_prompt

# معالجة الطلب
if user_input:
    # عرض رسالة العميل
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # معالجة الرد
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 1. التوجيه الذكي: هل هي مجرد تحية؟
        fast_reply = get_fast_reply(user_input)
        
        if fast_reply:
            message_placeholder.markdown(fast_reply)
            st.session_state.messages.append({"role": "assistant", "content": fast_reply})
            
        # 2. إذا لم تكن تحية، اذهب للمحرك الرئيسي لفحص البيانات
        else:
            with st.spinner("جاري فحص قاعدة البيانات... 🔍"):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    reply = response.text
                    message_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    # رسالة خطأ ذكية في حال توقف الـ VPN
                    error_msg = """
                    ⚠️ **عذراً، يبدو أن هناك انقطاعاً في الاتصال بالشبكة المركزية.** \n*يرجى التحقق من اتصال الإنترنت أو التأكد من تفعيل خدمة الـ VPN والمحاولة مرة أخرى.*
                    """
                    message_placeholder.error(error_msg)