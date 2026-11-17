import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ==========================================
# 1. PAGE CONFIGURATION & THEME FORCE
# ==========================================
st.set_page_config(page_title="Cholera Response Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to force professional Light Mode and fix all layout issues
st.markdown("""
    <style>
    /* Force professional light background */
    .stApp { 
        background-color: #f4f7f9 !important; 
    }
    
    /* Force sidebar light theme */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e6ed;
    }
    
    /* KPI Cards - fixed height and perfect centering */
    .kpi-card { 
        background-color: #ffffff; 
        padding: 15px 10px; 
        border-radius: 8px; 
        text-align: center; 
        border-top: 4px solid #1f3b73; 
        height: 120px; /* Fixed height to prevent overlap */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 25px;
    }
    .kpi-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #1f3b73; 
        margin: 0 0 5px 0; 
        line-height: 1;
    }
    .kpi-label { 
        font-size: 11px; 
        color: #5a7184; 
        text-transform: uppercase; 
        line-height: 1.2; 
        font-weight: 700;
        margin: 0;
    }
    
    /* Header Styling */
    .header-box { 
        background-color: #1f3b73; 
        color: white; 
        padding: 24px 30px; 
        border-radius: 8px; 
        margin-bottom: 30px; 
        box-shadow: 0 4px 12px rgba(31, 59, 115, 0.2);
    }
    .header-title { font-size: 26px; font-weight: bold; margin: 0; }
    .header-sub { font-size: 14px; color: #c9d6f0; margin: 6px 0 0 0; }
    
    /* Tabs Layout */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 6px; 
        padding: 10px 20px; 
        border: 1px solid #d0d7de; 
        color: #333;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1f3b73 !important; 
        color: #ffffff !important; 
        border: 1px solid #1f3b73;
    }
    
    /* Chart Titles */
    h4 { color: #1f3b73; margin-bottom: 2px !important; font-size: 16px !important; }
    .caption-text { font-size: 12px; color: #666; margin-bottom: 15px; display: block; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING (MOCK DATA)
# ==========================================
@st.cache_data(ttl=600) 
def load_data():
    # ---------------------------------------------------------
    # ⚠️ WE WILL REPLACE THIS BLOCK WITH KOBO API LATER ⚠️
    # ---------------------------------------------------------
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
st.sidebar.selectbox("LGA", ["All LGAs", "Jere", "Konduga", "MMC", "Magumeri"])
st.sidebar.selectbox("WARD", ["All wards", "Ward A", "Ward B"])
st.sidebar.selectbox("SURVEY TYPE", ["All types", "Beneficiary", "Key Informant", "FGD"])
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
    <p class="header-title">Cholera Emergency Response — Implementation Process Monitoring</p>
    <p class="header-sub">Borno State, Nigeria · Data collection 6–13 July 2026 · Beneficiary Interviews, KIIs & FGDs across Jere, Konduga, Magumeri & MMC</p>
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
    ("65", "Beneficiary<br>Interviews"), 
    ("19", "Key Informant<br>Interviews"), 
    ("6", "Focus Group<br>Discussions"),
    ("+20", "Net Promoter<br>Score"), 
    ("4.4/5", "Overall<br>Satisfaction"), 
    ("72%", "Good Cholera<br>Knowledge"),
    ("92%", "Meet Sphere<br>Water Min."), 
    ("9.8", "Avg Household<br>Size"), 
    ("25%", "HHs with a<br>PWD Member")
]
for col, (val, label) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="kpi-card"><p class="kpi-value">{val}</p><p class="kpi-label">{label}</p></div>', unsafe_allow_html=True)

# ==========================================
# 6. CHARTS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h4>Coverage by intervention (beneficiaries reporting receipt)</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>BL_Q1, Q6, Q18, Q27 — % answering 'yes'</span>", unsafe_allow_html=True)
    fig1 = px.bar(df_coverage, x='Percentage', y='Intervention', orientation='h', text='Percentage', color_discrete_sequence=['#1f3b73'])
    fig1.update_traces(texttemplate='%{text}%', textposition='inside')
    fig1.update_layout(xaxis_title="", yaxis_title="", xaxis_range=[0, 110], plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("<h4>Key informant ratings by theme (avg, 1–5)</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>KII rating questions grouped by KPI</span>", unsafe_allow_html=True)
    fig2 = px.bar(df_kii, x='Theme', y='Score', text='Score', color_discrete_sequence=['#78c043'])
    fig2.update_traces(textposition='outside')
    fig2.update_layout(yaxis_range=[0, 5], yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("<h4>Beneficiary interviews by LGA</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Count of beneficiary respondents</span>", unsafe_allow_html=True)
    fig3 = px.bar(df_lga, x='LGA', y='Interviews', text='Interviews', color_discrete_sequence=['#26a69a'])
    fig3.update_traces(textposition='outside')
    fig3.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("<h4>Net Promoter Score distribution</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>BL_Q38 — 'Would you recommend this support?' (0–10)</span>", unsafe_allow_html=True)
    colors = ['#d9534f' if x <= 6 else '#f0ad4e' if x <= 8 else '#5cb85c' for x in df_nps['Score']]
    fig4 = go.Figure(data=[go.Bar(x=df_nps['Score'], y=df_nps['Count'], text=df_nps['Count'], textposition='outside', marker_color=colors)])
    fig4.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='white', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig4, use_container_width=True)
