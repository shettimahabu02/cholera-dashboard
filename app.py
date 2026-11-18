import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & KILLER CSS
# ==========================================
st.set_page_config(page_title="Election War Room", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    .header-box { 
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; color: white; padding: 25px 30px; 
        border-radius: 12px; margin-bottom: 25px; 
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);
    }
    .header-title { font-size: 28px; font-weight: 800; margin: 0; color: #38bdf8; }
    .header-sub { font-size: 14px; color: #94a3b8; margin: 5px 0 0 0; }
    
    .kpi-card { 
        background-color: #1e293b; padding: 20px 15px; border-radius: 12px; 
        text-align: center; border: 1px solid #334155; height: 130px; 
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2); margin-bottom: 25px;
    }
    .kpi-value { font-size: 32px; font-weight: 900; color: #38bdf8; margin: 0 0 8px 0; line-height: 1; }
    .kpi-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; line-height: 1.3; font-weight: 600; margin: 0;}
    
    .chart-container {
        background: #1e293b; padding: 20px; border-radius: 12px;
        border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.2); margin-bottom: 20px;
    }
    h4 { color: #f8fafc; margin-bottom: 4px !important; font-size: 17px !important; font-weight: 700;}
    .caption-text { font-size: 12px; color: #94a3b8; margin-bottom: 15px; display: block; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING (LIVE KOBO API)
# ==========================================
@st.cache_data(ttl=60) 
def load_data():
    # ⚠️ YOUR KOBO CREDENTIALS ⚠️
    ASSET_UID = "a7xKxj3DgaNy7psHJyP7BM" 
    API_TOKEN = "350ca520c28c493b70e76afa3062c06971a4760d"
    
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{ASSET_UID}/data.json"
    headers = {"Authorization": f"Token {API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        raw_data = response.json()['results']
    except Exception as e:
        st.error(f"Error connecting to Kobo. Please check your API Token and Asset UID. Details: {e}")
        # Return empty dataframes so the app doesn't crash
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if not raw_data:
        st.warning("Connected to Kobo successfully, but there are 0 submissions. Please submit a test survey from the Kobo app!")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(raw_data)

    # ---------------------------------------------------------
    # ⚠️ COLUMN MAPPING ⚠️
    # You MUST ensure these names match your Kobo form exactly!
    # (Change 'APC_President' to whatever you named it in Kobo)
    # ---------------------------------------------------------
    
    # 1. Presidential Tally (Safely handle missing columns with .get)
    df_pres = pd.DataFrame({
        'Party': ['APC', 'PDP', 'LP'],
        'Votes': [
            pd.to_numeric(df.get('APC_President', pd.Series([0])), errors='coerce').fillna(0).sum(),
            pd.to_numeric(df.get('PDP_President', pd.Series([0])), errors='coerce').fillna(0).sum(),
            pd.to_numeric(df.get('LP_President', pd.Series([0])), errors='coerce').fillna(0).sum()
        ]
    })

    # 2. Reporting Status (Total PUs vs PUs that reported)
    # Assuming your form has a 'Polling_Unit_Name' column
    total_reported = len(df['Polling_Unit_Name'].dropna().unique()) if 'Polling_Unit_Name' in df.columns else 0
    total_expected = 120 # You can hardcode your total target PUs here
    pending = total_expected - total_reported if total_reported < total_expected else 0
    
    df_status = pd.DataFrame({
        'Status': ['Reported', 'Pending'],
        'Count': [total_reported, pending]
    })

    # 3. Security Incidents
    if 'Security_Issues' in df.columns:
        sec_counts = df['Security_Issues'].value_counts().reset_index()
        sec_counts.columns = ['Incident', 'Count']
    else:
        sec_counts = pd.DataFrame({'Incident': ['No Data'], 'Count': [0]})

    # 4. Staff Performance
    if 'Data_Entry_Staff' in df.columns:
        staff_counts = df['Data_Entry_Staff'].value_counts().reset_index()
        staff_counts.columns = ['Staff', 'Calls_Entered']
    else:
        staff_counts = pd.DataFrame({'Staff': ['No Data'], 'Calls_Entered': [0]})

    return df_pres, df_status, sec_counts, staff_counts

df_pres, df_status, df_security, df_staff = load_data()

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("### 🛡️ WAR ROOM CONTROLS")
st.sidebar.selectbox("State", ["All States", "Lagos", "Kano", "Rivers", "FCT"])
st.sidebar.selectbox("Election Level", ["Presidential", "Governorship", "House of Reps"])
st.sidebar.button("Force Refresh", use_container_width=True, type="primary")
st.sidebar.markdown("---")
st.sidebar.caption("Live Call Center Sync Active")

# ==========================================
# 4. HEADER
# ==========================================
st.markdown("""
<div class="header-box">
    <div>
        <p class="header-title">Election Command Center</p>
        <p class="header-sub">Live Polling Unit Tally & Incident Tracker</p>
    </div>
    <div style="background-color: #ef4444; color: white; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 900; animation: pulse 2s infinite;">
        🔴 LIVE KOBO SYNC
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. KPI CARDS
# ==========================================
# Dynamic calculations
total_votes = df_pres['Votes'].sum() if not df_pres.empty else 0
total_incidents = df_security[df_security['Incident'].isin(['Minor Issue', 'Major Incident'])]['Count'].sum() if not df_security.empty else 0
total_pus = df_status[df_status['Status'] == 'Reported']['Count'].sum() if not df_status.empty else 0

cols = st.columns(4)
kpis = [
    (f"{total_pus} / 120", "Polling Units<br>Reported"), 
    (f"{total_votes:,}", "Total Votes<br>Entered"), 
    (f"{total_incidents}", "Security<br>Incidents"),
    ("100%", "Call Center<br>Uptime")
]
for col, (val, label) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="kpi-card"><p class="kpi-value">{val}</p><p class="kpi-label">{label}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. CHARTS
# ==========================================
col1, col2 = st.columns([2, 1]) 

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Live Presidential Vote Tally</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Aggregated votes from reported Polling Units</span>", unsafe_allow_html=True)
    
    if total_votes > 0:
        colors = {'APC': '#3b82f6', 'PDP': '#ef4444', 'LP': '#eab308'}
        fig1 = px.bar(df_pres, x='Party', y='Votes', text='Votes', color='Party', color_discrete_map=colors)
        fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Waiting for vote count data from Kobo...")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Reporting Status</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Polling Units that have called in</span>", unsafe_allow_html=True)
    
    if not df_status.empty:
        fig2 = px.pie(df_status, values='Count', names='Status', hole=0.6, color='Status', color_discrete_map={'Reported': '#10b981', 'Pending': '#334155'})
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Security & Incident Report</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Real-time field safety updates</span>", unsafe_allow_html=True)
    
    if not df_security.empty:
        fig3 = px.bar(df_security, x='Count', y='Incident', orientation='h', text='Count', color='Incident', color_discrete_map={'No Issues': '#10b981', 'Minor Issue': '#f59e0b', 'Major Incident': '#ef4444'})
        fig3.update_traces(textposition='inside')
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("<h4>Call Center Staff Performance</h4>", unsafe_allow_html=True)
    st.markdown("<span class='caption-text'>Calls entered into Kobo by staff</span>", unsafe_allow_html=True)
    
    if not df_staff.empty:
        fig4 = px.bar(df_staff, x='Staff', y='Calls_Entered', text='Calls_Entered', color_discrete_sequence=['#38bdf8'])
        fig4.update_traces(textposition='outside')
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'))
        st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
