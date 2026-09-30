import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# إعدادات الصفحة لتناسب شاشة الهاتف
st.set_page_config(page_title="مدير مشتركين الإنترنت", page_icon="🌐", layout="centered")

# ملف حفظ البيانات
DATA_FILE = "subscribers.csv"

# دالة لتحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            return pd.DataFrame(columns=["الاسم", "رقم الهاتف", "تاريخ الانتهاء"])
    return pd.DataFrame(columns=["الاسم", "رقم الهاتف", "تاريخ الانتهاء"])

# دالة لحفظ البيانات
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# تحميل البيانات الحالية
if 'df' not in st.session_state:
    st.session_state.df = load_data()

st.title("📱 نظام إدارة وتنبيه المشتركين")

# --- القسم الأول: إضافة مشترك جديد ---
with st.expander("➕ إضافة مشترك جديد", expanded=True):
    name = st.text_input("اسم المشترك")
    phone = st.text_input("رقم الهاتف (مع مفتاح الدولة مثلاً 9647700000000)")
    end_date = st.date_input("تاريخ انتهاء الاشتراك", datetime.today())
    
    if st.button("حفظ المشترك"):
        if name and phone:
            # تنظيف الرقم من أي مسافات أو علامة +
            clean_phone = str(phone).replace("+", "").strip()
            new_user = pd.DataFrame([[name, clean_phone, end_date.strftime('%Y-%m-%d')]], columns=["الاسم", "رقم الهاتف", "تاريخ الانتهاء"])
            st.session_state.df = pd.concat([st.session_state.df, new_user], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"تم حفظ المشترك {name} بنجاح!")
            st.rerun()
        else:
            st.error("الرجاء إدخال الاسم ورقم الهاتف!")

# --- القسم الثاني: عرض المشتركين والتنبيهات ---
st.subheader("📋 قائمة المشتركين والتنبيه عبر الواتساب")

if not st.session_state.df.empty:
    today = datetime.today().date()
    
    for index, row in st.session_state.df.iterrows():
        try:
            sub_date = datetime.strptime(str(row["تاريخ الانتهاء"]), '%Y-%m-%d').date()
            days_left = (sub_date - today).days
        except:
            days_left = 999
        
        # تنسيق طريقة العرض لكل مشترك
        with st.container():
            col1, col2 = st.columns()
            
            with col1:
                st.write(f"👤 **{row['الاسم']}** | 📞 {row['رقم الهاتف']}")
                if days_left < 0:
                    st.caption(f"❌ منتهي منذ {-days_left} يوم ({row['تاريخ الانتهاء']})")
                elif days_left <= 3:
                    st.caption(f"⚠️ ينتهي قريباً! متبقي {days_left} أيام ({row['تاريخ الانتهاء']})")
                else:
                    st.caption(f"✅ مستمر: متبقي {days_left} يوم ({row['تاريخ الانتهاء']})")
            
            with col2:
                # تجهيز نص الرسالة وتشفيرها للرابط
                msg = f"مرحباً سيد {row['الاسم']}، نود تذكيرك بأن اشتراك الإنترنت الخاص بك سينتهي بتاريخ {row['تاريخ الانتهاء']}. يرجى التجديد لضمان استمرار الخدمة."
                encoded_msg = urllib.parse.quote(msg)
                whatsapp_url = f"https://wa.me{row['رقم الهاتف']}?text={encoded_msg}"

                
                # زر يفتح الواتساب مباشرة
                st.link_button("💬 تنبيه", whatsapp_url)
            st.divider()
else:
    st.info("لا يوجد مشتركين مضافين حالياً.")
