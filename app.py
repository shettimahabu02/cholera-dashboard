import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Cholera Response Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #eaeff2; }
    .kpi-card { background-color: white; padding: 15px; border-radius: 8px; text-align: center; border-top: 4px solid #1f3b73; height: 110px;}
    .kpi-value { font-size: 24px; font-weight: bold; color: #1f3b73; margin: 0; }
    .kpi-label { font-size: 11px; color: #666; text-transform: uppercase; margin: 0; line-height: 1.2;}
    .header-box { background-color: #1f3b73; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;}
    .header-title { font-size: 26px; font-weight: bold; margin: 0; }
    .header-sub { font-size: 13px; color: #c9d6f0; margin: 0; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: white; border-radius: 4px; padding: 10px 20px; border: 1px solid #ddd; }
    .stTabs [aria-selected="true"] { background-color: #1f3b73 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING (MOCK DATA)
# ==========================================
@st.cache_data(ttl=600) # Refreshes every 10 minutes
def load_data():
    # ---------------------------------------------------------
    # ⚠️ WHEN YOU GET THE KOBO TOKEN, REPLACE THIS BLOCK ⚠️
    # ---------------------------------------------------------
    
    # --- MOCK DATA (Matches your screenshot) ---
    data = {
        'LGA': ['Jere', 'Konduga', 'MMC', 'Magumeri'],
        'Interviews': [9, 21, 17, 16],
    }
    df_lga = pd.DataFrame(data)
    
    df_coverage = pd.DataFrame({
        'Intervention': ['WASH/cholera kit', 'Hygiene promotion', 'Sanitation support', 'Water trucking'],
        'Percentage': [100, 87, 48, 40]
    })

    df_kii = pd.DataFrame({
        'Theme': ['Coverage', 'Case reduction', 'Effectiveness', 'Info quality', 'Implementation', 
                  'Leader consult.', 'Women particip.', 'PWD inclusion', 'Learning value'],
        'Score': [4.2, 4.5, 4.4, 4.4, 3.7, 4.2, 4.2, 4.2, 4.2]
    })

    df_nps = pd.DataFrame({
        'Score': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Count': [0, 0, 1, 1, 1, 4, 4, 6, 21, 17, 6]
    })

    return df_lga, df_coverage, df_kii, df_nps

df_lga, df_coverage, df_kii, df_nps = load_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("### FILTERS")
lga_filter = st.sidebar.selectbox("LGA", ["All LGAs", "Jere", "Konduga", "MMC", "Magumeri"])
ward_filter = st.sidebar.selectbox("WARD", ["All wards", "Ward A", "Ward B"])
survey_filter = st.sidebar.selectbox("SURVEY TYPE", ["All types", "Beneficiary", "Key Informant", "FGD"])
st.sidebar.date_input("FROM", pd.to_datetime("2026-07-06"))
st.sidebar.date_input("TO", pd.to_datetime("2026-07-13"))
st.sidebar.button("Reset", use_container_width=True, type="primary")

st.sidebar.markdown("---")
st.sidebar.caption("All LGAs · All survey types · 2026-07-06 → 2026-07-13")

# ==========================================
# 4. HEADER
# ==========================================
st.markdown("""
<div class="header-box">
    <div>
        <p class="header-title">Cholera Emergency Response — Implementation Process Monitoring</p>
        <p class="header-sub">Borno State, Nigeria · Data collection 6–13 July 2026 · Beneficiary Interviews, KIIs & FGDs across Jere, Konduga, Magumeri & MMC</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tabs = ["Overview", "Water Supply & Treatment", "WASH / Cholera Kits", "Hygiene Promotion", 
        "Emergency Sanitation", "RCCE & Referral", "IPC Support", "Accountability & NPS"]
st.tabs(tabs)

# ==========================================
# 5. KPI CARDS
# ==========================================
cols = st.columns(9)
kpis = [
    ("65", "BENEFICIARY<br>INTERVIEWS"), ("19", "KEY INFORMANT<br>INTERVIEWS"), ("6", "FOCUS GROUP<br>DISCUSSIONS"),
    ("+20", "NET PROMOTER<br>SCORE"), ("4.4/5", "OVERALL<br>SATISFACTION"), ("72%", "GOOD CHOLERA<br>KNOWLEDGE"),
    ("92%", "MEET SPHERE<br>WATER MIN."), ("9.8", "AVG HOUSEHOLD<br>SIZE"), ("25%", "HHS WITH A<br>PWD MEMBER")
]
for col, (val, label) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="kpi-card"><p class="kpi-value">{val}</p><p class="kpi-label">{label}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. CHARTS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Coverage by intervention (beneficiaries reporting receipt)")
    st.caption("BL_Q1, Q6, Q18, Q27 — % answering 'yes'")
    fig1 = px.bar(df_coverage, x='Percentage', y='Intervention', orientation='h', text='Percentage', color_discrete_sequence=['#1f3b73'])
    fig1.update_traces(texttemplate='%{text}%', textposition='inside')
    fig1.update_layout(xaxis_title="", yaxis_title="", xaxis_range=[0, 110], plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### Key informant ratings by theme (avg, 1–5)")
    st.caption("KII rating questions grouped by KPI")
    fig2 = px.bar(df_kii, x='Theme', y='Score', text='Score', color_discrete_sequence=['#78c043'])
    fig2.update_traces(textposition='outside')
    fig2.update_layout(yaxis_range=[0, 5], yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Beneficiary interviews by LGA")
    st.caption("Count of beneficiary respondents")
    fig3 = px.bar(df_lga, x='LGA', y='Interviews', text='Interviews', color_discrete_sequence=['#26a69a'])
    fig3.update_traces(textposition='outside')
    fig3.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### Net Promoter Score distribution")
    st.caption("BL_Q38 — 'Would you recommend this support?' (0–10)")
    colors = ['#d9534f' if x <= 6 else '#f0ad4e' if x <= 8 else '#5cb85c' for x in df_nps['Score']]
    fig4 = go.Figure(data=[go.Bar(x=df_nps['Score'], y=df_nps['Count'], text=df_nps['Count'], textposition='outside', marker_color=colors)])
    fig4.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig4, use_container_width=True)