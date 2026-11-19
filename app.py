
import re
import hashlib
from urllib.parse import urlparse
from difflib import SequenceMatcher
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="HISN AI | Cyber Shield", page_icon="🛡️", layout="wide")

# --- Styling ---
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#071426 0%,#0b1d34 55%,#102744 100%); color:#eef5ff;}
[data-testid="stSidebar"] {background:#09182b;}
h1,h2,h3,p,li,label {color:#eef5ff !important;}
.hero {padding:24px 28px;border:1px solid #294767;border-radius:20px;background:linear-gradient(110deg,#102b4a,#0b1b30);margin-bottom:18px;}
.hero small {color:#9ec7f4;}
.metric {background:#10243c;border:1px solid #294767;border-radius:15px;padding:15px;}
.result {background:#10243c;border:1px solid #294767;border-radius:16px;padding:18px;}
.muted {color:#a9bfd8;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <small>AI-ASSISTED CYBERCRIME PREVENTION • PROTOTYPE</small>
  <h1 style="font-size:42px;margin:5px 0;">🛡️ HISN AI</h1>
  <div style="font-size:18px;color:#c9ddf4;">Your AI-Powered Cyber Shield</div>
  <p style="margin-top:12px;color:#b7cce4;">حل تجريبي لتحليل مؤشرات الاحتيال، توعية المستخدم، وربط الرسائل المتشابهة.</p>
</div>
""", unsafe_allow_html=True)

# --- Detection engine: transparent heuristic baseline, not a production AI model ---
URGENCY = [
    "خلال 10 دقائق", "خلال ١٠ دقائق", "فوراً", "فورا", "عاجل", "بشكل عاجل",
    "immediately", "urgent", "within 10 minutes", "act now", "limited time"
]
CREDENTIALS = [
    "كلمة المرور", "كلمه المرور", "رمز التحقق", "رمز otp", "otp", "password",
    "بياناتك البنكية", "بيانات البطاقة", "تحديث بياناتك", "verify your account",
    "login", "account details", "card details", "pin"
]
IMPERSONATION = [
    "البنك", "مصرف", "الشرطة", "وزارة الداخلية", "الهوية الرقمية",
    "جهة حكومية", "شركة التوصيل", "your bank", "government", "police",
    "delivery company", "support team"
]
REWARD = [
    "مبروك", "ربحت", "جائزة", "اربح", "هدية", "تحويل مالي",
    "you won", "winner", "prize", "free gift", "claim your reward"
]
THREAT = [
    "سيتم إيقاف", "تم تعليق", "سيتم حظر", "إغلاق حسابك", "غرامة",
    "suspended", "blocked", "account will be closed", "penalty"
]

def extract_urls(text):
    return re.findall(r'https?://[^\s<>"\']+', text or "", flags=re.I)

def url_features(url):
    raw = (url or "").strip()
    if not raw:
        return [], 0
    candidate = raw if "://" in raw else "https://" + raw
    try:
        p = urlparse(candidate)
        host = (p.hostname or "").lower()
    except Exception:
        return ["تعذر تحليل صيغة الرابط"], 2
    flags, score = [], 0
    if not host or "." not in host:
        flags.append("اسم النطاق غير واضح أو غير مكتمل")
        score += 2
    if p.scheme.lower() != "https":
        flags.append("الرابط لا يستخدم HTTPS")
        score += 1
    if re.search(r'(\d{1,3}\.){3}\d{1,3}$', host):
        flags.append("الرابط يستخدم عنوان IP بدلاً من اسم نطاق")
        score += 3
    if "xn--" in host:
        flags.append("النطاق يحتوي على ترميز دولي قد يخفي تشابهاً بصرياً")
        score += 2
    if len(host) > 45:
        flags.append("اسم النطاق طويل بشكل غير معتاد")
        score += 1
    if host.count("-") >= 3:
        flags.append("اسم النطاق يحتوي على عدة شرطات")
        score += 1
    if any(x in host for x in ["login", "verify", "secure", "update", "banking"]):
        flags.append("النطاق يحتوي على كلمات مرتبطة بتسجيل الدخول أو التحقق")
        score += 1
    if p.username or p.password:
        flags.append("الرابط يحتوي على بيانات مستخدم ضمن العنوان")
        score += 3
    return flags, score

def analyze_message(message, extra_url=""):
    msg = (message or "").lower()
    reasons, score = [], 0
    checks = [
        (URGENCY, 2, "لغة استعجال أو ضغط زمني"),
        (CREDENTIALS, 3, "طلب أو إشارة إلى بيانات حساسة أو رموز تحقق"),
        (IMPERSONATION, 1, "انتحال أو ادعاء صفة جهة موثوقة"),
        (REWARD, 2, "وعد بجائزة أو مكافأة"),
        (THREAT, 2, "تهديد بتعليق الحساب أو فرض إجراء"),
    ]
    for terms, points, label in checks:
        if any(t in msg for t in terms):
            score += points
            reasons.append(label)
    urls = extract_urls(message)
    if extra_url.strip():
        urls.append(extra_url.strip())
    unique_urls = list(dict.fromkeys(urls))
    url_details = []
    for u in unique_urls:
        flags, pts = url_features(u)
        score += pts
        url_details.append((u, flags))
        reasons.extend(flags)
    score = min(score, 10)
    if score >= 7:
        level, color, advice = "مرتفع", "🔴", "لا تفتح الرابط ولا تشارك أي رمز أو بيانات. تواصل مع الجهة عبر قنواتها الرسمية."
    elif score >= 4:
        level, color, advice = "متوسط", "🟠", "تحقق من هوية المرسل والرابط عبر التطبيق أو الموقع الرسمي قبل أي إجراء."
    else:
        level, color, advice = "منخفض حسب المؤشرات المتاحة", "🟢", "لا توجد مؤشرات قوية في هذا الفحص، لكن هذا لا يضمن أن الرسالة آمنة."
    return {"score": score, "level": level, "color": color, "reasons": reasons or ["لم تُكتشف مؤشرات واضحة ضمن قواعد النموذج الأولي."], "urls": url_details, "advice": advice}

def fingerprint(text, url=""):
    words = set(re.findall(r'[\w\u0600-\u06FF]+', (text or "").lower()))
    words = {w for w in words if len(w) > 2}
    host = ""
    try:
        candidate = url if "://" in url else ("https://" + url if url else "")
        host = (urlparse(candidate).hostname or "").lower() if candidate else ""
    except Exception:
        pass
    return words, host

def similarity(a, b):
    wa, ha = fingerprint(a.get("message",""), a.get("url",""))
    wb, hb = fingerprint(b.get("message",""), b.get("url",""))
    union = wa | wb
    jaccard = len(wa & wb) / len(union) if union else 0
    host_match = bool(ha and hb and ha == hb)
    return max(jaccard, 0.85 if host_match else 0)

if "cases" not in st.session_state:
    st.session_state.cases = [
        {"message":"عميلنا العزيز، تم تعليق حسابك. حدث بياناتك البنكية خلال 10 دقائق عبر الرابط","url":"http://secure-bank-update.example.test"},
        {"message":"تنبيه من البنك: حسابك موقوف مؤقتاً، يرجى تحديث بياناتك البنكية فوراً","url":"http://secure-bank-update.example.test"},
        {"message":"مبروك ربحت جائزة، اضغط هنا لاستلام الهدية","url":"http://claim-prize.example.test"},
    ]

tab1, tab2, tab3 = st.tabs(["🔎 فحص رسالة أو رابط", "🧩 ربط حملات الاحتيال", "📊 لوحة المؤشرات"])

with tab1:
    st.subheader("افحص قبل أن تتصرف")
    st.write("الصق نص الرسالة أو الرابط. لا تدخل كلمات مرور أو أرقام بطاقات أو بيانات شخصية حقيقية.")
    c1, c2 = st.columns([2,1])
    with c1:
        message = st.text_area("نص الرسالة", height=170, placeholder="الصق الرسالة المشبوهة هنا...")
    with c2:
        url = st.text_input("رابط إضافي (اختياري)", placeholder="https://example.com")
        st.caption("يمكنك أيضاً وضع الرابط داخل نص الرسالة.")
        analyze_btn = st.button("تحليل باستخدام حِصن", type="primary", use_container_width=True)
    if analyze_btn:
        if not message.strip() and not url.strip():
            st.warning("أدخل رسالة أو رابطاً أولاً.")
        else:
            result = analyze_message(message, url)
            st.session_state.last_result = result
            st.session_state.cases.append({"message":message, "url":url or (extract_urls(message)[0] if extract_urls(message) else "")})
    if "last_result" in st.session_state:
        r = st.session_state.last_result
        st.markdown("---")
        st.markdown(f"### {r['color']} مستوى الخطورة: {r['level']}")
        st.progress(r["score"]/10, text=f"مؤشر الاشتباه التجريبي: {r['score']}/10")
        left, right = st.columns([1,1])
        with left:
            st.markdown("**المؤشرات التي تم رصدها**")
            for reason in r["reasons"]:
                st.write("• " + reason)
            for u, flags in r["urls"]:
                st.markdown("**الرابط:** `" + u + "`")
                if flags:
                    for f in flags: st.write("• " + f)
                else:
                    st.write("• لم تُرصد مؤشرات الرابط المحددة في النموذج.")
        with right:
            st.markdown("**توصية حِصن**")
            st.info(r["advice"])
            st.caption("هذا نموذج توعوي أولي يعتمد قواعد قابلة للتفسير، وليس خدمة تحقق أمنية معتمدة أو حكماً نهائياً على الرسالة.")

with tab2:
    st.subheader("اكتشاف الرسائل التي قد تنتمي إلى حملة واحدة")
    st.write("يقارن النموذج الرسائل التجريبية بناءً على تشابه الكلمات والنطاقات. التشابه ليس دليلاً على هوية المرسل أو ارتكاب جريمة.")
    cases = st.session_state.cases
    if len(cases) < 2:
        st.info("أضف رسائل من تبويب الفحص لبدء المقارنة.")
    else:
        threshold = st.slider("حد التشابه لعرض ارتباط محتمل", 0.1, 1.0, 0.35, 0.05)
        found = []
        for i in range(len(cases)):
            for j in range(i+1, len(cases)):
                sim = similarity(cases[i], cases[j])
                if sim >= threshold:
                    found.append((i+1,j+1,sim))
        st.metric("الروابط المحتملة بين الحالات", len(found))
        if found:
            for a,b,s in found:
                st.markdown(f"- **الحالة {a} ↔ الحالة {b}** — تشابه {s:.0%}")
        else:
            st.success("لم يتم العثور على روابط تتجاوز حد التشابه المحدد.")
        with st.expander("عرض الحالات التجريبية"):
            for i, case in enumerate(cases,1):
                st.write(f"**الحالة {i}:** {case['message'][:180]}")
                if case.get("url"): st.code(case["url"])

with tab3:
    st.subheader("مؤشرات النموذج التجريبي")
    cases = st.session_state.cases
    results = [analyze_message(c.get("message",""), c.get("url","")) for c in cases]
    high = sum(1 for x in results if x["score"] >= 7)
    med = sum(1 for x in results if 4 <= x["score"] < 7)
    low = len(results)-high-med
    a,b,c,d = st.columns(4)
    a.metric("الحالات المفحوصة", len(cases))
    b.metric("مؤشر مرتفع", high)
    c.metric("مؤشر متوسط", med)
    d.metric("مؤشر منخفض", low)
    st.markdown("#### سجل الحالات")
    for i,(case,res) in enumerate(zip(cases,results),1):
        st.write(f"{i}. {res['color']} **{res['level']}** — {case['message'][:100]}")
    st.caption("الأرقام ناتجة عن بيانات تجريبية داخل جلسة التطبيق، ولا تمثل إحصاءات وطنية أو بلاغات حقيقية.")

st.markdown("---")
st.caption("HISN AI MVP • Hackathon prototype • Use synthetic examples only • Not for real-world blocking or law-enforcement decisions")
