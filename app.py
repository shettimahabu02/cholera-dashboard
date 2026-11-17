import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Cholera Response Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* 1. MAIN BACKGROUND */
    .stApp { 
        background-color: #e2e8f0 !important; 
    }
    
    /* 2. SIDEBAR DARK NAVY STYLE */
    [data-testid="stSidebar"] {
        background-color: #1e2a4a !important;
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important; /* Force all sidebar text white */
    }
    /* Style the dropdowns and date pickers to be white with dark text */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    /* Reset button styling */
    [data-testid="stSidebar"] .stButton>button {
        background-color: #65a30d !important; /* Bright green */
        color: white !important;
        border: none;
        font-weight: bold;
    }
    
    /* 3. HEADER NAVY BAR */
    .header-box { 
        background-color: #1e2a4a; 
        color: white; 
        padding: 20px 30px; 
        border-radius: 8px; 
        margin-bottom: 25px; 
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title { font-size: 26px; font-weight: bold; margin: 0; }
    .header-sub { font-size: 13px; color: #cbd5e1; margin: 5px 0 0 0; }
    
    /* 4. KPI CARDS (Floating White Boxes) */
    .kpi-card { 
        background-color: #ffffff; 
        padding: 20px 10px; 
        border-radius: 8px; 
        text-align: center; 
        height: 130px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .kpi-value { font-size: 28px; font-weight: 800; color: #1e2a4a; margin: 0 0 8px 0; line-height: 1; }
    .kpi-label { font-size: 11px; color: #64748b; text-transform: uppercase; line-height: 1.3; font-weight: 700; margin: 0;}
    
    /* 5. TABS NAVIGATION */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: #ffffff; 
        border-radius: 6px; 
        padding: 12px 24px; 
        color: #1e2a4a;
        font-weight: 600;
        border: 1px solid #cbd5e1;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #1e2a4a !important; 
        color: #ffffff !important; 
        border: 1px solid #1e2a4a;
    }
    
    /* 6. CHART CONTAINERS (Floating White Boxes) */
    .chart-container {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    h4 { color: #1e2a4a; margin-bottom: 4px !important; font-size: 17px !important; font-weight: 700;}
    .caption-text { font-size: 12px; color: #64748b; margin-bottom: 15px; display: block; }
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
st.sidebar.button("Reset", use_container_width=True)

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
    <div style="background-color: #65a30d; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: bold; white-space: nowrap;">
        65 HH interviews · 19 KIIs · 6 FGDs
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
# 6. CHARTS (Wrapped in white containers)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Coverage by intervention (beneficiaries reporting receipt)</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>BL_Q1, Q6, Q18, Q27 — % answering 'yes'</span>", unsafe_allow_html=True)
    
    fig1 = px.bar(df_coverage, x='Percentage', y='Intervention', orientation='h', text='Percentage', color_discrete_sequence=['#1e2a4a'])
    fig1.update_traces(texttemplate='%{text}%', textposition='inside', textfont_color='white')
    fig1.update_layout(xaxis_title="", yaxis_title="", xaxis_range=[0, 110], plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Key informant ratings by theme (avg, 1–5)</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>KII rating questions grouped by KPI</span>", unsafe_allow_html=True)
    
    fig2 = px.bar(df_kii, x='Theme', y='Score', text='Score', color_discrete_sequence=['#65a30d'])
    fig2.update_traces(textposition='outside')
    fig2.update_layout(yaxis_range=[0, 5], yaxis_title="", xaxis_title="", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Beneficiary interviews by LGA</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Count of beneficiary respondents</span>", unsafe_allow_html=True)
    
    fig3 = px.bar(df_lga, x='LGA', y='Interviews', text='Interviews', color_discrete_sequence=['#0d9488'])
    fig3.update_traces(textposition='outside')
    fig3.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Net Promoter Score distribution</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>BL_Q38 — 'Would you recommend this support?' (0–10)</span>", unsafe_allow_html=True)
    
    colors = ['#ef4444' if x <= 6 else '#f59e0b' if x <= 8 else '#65a30d' for x in df_nps['Score']]
    fig4 = go.Figure(data=[go.Bar(x=df_nps['Score'], y=df_nps['Count'], text=df_nps['Count'], textposition='outside', marker_color=colors)])
    fig4.update_layout(yaxis_title="", xaxis_title="", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
