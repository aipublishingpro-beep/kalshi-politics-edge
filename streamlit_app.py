import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ============================================================================
# KALSHI POLITICS STRUCTURAL EDGE v1.0
# ============================================================================

st.set_page_config(
    page_title="Kalshi Politics Edge",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for serious, data-first UI
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
    .constraint-open { color: #f59e0b; font-weight: 600; }
    .constraint-passed { color: #10b981; font-weight: 600; }
    .constraint-blocked { color: #ef4444; font-weight: 600; }
    .lag-detected { 
        background: #fef3c7; 
        border-left: 4px solid #f59e0b;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    .path-collapse {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    .structural-resolved {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    .disclaimer {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #64748b;
    }
    .event-item {
        border-left: 3px solid #6366f1;
        padding-left: 0.75rem;
        margin: 0.5rem 0;
    }
    .tier-locked {
        opacity: 0.5;
        pointer-events: none;
    }
    .tier-badge {
        background: #6366f1;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'user_tier' not in st.session_state:
    st.session_state.user_tier = 'pro'  # Default to pro for demo
if 'selected_market' not in st.session_state:
    st.session_state.selected_market = None
if 'alerts_enabled' not in st.session_state:
    st.session_state.alerts_enabled = {}

# ============================================================================
# MOCK DATA - Replace with real API calls in v1.1
# ============================================================================

def get_mock_markets():
    """Mock political markets data - will be replaced with Kalshi API"""
    markets = [
        {
            'ticker': 'PRES-2024-DEM',
            'title': 'Democratic Nominee 2024',
            'category': 'Elections',
            'subcategory': 'Presidential',
            'yes_price': 0.92,
            'volume': 245000,
            'expiration': '2024-08-22',
            'status': 'active',
            'lag_status': 'none',
            'structural_certainty': 'high',
            'paths_yes': 1,
            'paths_no': 0,
            'constraint_summary': 'Nomination structurally resolved'
        },
        {
            'ticker': 'PRES-2024-GOP',
            'title': 'Republican Nominee 2024',
            'category': 'Elections',
            'subcategory': 'Presidential',
            'yes_price': 0.94,
            'volume': 312000,
            'expiration': '2024-07-18',
            'status': 'active',
            'lag_status': 'none',
            'structural_certainty': 'high',
            'paths_yes': 1,
            'paths_no': 0,
            'constraint_summary': 'Primary process complete'
        },
        {
            'ticker': 'SENATE-2024-CONTROL',
            'title': 'Senate Control 2024',
            'category': 'Elections',
            'subcategory': 'Congressional',
            'yes_price': 0.51,
            'volume': 189000,
            'expiration': '2024-11-06',
            'status': 'active',
            'lag_status': 'detected',
            'structural_certainty': 'low',
            'paths_yes': 8,
            'paths_no': 7,
            'constraint_summary': 'Multiple paths open, thin liquidity'
        },
        {
            'ticker': 'GOV-2024-NC',
            'title': 'NC Governor 2024',
            'category': 'Elections',
            'subcategory': 'Gubernatorial',
            'yes_price': 0.67,
            'volume': 45000,
            'expiration': '2024-11-06',
            'status': 'active',
            'lag_status': 'detected',
            'structural_certainty': 'medium',
            'paths_yes': 2,
            'paths_no': 2,
            'constraint_summary': 'Filing complete, legal challenge pending'
        },
        {
            'ticker': 'SCOTUS-2024-TERM',
            'title': 'SCOTUS Retirement 2024 Term',
            'category': 'Legal',
            'subcategory': 'Supreme Court',
            'yes_price': 0.15,
            'volume': 28000,
            'expiration': '2024-10-01',
            'status': 'active',
            'lag_status': 'none',
            'structural_certainty': 'medium',
            'paths_yes': 3,
            'paths_no': 1,
            'constraint_summary': 'Term window closing, no signals'
        },
        {
            'ticker': 'IMPEACH-2024',
            'title': 'Impeachment Vote 2024',
            'category': 'Congress',
            'subcategory': 'Procedures',
            'yes_price': 0.08,
            'volume': 67000,
            'expiration': '2024-12-31',
            'status': 'active',
            'lag_status': 'none',
            'structural_certainty': 'high',
            'paths_yes': 1,
            'paths_no': 4,
            'constraint_summary': 'Procedural path exists but blocked'
        },
        {
            'ticker': 'SHUTDOWN-2024-Q1',
            'title': 'Government Shutdown Q1 2024',
            'category': 'Congress',
            'subcategory': 'Fiscal',
            'yes_price': 0.35,
            'volume': 92000,
            'expiration': '2024-03-31',
            'status': 'resolved',
            'lag_status': 'none',
            'structural_certainty': 'resolved',
            'paths_yes': 0,
            'paths_no': 0,
            'constraint_summary': 'CR passed, outcome resolved'
        },
        {
            'ticker': 'TX-BORDER-2024',
            'title': 'TX Border Federal Intervention',
            'category': 'Legal',
            'subcategory': 'Federal',
            'yes_price': 0.42,
            'volume': 156000,
            'expiration': '2024-06-30',
            'status': 'active',
            'lag_status': 'detected',
            'structural_certainty': 'low',
            'paths_yes': 4,
            'paths_no': 3,
            'constraint_summary': 'SCOTUS ruling pending, multiple paths'
        },
    ]
    return pd.DataFrame(markets)

def get_mock_constraints(ticker):
    """Mock constraint data for a specific market"""
    constraints = {
        'PRES-2024-DEM': [
            {'name': 'Primary Elections', 'status': 'passed', 'date': '2024-06-04', 'notes': 'All state primaries complete'},
            {'name': 'Delegate Threshold', 'status': 'passed', 'date': '2024-03-12', 'notes': 'Majority secured'},
            {'name': 'Convention Vote', 'status': 'passed', 'date': '2024-08-22', 'notes': 'Formal nomination complete'},
            {'name': 'Legal Challenges', 'status': 'resolved', 'date': '2024-04-15', 'notes': 'No active challenges'},
        ],
        'SENATE-2024-CONTROL': [
            {'name': 'Filing Deadlines', 'status': 'passed', 'date': '2024-06-15', 'notes': 'All states closed'},
            {'name': 'Primary Certifications', 'status': 'open', 'date': '2024-09-15', 'notes': '42/50 complete'},
            {'name': 'Early Voting Start', 'status': 'open', 'date': '2024-10-15', 'notes': 'Pending'},
            {'name': 'Legal Challenges', 'status': 'open', 'date': None, 'notes': '3 active in swing states'},
        ],
        'GOV-2024-NC': [
            {'name': 'Filing Deadline', 'status': 'passed', 'date': '2024-03-01', 'notes': 'Candidates locked'},
            {'name': 'Primary Election', 'status': 'passed', 'date': '2024-05-14', 'notes': 'Nominees selected'},
            {'name': 'Ballot Challenge', 'status': 'open', 'date': '2024-08-30', 'notes': 'Robinson challenge pending'},
            {'name': 'Certification', 'status': 'open', 'date': '2024-11-26', 'notes': 'Post-election'},
        ],
        'TX-BORDER-2024': [
            {'name': 'SCOTUS Emergency Stay', 'status': 'passed', 'date': '2024-01-22', 'notes': 'Federal access granted'},
            {'name': 'Full SCOTUS Review', 'status': 'open', 'date': '2024-04-15', 'notes': 'Oral arguments pending'},
            {'name': 'Congressional Action', 'status': 'open', 'date': None, 'notes': 'Bills in committee'},
            {'name': 'Executive Order Window', 'status': 'open', 'date': None, 'notes': 'Presidential discretion'},
        ],
    }
    return constraints.get(ticker, [
        {'name': 'Data Pending', 'status': 'open', 'date': None, 'notes': 'Structural analysis in progress'}
    ])

def get_mock_paths(ticker):
    """Mock path data for a specific market"""
    paths = {
        'SENATE-2024-CONTROL': {
            'yes_paths': [
                {'description': 'Hold WV + flip TX + hold MT', 'status': 'viable', 'probability_band': 'low'},
                {'description': 'Hold WV + hold MT + flip FL', 'status': 'viable', 'probability_band': 'low'},
                {'description': 'Hold WV + hold MT + hold OH', 'status': 'viable', 'probability_band': 'medium'},
            ],
            'no_paths': [
                {'description': 'Lose WV + lose MT', 'status': 'viable', 'probability_band': 'medium'},
                {'description': 'Lose WV + lose OH + lose PA', 'status': 'viable', 'probability_band': 'low'},
            ],
            'recently_collapsed': [
                {'description': 'Flip TX via O\'Rourke', 'collapsed_date': '2024-02-15', 'reason': 'Candidate withdrew'},
            ]
        },
        'GOV-2024-NC': {
            'yes_paths': [
                {'description': 'Standard election, no disqualification', 'status': 'viable', 'probability_band': 'high'},
                {'description': 'Post-challenge reinstatement', 'status': 'viable', 'probability_band': 'low'},
            ],
            'no_paths': [
                {'description': 'Ballot disqualification upheld', 'status': 'viable', 'probability_band': 'medium'},
                {'description': 'Candidate withdrawal', 'status': 'viable', 'probability_band': 'low'},
            ],
            'recently_collapsed': []
        },
    }
    return paths.get(ticker, {'yes_paths': [], 'no_paths': [], 'recently_collapsed': []})

def get_mock_events(ticker):
    """Mock event timeline for a specific market"""
    events = {
        'SENATE-2024-CONTROL': [
            {'date': '2024-08-15', 'event': 'MT primary certification complete', 'impact': 'neutral'},
            {'date': '2024-08-10', 'event': 'OH polling shift detected', 'impact': 'negative'},
            {'date': '2024-08-05', 'event': 'WV incumbent retirement confirmed', 'impact': 'negative'},
            {'date': '2024-07-28', 'event': 'TX filing deadline passed', 'impact': 'neutral'},
            {'date': '2024-07-15', 'event': 'FL legal challenge dismissed', 'impact': 'positive'},
        ],
        'GOV-2024-NC': [
            {'date': '2024-08-20', 'event': 'Ballot challenge hearing scheduled', 'impact': 'negative'},
            {'date': '2024-08-12', 'event': 'CNN report on candidate statements', 'impact': 'negative'},
            {'date': '2024-07-30', 'event': 'Primary runoff avoided', 'impact': 'positive'},
            {'date': '2024-06-15', 'event': 'Major endorsement received', 'impact': 'positive'},
        ],
        'TX-BORDER-2024': [
            {'date': '2024-08-18', 'event': 'DOJ brief filed', 'impact': 'positive'},
            {'date': '2024-08-05', 'event': 'TX Governor press conference', 'impact': 'negative'},
            {'date': '2024-07-22', 'event': 'SCOTUS grants cert', 'impact': 'neutral'},
            {'date': '2024-07-10', 'event': '5th Circuit ruling', 'impact': 'negative'},
        ],
    }
    return events.get(ticker, [])

def get_mock_price_history(ticker):
    """Generate mock price history for charts"""
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    base_price = random.uniform(0.3, 0.7)
    prices = []
    current = base_price
    for _ in range(90):
        change = random.gauss(0, 0.02)
        current = max(0.01, min(0.99, current + change))
        prices.append(current)
    return pd.DataFrame({'date': dates, 'price': prices})

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🏛️ Politics Edge")
    st.markdown("*Structural Analysis Platform*")
    st.markdown("---")
    
    # User tier display
    tier_display = {
        'free': '🆓 Free',
        'pro': '⭐ Pro',
        'pro_plus': '💎 Pro+'
    }
    st.markdown(f"**Account:** {tier_display[st.session_state.user_tier]}")
    
    # Tier selector for demo
    st.session_state.user_tier = st.selectbox(
        "Demo Tier",
        ['free', 'pro', 'pro_plus'],
        index=['free', 'pro', 'pro_plus'].index(st.session_state.user_tier),
        help="Switch tiers to see feature gating"
    )
    
    st.markdown("---")
    
    # Filters
    st.markdown("### Filters")
    
    markets_df = get_mock_markets()
    
    category_filter = st.multiselect(
        "Category",
        options=markets_df['category'].unique(),
        default=markets_df['category'].unique()
    )
    
    status_filter = st.multiselect(
        "Status",
        options=['active', 'resolved'],
        default=['active']
    )
    
    st.markdown("---")
    
    # Structural filters
    st.markdown("### Structural Signals")
    
    show_lag = st.checkbox("🔶 Lag Detected", value=True)
    show_path_collapse = st.checkbox("🔴 Recent Path Collapse", value=True)
    show_high_certainty = st.checkbox("🟢 High Certainty", value=True)
    
    st.markdown("---")
    
    # Quick links
    st.markdown("### Quick Access")
    if st.button("📊 Elections", use_container_width=True):
        category_filter = ['Elections']
    if st.button("⚖️ Legal", use_container_width=True):
        category_filter = ['Legal']
    if st.button("🏛️ Congress", use_container_width=True):
        category_filter = ['Congress']
    
    st.markdown("---")
    
    # Alert config
    st.markdown("### Alert Settings")
    if st.session_state.user_tier in ['pro', 'pro_plus']:
        alert_constraint = st.checkbox("Constraint Changes", value=True)
        alert_path = st.checkbox("Path Collapses", value=True)
        alert_lag = st.checkbox("Lag Detection", value=True)
        alert_deadline = st.checkbox("Deadline Crossings", value=True)
    else:
        st.markdown("*Upgrade to Pro for alerts*")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="main-header">Kalshi Politics Structural Edge</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Constraint awareness • Path counting • Market lag detection</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh"):
        st.rerun()

st.markdown("---")

# Filter markets
filtered_df = markets_df[
    (markets_df['category'].isin(category_filter)) &
    (markets_df['status'].isin(status_filter))
]

# Apply structural filters
if not show_lag:
    filtered_df = filtered_df[filtered_df['lag_status'] != 'detected']
if not show_high_certainty:
    filtered_df = filtered_df[filtered_df['structural_certainty'] != 'high']

# ============================================================================
# MARKET DASHBOARD
# ============================================================================

st.markdown("### Market Dashboard")

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active Markets", len(filtered_df[filtered_df['status'] == 'active']))
with col2:
    lag_count = len(filtered_df[filtered_df['lag_status'] == 'detected'])
    st.metric("Lag Detected", lag_count, delta="Review" if lag_count > 0 else None)
with col3:
    high_cert = len(filtered_df[filtered_df['structural_certainty'] == 'high'])
    st.metric("High Certainty", high_cert)
with col4:
    total_vol = filtered_df['volume'].sum()
    st.metric("Total Volume", f"${total_vol:,.0f}")

st.markdown("")

# Market table
for idx, row in filtered_df.iterrows():
    with st.container():
        cols = st.columns([3, 1, 1, 1, 1, 1])
        
        with cols[0]:
            # Market title with structural indicator
            indicator = ""
            if row['lag_status'] == 'detected':
                indicator = "🔶"
            elif row['structural_certainty'] == 'high':
                indicator = "🟢"
            elif row['structural_certainty'] == 'low':
                indicator = "⚪"
            
            if st.button(f"{indicator} {row['title']}", key=f"btn_{row['ticker']}", use_container_width=True):
                st.session_state.selected_market = row['ticker']
        
        with cols[1]:
            st.markdown(f"**${row['yes_price']:.2f}**")
            st.caption("YES Price")
        
        with cols[2]:
            st.markdown(f"**{row['paths_yes']}** / **{row['paths_no']}**")
            st.caption("Paths Y/N")
        
        with cols[3]:
            cert_color = {
                'high': '🟢',
                'medium': '🟡', 
                'low': '🔴',
                'resolved': '✅'
            }
            st.markdown(f"{cert_color.get(row['structural_certainty'], '⚪')} {row['structural_certainty'].title()}")
            st.caption("Certainty")
        
        with cols[4]:
            st.markdown(f"${row['volume']:,}")
            st.caption("Volume")
        
        with cols[5]:
            st.markdown(f"`{row['subcategory']}`")
            st.caption("Type")
        
        # Constraint summary line
        st.caption(f"📋 {row['constraint_summary']}")
        st.markdown("---")

# ============================================================================
# STRUCTURAL DETAIL PANEL
# ============================================================================

if st.session_state.selected_market:
    ticker = st.session_state.selected_market
    market_row = markets_df[markets_df['ticker'] == ticker].iloc[0]
    
    st.markdown(f"## 📊 {market_row['title']}")
    st.markdown(f"`{ticker}` • Expires: {market_row['expiration']}")
    
    # Structural status alert box
    if market_row['lag_status'] == 'detected':
        st.markdown(f"""
        <div class="lag-detected">
            <strong>⚠️ Market Lag Detected</strong><br>
            Structure suggests different certainty than current price implies. 
            Review constraint status and path count below.
        </div>
        """, unsafe_allow_html=True)
    elif market_row['structural_certainty'] == 'high':
        st.markdown(f"""
        <div class="structural-resolved">
            <strong>✅ Structurally Resolved</strong><br>
            Procedural and legal constraints indicate high outcome certainty.
            Limited remaining paths for alternative outcomes.
        </div>
        """, unsafe_allow_html=True)
    
    # Three column layout for details
    col1, col2, col3 = st.columns(3)
    
    # CONSTRAINT STATUS
    with col1:
        st.markdown("### Constraint Status")
        
        if st.session_state.user_tier == 'free':
            st.markdown("*🔒 Upgrade to Pro for real-time constraints*")
            st.markdown("---")
            st.markdown("**Sample (delayed):**")
        
        constraints = get_mock_constraints(ticker)
        for c in constraints:
            status_icon = {
                'passed': '✅',
                'open': '🔶',
                'blocked': '🔴',
                'resolved': '✅'
            }
            st.markdown(f"""
            **{c['name']}**  
            {status_icon.get(c['status'], '⚪')} {c['status'].upper()}  
            {f"📅 {c['date']}" if c['date'] else ""}  
            _{c['notes']}_
            """)
            st.markdown("")
    
    # PATH COUNT
    with col2:
        st.markdown("### Path Analysis")
        
        if st.session_state.user_tier == 'free':
            st.markdown("*🔒 Upgrade to Pro for path visibility*")
        else:
            paths = get_mock_paths(ticker)
            
            st.markdown(f"**YES Paths Remaining:** {len(paths['yes_paths'])}")
            for p in paths['yes_paths']:
                band_color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
                st.markdown(f"- {band_color.get(p['probability_band'], '⚪')} {p['description']}")
            
            st.markdown("")
            st.markdown(f"**NO Paths Remaining:** {len(paths['no_paths'])}")
            for p in paths['no_paths']:
                band_color = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}
                st.markdown(f"- {band_color.get(p['probability_band'], '⚪')} {p['description']}")
            
            if paths['recently_collapsed']:
                st.markdown("")
                st.markdown("**Recently Collapsed:**")
                for p in paths['recently_collapsed']:
                    st.markdown(f"""
                    <div class="path-collapse">
                        ❌ {p['description']}<br>
                        <small>Collapsed: {p['collapsed_date']} — {p['reason']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # EVENT TIMELINE
    with col3:
        st.markdown("### Event Timeline")
        
        if st.session_state.user_tier in ['pro', 'pro_plus']:
            events = get_mock_events(ticker)
            for e in events:
                impact_icon = {
                    'positive': '📈',
                    'negative': '📉',
                    'neutral': '➡️'
                }
                st.markdown(f"""
                <div class="event-item">
                    <strong>{e['date']}</strong><br>
                    {impact_icon.get(e['impact'], '➡️')} {e['event']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*🔒 Upgrade to Pro for event mapping*")
    
    # PRICE CHART
    st.markdown("### Price History with Events")
    
    price_df = get_mock_price_history(ticker)
    
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(
        x=price_df['date'],
        y=price_df['price'],
        mode='lines',
        name='YES Price',
        line=dict(color='#6366f1', width=2)
    ))
    
    # Add event markers if pro
    if st.session_state.user_tier in ['pro', 'pro_plus']:
        events = get_mock_events(ticker)
        for e in events:
            event_date = pd.to_datetime(e['date'])
            if event_date >= price_df['date'].min():
                closest_idx = (price_df['date'] - event_date).abs().argmin()
                price_at_event = price_df.iloc[closest_idx]['price']
                
                color = {'positive': 'green', 'negative': 'red', 'neutral': 'gray'}
                fig.add_trace(go.Scatter(
                    x=[event_date],
                    y=[price_at_event],
                    mode='markers',
                    marker=dict(size=12, color=color.get(e['impact'], 'gray'), symbol='diamond'),
                    name=e['event'][:30],
                    hovertext=e['event']
                ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="",
        yaxis_title="Price ($)",
        yaxis=dict(range=[0, 1]),
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_market = None
        st.rerun()

# ============================================================================
# STRUCTURAL SIGNALS SUMMARY (Pro+ only)
# ============================================================================

if st.session_state.user_tier == 'pro_plus' and not st.session_state.selected_market:
    st.markdown("---")
    st.markdown("### 🎯 Priority Structural Signals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Markets with Lag Detected")
        lag_markets = filtered_df[filtered_df['lag_status'] == 'detected']
        if len(lag_markets) > 0:
            for _, row in lag_markets.iterrows():
                st.markdown(f"""
                <div class="lag-detected">
                    <strong>{row['title']}</strong><br>
                    Price: ${row['yes_price']:.2f} • {row['constraint_summary']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*No lag detected in current filter*")
    
    with col2:
        st.markdown("#### High Structural Certainty")
        high_cert = filtered_df[filtered_df['structural_certainty'] == 'high']
        if len(high_cert) > 0:
            for _, row in high_cert.iterrows():
                st.markdown(f"""
                <div class="structural-resolved">
                    <strong>{row['title']}</strong><br>
                    Price: ${row['yes_price']:.2f} • Paths: {row['paths_yes']}Y / {row['paths_no']}N
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*No high certainty markets in current filter*")

# ============================================================================
# DISCLAIMER FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div class="disclaimer">
    <strong>Disclaimer:</strong> This platform provides informational analysis of publicly available data 
    related to Kalshi event contracts. Nothing on this platform constitutes financial, legal, or investment advice. 
    Kalshi contracts are regulated by the CFTC and involve risk of loss. Users are solely responsible for their 
    own trading decisions. Past structural signals do not guarantee future results.
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.caption("Kalshi Politics Edge v1.0 • Structural Analysis Platform • © 2024")
