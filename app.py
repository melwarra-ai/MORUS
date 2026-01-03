import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os

# ===== CONFIGURATION =====
st.set_page_config(
    page_title="AlphaStream Wealth Master",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PREMIUM STYLING =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    }
    
    .premium-card {
        background: white;
        padding: 28px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .desc-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4);
    }
    
    .desc-box h4 {
        margin-top: 0;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .profile-tile {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .profile-tile:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    
    .profile-tile-optimized {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }
    
    .profile-tile-warning {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { 
            border-left-color: #f97316;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        50% { 
            border-left-color: #ef4444;
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
    }
    
    .drift-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        animation: pulse-badge 1.5s infinite;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.4);
    }
    
    @keyframes pulse-badge {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
            box-shadow: 0 4px 6px rgba(239, 68, 68, 0.4);
        }
        50% { 
            opacity: 0.7; 
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(239, 68, 68, 0.6);
        }
    }
    
    .success-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .metric-showcase {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.4);
    }
    
    .metric-showcase h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-showcase p {
        margin: 8px 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .stat-item {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 8px;
        word-wrap: break-word;
    }
    
    .allocation-blocked {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 3px solid #ef4444;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
        font-weight: 700;
        color: #991b1b;
        font-size: 1.1rem;
        animation: shake 0.5s;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .buying-guide {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-weight: 600;
        color: #1e40af;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .buying-guide-highlight {
        background: #1e40af;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 1rem;
        display: inline-block;
        margin: 0 2px;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1e293b;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 8px;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ===== PERSISTENCE LAYER =====
DB_FILE = "alphastream_wealth.json"

def load_db():
    base_schema = {"profiles": {}, "global_logs": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: 
                data = json.load(f)
                data.setdefault("profiles", {})
                data.setdefault("global_logs", [])
                for p in data["profiles"].values():
                    p.setdefault("drift_tolerance", 5.0)
                    p.setdefault("rebalance_stats", [])
                    p.setdefault("last_rebalanced", None)
                    p.setdefault("benchmark", None)
                return data
            except: 
                return base_schema
    return base_schema

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_profile(prof, message):
    prof.setdefault("rebalance_logs", [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    prof["rebalance_logs"].insert(0, {
        "date": timestamp, 
        "event": str(message)
    })
    prof["rebalance_logs"] = prof["rebalance_logs"][:50]

def description_box(title, content):
    st.markdown(f'''
        <div class="desc-box">
            <h4>{title}</h4>
            <div style="line-height:1.7; font-weight: 300;">{content}</div>
        </div>
    ''', unsafe_allow_html=True)

def check_recently_rebalanced(last_rebalanced_str):
    """Check if portfolio was rebalanced in last 24 hours"""
    if not last_rebalanced_str:
        return False
    try:
        last_rebal_time = datetime.strptime(last_rebalanced_str, "%Y-%m-%d %H:%M:%S")
        hours_since = (datetime.now() - last_rebal_time).total_seconds() / 3600
        return hours_since < 24
    except:
        return False

def calculate_drift_status(p_data, prices):
    """Calculate if portfolio needs rebalancing"""
    p_assets = p_data.get("assets", {})
    if not p_assets:
        return False, []
    
    curr_v = float(sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets))
    if curr_v == 0:
        return False, []
    
    has_rebalanced = p_data.get("last_rebalanced") is not None
    recently_rebalanced = check_recently_rebalanced(p_data.get("last_rebalanced"))
    
    # Never rebalanced = needs rebalance
    if not has_rebalanced:
        return True, []
    
    # Recently rebalanced = don't check drift yet
    if recently_rebalanced:
        return False, []
    
    # Check actual drift
    drift_details = []
    for t in p_assets:
        actual_pct = float((p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100))
        target_pct = float(p_assets[t]["target"])
        drift = abs(actual_pct - target_pct)
        if drift >= p_data.get("drift_tolerance", 5.0):
            drift_details.append((t, drift, actual_pct, target_pct))
    
    return len(drift_details) > 0, drift_details

# ===== SESSION STATE =====
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_page" not in st.session_state:
    st.session_state.current_page = "Global Dashboard"
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🛡️ AlphaStream")
    st.caption("Wealth Management Suite v4.0")
    
    st.divider()
    
    # Navigation
    view_mode = st.radio(
        "Navigation",
        ["🏠 Global Dashboard", "📊 Portfolio Manager"],
        key="nav_radio"
    )
    
    st.divider()
    
    # Profile Creation
    st.markdown("### ⚙️ Strategy Setup")
    with st.expander("🆕 Create New Profile", expanded=False):
        with st.form("new_profile_form"):
            n_name = st.text_input("Profile Name", placeholder="e.g., Retirement USD")
            n_curr = st.selectbox("Currency", ["USD", "CAD"])
            n_p = st.number_input("Principal ($)", value=10000.0, step=1000.0, min_value=0.0)
            n_goal = st.number_input("Annual Growth Goal (%)", value=10.0, step=0.5, min_value=0.0)
            n_start = st.date_input("Inception Date", value=date.today() - timedelta(days=365))
            
            submitted = st.form_submit_button("🚀 Initialize Profile", use_container_width=True)
            
            if submitted:
                if n_name and n_name not in st.session_state.db["profiles"]:
                    st.session_state.db["profiles"][n_name] = {
                        "currency": n_curr,
                        "principal": n_p,
                        "yearly_goal_pct": n_goal,
                        "start_date": str(n_start),
                        "assets": {},
                        "rebalance_logs": [],
                        "drift_tolerance": 5.0,
                        "rebalance_stats": [],
                        "last_rebalanced": None,
                        "benchmark": None
                    }
                    save_db(st.session_state.db)
                    log_profile(st.session_state.db["profiles"][n_name], "Profile created")
                    st.success(f"✅ Profile '{n_name}' created!")
                    st.rerun()
                elif not n_name:
                    st.error("Please enter a profile name")
                else:
                    st.warning(f"Profile '{n_name}' already exists")
    
    # Profile-specific sidebar content
    if view_mode == "📊 Portfolio Manager" and st.session_state.db["profiles"]:
        st.divider()
        st.markdown("### 🎯 Active Profile")
        
        profile_names = list(st.session_state.db["profiles"].keys())
        
        if st.session_state.active_profile and st.session_state.active_profile in profile_names:
            default_index = profile_names.index(st.session_state.active_profile)
        else:
            default_index = 0
        
        selected = st.selectbox(
            "Select Profile",
            profile_names,
            index=default_index,
            key="profile_selector"
        )
        
        if selected != st.session_state.active_profile:
            st.session_state.active_profile = selected
            st.rerun()
        
        prof = st.session_state.db["profiles"][st.session_state.active_profile]
        p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
        
        st.divider()
        
        # Drift Strategy
        st.markdown("### ⚙️ Drift Strategy")
        st.caption("Set tolerance threshold for rebalance alerts")
        new_tolerance = st.number_input(
            "Drift Tolerance (%)",
            value=float(prof.get('drift_tolerance', 5.0)),
            min_value=0.5,
            max_value=20.0,
            step=0.5,
            help="Alert when any asset drifts this much from target",
            key="drift_tolerance_input"
        )
        if st.button("💾 Update Tolerance", use_container_width=True, key="update_tolerance"):
            prof['drift_tolerance'] = new_tolerance
            save_db(st.session_state.db)
            log_profile(prof, f"Updated drift tolerance to {new_tolerance}%")
            st.success("✅ Updated!")
            st.rerun()
        
        st.divider()
        
        # Benchmark Selection
        st.markdown("### 📊 Benchmark Comparison")
        st.caption("Compare your portfolio against market benchmarks")
        
        benchmark_options = {
            "None": None,
            "S&P 500 (SPY)": "SPY",
            "NASDAQ-100 (QQQ)": "QQQ",
            "Total Market (VTI)": "VTI",
            "Russell 2000 (IWM)": "IWM",
            "Dow Jones (DIA)": "DIA"
        }
        
        current_benchmark = prof.get('benchmark')
        benchmark_index = 0
        for idx, (key, value) in enumerate(benchmark_options.items()):
            if value == current_benchmark:
                benchmark_index = idx
                break
        
        selected_benchmark = st.selectbox(
            "Select Benchmark",
            options=list(benchmark_options.keys()),
            index=benchmark_index,
            key="benchmark_select"
        )
        
        if st.button("💾 Save Benchmark", use_container_width=True, key="save_benchmark"):
            prof['benchmark'] = benchmark_options[selected_benchmark]
            save_db(st.session_state.db)
            st.success("✅ Benchmark saved!")
            st.rerun()
        
        if prof.get('benchmark'):
            st.caption(f"📊 Active: {prof['benchmark']} will appear on chart")
        else:
            st.caption("No benchmark selected")
        
        st.divider()
        
        # Asset Allocation
        st.markdown("### 🎯 Asset Allocation")
        st.caption("Add assets to your portfolio and set target percentages")
        
        with st.expander("💡 Need help finding tickers?", expanded=False):
            st.caption("**Popular Examples:**")
            st.caption("• Stocks: AAPL, MSFT, GOOGL, AMZN, TSLA")
            st.caption("• ETFs: SPY, QQQ, VTI, VOO, IWM")
            st.caption("• Bonds: AGG, BND, TLT")
            st.caption("")
            st.caption("Find more at: finance.yahoo.com")
        
        # Calculate current allocation
        current_alloc = sum(a.get('target', 0) for a in prof.get("assets", {}).values())
        
        # Allocation progress bar with color coding
        progress_color = "🟢" if current_alloc >= 100 else "🟠"
        bar_color = "#10b981" if current_alloc >= 100 else "#f97316"
        
        st.markdown(f"""
            <div style="margin: 12px 0;">
                <div style="background: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: {bar_color}; height: 100%; width: {min(current_alloc, 100)}%; transition: all 0.3s;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**{progress_color} Allocated: {current_alloc:.1f}% / 100%**")
        
        # Asset ticker input
        a_sym = st.text_input(
            "Ticker Symbol",
            placeholder="e.g., AAPL, MSFT",
            help="Enter stock ticker and press Enter",
            key="ticker_input"
        ).upper().strip()
        
        is_existing = a_sym in prof.get("assets", {})
        
        # Calculate available allocation space
        if is_existing:
            other_allocs = current_alloc - prof["assets"][a_sym].get("target", 0)
        else:
            other_allocs = current_alloc
        
        max_available = 100.0 - other_allocs
        block_new = (not is_existing) and (max_available <= 0) and (a_sym != "")
        
        # Show allocation block warning
        if block_new:
            st.markdown("""
                <div class="allocation-blocked">
                    🚫 PORTFOLIO AT 100%<br>
                    Remove or reduce existing assets first!
                </div>
            """, unsafe_allow_html=True)
        
        valid_ticker = False
        last_price = 1.0
        ticker_name = ""
        
        # Validate ticker
        if a_sym and not block_new:
            try:
                with st.spinner(f"🔍 Validating {a_sym}..."):
                    t_check = yf.Ticker(a_sym)
                    hist = t_check.history(period="1d")
                    if not hist.empty:
                        last_price = float(hist['Close'].iloc[-1])
                        try:
                            ticker_info = t_check.info
                            ticker_name = ticker_info.get('longName', a_sym)
                        except:
                            ticker_name = a_sym
                        st.success(f"✓ {ticker_name}")
                        st.caption(f"**Current Price:** {p_flag} ${last_price:,.2f}")
                        valid_ticker = True
                    else:
                        st.error(f"❌ No price data available for '{a_sym}'")
            except:
                if a_sym:
                    st.error(f"❌ Cannot validate '{a_sym}'. Please verify it's a valid stock symbol.")
                    st.caption("💡 Try: AAPL, MSFT, GOOGL, TSLA, SPY, QQQ")
        
        # Asset form
        if valid_ticker:
            st.markdown("---")
            
            default_target = prof.get("assets", {}).get(a_sym, {}).get("target", 0.0)
            default_units = prof.get("assets", {}).get(a_sym, {}).get("units", 0.0)
            
            a_w = st.number_input(
                f"Target Allocation %",
                min_value=0.0,
                max_value=max_available,
                value=min(float(default_target), max_available),
                step=0.5,
                help=f"Maximum available: {max_available:.1f}%",
                key="target_weight"
            )
            
            # Buying Guide
            if a_w > 0:
                target_value = (a_w / 100) * prof['principal']
                suggested_units = target_value / last_price
                
                st.markdown(f"""
                    <div class="buying-guide">
                        💡 <strong>Buy Guide:</strong> To reach {a_w}% → Buy <span class="buying-guide-highlight">{suggested_units:.4f} units</span> (${target_value:,.0f} @ ${last_price:,.2f}/unit)
                    </div>
                """, unsafe_allow_html=True)
            
            a_u = st.number_input(
                "Units Currently Owned",
                min_value=0.0,
                value=float(default_units),
                step=0.0001,
                format="%.4f",
                help="How many shares do you own?",
                key="units_owned"
            )
            
            st.markdown("---")
            
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                save_disabled = (a_w <= 0) or (a_w > max_available)
                if st.button("💾 Save Asset", use_container_width=True, type="primary", key="save_asset", disabled=save_disabled):
                    prof.setdefault("assets", {})[a_sym] = {"units": a_u, "target": a_w}
                    action = "Updated" if is_existing else "Added"
                    log_profile(prof, f"{action} {a_sym}: {a_w}% target, {a_u:.4f} units")
                    save_db(st.session_state.db)
                    st.success(f"✅ {action} {a_sym}!")
                    st.rerun()
            
            with col_b2:
                if is_existing:
                    if st.button("🗑️ Remove", use_container_width=True, key="remove_asset"):
                        del prof["assets"][a_sym]
                        log_profile(prof, f"Removed {a_sym} from portfolio")
                        save_db(st.session_state.db)
                        st.success(f"✅ Removed {a_sym}!")
                        st.rerun()
        
        # Show existing assets
        if prof.get("assets"):
            st.divider()
            st.markdown("### 📋 Current Assets")
            for ticker, data in prof["assets"].items():
                st.caption(f"**{ticker}**: {data['target']}% ({data['units']:.4f} units)")
        
        # Activity Log
        st.divider()
        st.markdown("### 📜 Activity Log")
        st.caption("Track all portfolio changes and updates")
        with st.expander("View Recent Activity", expanded=False):
            all_logs = prof.get("rebalance_logs", [])
            logs_to_show = all_logs[:20]
            if logs_to_show:
                for log_entry in logs_to_show:
                    st.caption(f"**{log_entry['date']}**: {log_entry['event']}")
                if len(all_logs) > 20:
                    st.caption(f"... and {len(all_logs) - 20} more entries")
            else:
                st.caption("No activity yet")

# ===== MAIN CONTENT =====
if view_mode == "🏠 Global Dashboard":
    st.title("🏠 Global Portfolio Dashboard")
    
    description_box(
        "Portfolio Command Center",
        "Monitor all your investment strategies at a glance. Track performance, detect drift, and manage multiple portfolios with institutional-grade precision."
    )
    
    profiles = st.session_state.db.get("profiles", {})
    
    if not profiles:
        st.info("👋 Welcome to AlphaStream! Create your first investment profile using the sidebar.")
        
        st.markdown("### 🎯 Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="premium-card">
                    <h4>🎯 Drift Detection</h4>
                    <p style="color: #64748b;">
                        Automatic alerts when assets deviate from target allocation. Stay disciplined with your strategy.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="premium-card">
                    <h4>📈 Performance Tracking</h4>
                    <p style="color: #64748b;">
                        Real-time portfolio valuation vs. your target growth path. See if you're on track.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="premium-card">
                    <h4>⚖️ Smart Rebalancing</h4>
                    <p style="color: #64748b;">
                        Automated calculations show exactly what to buy or sell to restore balance.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
    else:
        # Fetch all prices
        all_tickers = set()
        for p in profiles.values():
            all_tickers.update(p.get("assets", {}).keys())
        
        prices = {}
        if all_tickers:
            try:
                with st.spinner("📊 Fetching market data..."):
                    raw_px = yf.download(list(all_tickers), period="1d", progress=False)['Close']
                    if len(all_tickers) == 1:
                        if not raw_px.empty:
                            prices = {list(all_tickers)[0]: float(raw_px.iloc[-1])}
                    else:
                        for k, v in raw_px.iloc[-1].to_dict().items():
                            try:
                                if pd.notna(v):
                                    prices[k] = float(v)
                            except:
                                pass
            except:
                st.warning("⚠️ Could not fetch current prices. Portfolio values may be outdated.")
        
        # Calculate summary metrics
        total_value = 0
        total_drift_count = 0
        
        for p_data in profiles.values():
            p_assets = p_data.get("assets", {})
            curr_v = float(sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets))
            total_value += curr_v
            
            needs_rebal, _ = calculate_drift_status(p_data, prices)
            if needs_rebal:
                total_drift_count += 1
        
        # Top Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"""
                <div class="metric-showcase">
                    <h3>${total_value:,.0f}</h3>
                    <p>Total Portfolio Value</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
                <div class="metric-showcase" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <h3>{len(profiles)}</h3>
                    <p>Active Strategies</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            alert_color = "#ef4444" if total_drift_count > 0 else "#10b981"
            alert_text = f"⚠️ {total_drift_count} Need Rebalancing" if total_drift_count > 0 else f"{total_drift_count} Need Rebalancing"
            st.markdown(f"""
                <div class="metric-showcase" style="background: linear-gradient(135deg, {alert_color} 0%, {alert_color} 100%);">
                    <h3>{total_drift_count}</h3>
                    <p>{alert_text}</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Portfolio Grid
        st.markdown("### 📁 Portfolio Strategies")
        st.caption("Click any profile name to view detailed analytics and manage assets")
        
        cols = st.columns(2)
        for i, (name, p_data) in enumerate(profiles.items()):
            p_assets = p_data.get("assets", {})
            curr_v = float(sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets))
            
            has_rebalanced = p_data.get("last_rebalanced") is not None
            recently_rebalanced = check_recently_rebalanced(p_data.get("last_rebalanced"))
            needs_rebal, drift_details = calculate_drift_status(p_data, prices)
            
            # Calculate ROI and CAGR
            start_val = float(p_data.get('principal', 0))
            roi_pct = ((curr_v / start_val) - 1) * 100 if start_val > 0 else 0
            
            start_date = datetime.strptime(p_data.get('start_date', str(date.today())), '%Y-%m-%d')
            years_elapsed = max((date.today() - start_date.date()).days / 365.25, 0.01)
            cagr = ((curr_v / start_val) ** (1 / years_elapsed) - 1) * 100 if start_val > 0 and years_elapsed > 0 else 0
            
            p_flag = "🇺🇸" if p_data.get("currency") == "USD" else "🇨🇦"
            
            # Determine status
            if not has_rebalanced and len(p_assets) > 0:
                tile_class = "profile-tile-warning"
                status_badge = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            elif not has_rebalanced:
                tile_class = "profile-tile"
                status_badge = '<span style="background: #94a3b8; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚪ Not Rebalanced</span>'
            elif recently_rebalanced:
                tile_class = "profile-tile-optimized"
                status_badge = '<span class="success-badge">✅ Balanced</span>'
            elif needs_rebal:
                tile_class = "profile-tile-warning"
                status_badge = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            else:
                tile_class = "profile-tile-optimized"
                status_badge = '<span class="success-badge">✅ Balanced</span>'
            
            with cols[i % 2]:
                # Clickable title button
                if st.button(f"{p_flag} {name}", key=f"title_{name}", use_container_width=True, type="secondary"):
                    st.session_state.active_profile = name
                    st.rerun()
                
                # Profile tile
                st.markdown(f"""
                    <div class="{tile_class}" style="cursor: pointer; padding: 24px; margin-top: 0px;">
                        <div style="margin-bottom: 16px; text-align: center;">
                            {status_badge}
                        </div>
                        <div style="margin: 20px 0; text-align: center;">
                            <div class="stat-label">Portfolio Value</div>
                            <div class="stat-value" style="font-size: 2rem;">${curr_v:,.0f}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 0.9rem; color: #64748b;">
                            <div>
                                <div style="font-size: 0.75rem; opacity: 0.8;">Goal</div>
                                <div style="font-weight: 600;">{p_data['yearly_goal_pct']}%/yr</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.75rem; opacity: 0.8;">CAGR</div>
                                <div style="font-weight: 700; color: {'#10b981' if cagr >= 0 else '#ef4444'};">
                                    {cagr:+.1f}%
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 0.75rem; opacity: 0.8;">ROI</div>
                                <div style="font-weight: 700; color: {'#10b981' if roi_pct >= 0 else '#ef4444'};">
                                    {roi_pct:+.1f}%
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if needs_rebal and drift_details:
                    with st.expander("⚠️ View Drift Details", expanded=False):
                        for t, drift, actual, target in drift_details:
                            st.caption(f"• {t}: {drift:.1f}% drift")
                
                st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

else:  # Portfolio Manager
    if not st.session_state.active_profile or st.session_state.active_profile not in st.session_state.db["profiles"]:
        st.warning("⚠️ No profile selected. Please select a profile from the sidebar.")
        st.stop()
    
    prof = st.session_state.db["profiles"][st.session_state.active_profile]
    p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
    
    st.title(f"{p_flag} {st.session_state.active_profile}")
    st.caption(f"Portfolio Manager • Inception: {prof.get('start_date', 'N/A')} • Drift Tolerance: {prof.get('drift_tolerance', 5.0)}%")
    
    # Portfolio Summary at top
    has_rebalanced = prof.get("last_rebalanced") is not None
    recently_rebalanced = check_recently_rebalanced(prof.get("last_rebalanced"))
    
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    with col_sum1:
        asset_count = len(prof.get("assets", {}))
        st.metric("Total Assets", asset_count)
    with col_sum2:
        prof_start = datetime.strptime(prof.get('start_date', str(date.today())), '%Y-%m-%d')
        age_years = max((date.today() - prof_start.date()).days / 365.25, 0.01)
        st.metric("Portfolio Age", f"{age_years:.1f} years")
    with col_sum3:
        if prof.get("last_rebalanced"):
            st.metric("Last Rebalanced", prof["last_rebalanced"][:10])
        else:
            st.metric("Last Rebalanced", "Never")
    with col_sum4:
        if has_rebalanced:
            if recently_rebalanced:
                st.metric("Status", "✅ Balanced", delta="Optimized", delta_color="normal")
            else:
                st.metric("Status", "Active", delta="Monitoring", delta_color="off")
        else:
            st.metric("Status", "⚪ New", delta="Not rebalanced", delta_color="off")
    
    st.divider()
    
    asset_dict = prof.get("assets", {})
    tickers = list(asset_dict.keys())
    
    if not tickers:
        st.info("👈 **Add your first asset using the sidebar** to start tracking your portfolio")
        st.markdown("""
        ### 📝 Quick Start Guide:
        1. Enter a ticker symbol (e.g., AAPL, MSFT, VTI)
        2. Set your target allocation percentage
        3. See the **buying guide** showing exact units needed
        4. Enter units you currently own
        5. Click **Save Asset**
        """)
        st.stop()
    
    # Fetch data and analyze
    with st.spinner("📊 Analyzing portfolio..."):
        try:
            raw = yf.download(tickers, start=prof["start_date"], auto_adjust=True, progress=False)
            
            if raw.empty:
                st.error("❌ Could not fetch historical data. Please check your tickers and date range.")
                st.stop()
            
            data = raw['Close']
            if len(tickers) == 1:
                data = pd.DataFrame(data, columns=tickers)
            
            v_t = [t for t in tickers if t in data.columns]
            
            if not v_t:
                st.error("❌ No valid ticker data found. Please check your asset symbols.")
                st.stop()
            
            if len(v_t) < len(tickers):
                missing = set(tickers) - set(v_t)
                st.warning(f"⚠️ Could not load data for: {', '.join(missing)}")
            
            # Calculate portfolio metrics
            daily_val = data[v_t].apply(
                lambda r: sum(r[t] * asset_dict[t]["units"] for t in v_t if t in r.index),
                axis=1
            )
            
            curr_v = float(daily_val.iloc[-1])
            start_val = float(prof['principal'])
            
            years = max((data.index[-1] - data.index[0]).days / 365.25, 0.01)
            target_val = start_val * (1 + (float(prof['yearly_goal_pct'])/100))**years
            perc_diff = ((curr_v / target_val) - 1) * 100
            roi_pct = ((curr_v / start_val) - 1) * 100
            
            # Calculate CAGR
            prof_start_date = datetime.strptime(prof.get('start_date', str(date.today())), '%Y-%m-%d')
            prof_years = max((date.today() - prof_start_date.date()).days / 365.25, 0.01)
            profile_cagr = ((curr_v / start_val) ** (1 / prof_years) - 1) * 100 if start_val > 0 else 0
            
            # Drift detection
            recently_rebalanced = check_recently_rebalanced(prof.get("last_rebalanced"))
            needs_rebalance = False
            drift_assets = []
            
            if not recently_rebalanced:
                for t in v_t:
                    actual_pct = float((asset_dict[t]["units"] * data[t].iloc[-1] / curr_v * 100))
                    target_pct = float(asset_dict[t]["target"])
                    drift = float(abs(actual_pct - target_pct))
                    
                    if drift >= prof.get("drift_tolerance", 5.0):
                        needs_rebalance = True
                        drift_assets.append((t, drift, actual_pct, target_pct))
            
            # Drift alert banner
            if needs_rebalance:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                border: 4px solid #ef4444; border-radius: 16px; padding: 28px; 
                                margin-bottom: 28px;">
                        <h2 style="color: #991b1b; margin: 0 0 16px 0; font-size: 1.8rem;">
                            🚨 DRIFT ALERT: Immediate Rebalancing Required
                        </h2>
                        <p style="color: #7f1d1d; font-size: 1.2rem; margin: 0; line-height: 1.6;">
                            <strong>{len(drift_assets)} asset(s)</strong> have exceeded your <strong>{prof.get('drift_tolerance', 5.0)}% drift tolerance</strong>.<br>
                            Your portfolio allocation has shifted significantly. Review the analysis below and execute rebalancing.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📊 Assets Requiring Rebalancing:")
                for ticker, drift, actual, target in drift_assets:
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.markdown(f"**{ticker}**")
                    with col2:
                        st.markdown(f"Drift: **{drift:.2f}%** ⚠️")
                    with col3:
                        st.markdown(f"Current: **{actual:.1f}%** (Target: {target:.1f}%)")
                
                st.divider()
            
            # Determine status badge
            has_rebalanced = prof.get("last_rebalanced") is not None
            has_assets = len(asset_dict) > 0
            
            if not has_rebalanced and has_assets:
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            elif not has_rebalanced:
                alert_html = '<span style="background: #94a3b8; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚪ Not Rebalanced</span>'
            elif recently_rebalanced:
                alert_html = '<span class="success-badge">✅ Balanced</span>'
            elif needs_rebalance:
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            else:
                alert_html = '<span class="success-badge">✅ Balanced</span>'
            
            # Header
            st.markdown(f"""
                <div class="premium-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h2 style="margin:0;">Portfolio Analytics</h2>
                        {alert_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Key Metrics
            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
            
            with col_s1:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Current Value</div>
                        <div class="stat-value">${curr_v:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s2:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Total ROI</div>
                        <div class="stat-value" style="color: {'#10b981' if roi_pct >= 0 else '#ef4444'};">
                            {roi_pct:+.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s3:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">CAGR</div>
                        <div class="stat-value" style="color: {'#10b981' if profile_cagr >= 0 else '#ef4444'};">
                            {profile_cagr:+.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s4:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">vs Target Path</div>
                        <div class="stat-value" style="color: {'#10b981' if perc_diff >= 0 else '#ef4444'};">
                            {perc_diff:+.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s5:
                annualized = ((curr_v / start_val) ** (1/years) - 1) * 100
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Annualized Return</div>
                        <div class="stat-value" style="color: {'#10b981' if annualized >= 0 else '#ef4444'};">
                            {annualized:.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Performance Chart
            st.markdown("### 📈 Performance vs Goal Path")
            benchmark_caption = f" & 100% {prof.get('benchmark', '')}" if prof.get('benchmark') else ""
            st.caption(f"Track your portfolio's actual performance against your target growth trajectory{benchmark_caption}")
            
            fig = go.Figure()
            
            # Actual portfolio
            fig.add_trace(go.Scatter(
                x=data.index,
                y=daily_val,
                name='Actual Portfolio',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)',
                hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                             '<b>Portfolio Value:</b> $%{y:,.2f}<br>' +
                             '<b>Performance:</b> Actual<br>' +
                             '<extra></extra>'
            ))
            
            # Goal path
            days = np.arange(len(data.index))
            daily_rate = (float(prof['yearly_goal_pct']) / 100) / 365.25
            target_path = start_val * (1 + daily_rate) ** days
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=target_path,
                name=f'Goal Path ({prof["yearly_goal_pct"]}%/yr)',
                line=dict(color='#10b981', width=2, dash='dash'),
                hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                             '<b>Target Value:</b> $%{y:,.2f}<br>' +
                             f'<b>Goal Rate:</b> {prof["yearly_goal_pct"]}% annually<br>' +
                             '<extra></extra>'
            ))
            
            # Benchmark comparison (100% invested in benchmark)
            benchmark_ticker = prof.get('benchmark')
            benchmark_comparison_msg = None
            
            if benchmark_ticker:
                try:
                    benchmark_raw = yf.download(benchmark_ticker, start=prof["start_date"], auto_adjust=True, progress=False)
                    if not benchmark_raw.empty:
                        benchmark_data = benchmark_raw['Close']
                        
                        # Show what would happen if 100% was invested in benchmark
                        benchmark_normalized = (benchmark_data / float(benchmark_data.iloc[0])) * start_val
                        bench_return = ((float(benchmark_normalized.iloc[-1]) / start_val) - 1) * 100
                        bench_final_value = float(benchmark_normalized.iloc[-1])
                        
                        fig.add_trace(go.Scatter(
                            x=benchmark_data.index,
                            y=benchmark_normalized,
                            name=f'100% in {benchmark_ticker} ({bench_return:+.1f}%)',
                            line=dict(color='#f59e0b', width=2, dash='dot'),
                            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                                         '<b>Value if 100% in Benchmark:</b> $%{y:,.2f}<br>' +
                                         f'<b>Benchmark:</b> {benchmark_ticker}<br>' +
                                         f'<b>Total Return:</b> {bench_return:+.1f}%<br>' +
                                         '<extra></extra>'
                        ))
                        
                        # Prepare comparison message
                        portfolio_vs_bench = curr_v - bench_final_value
                        if portfolio_vs_bench > 0:
                            benchmark_comparison_msg = ("success", f"📊 Your portfolio outperformed {benchmark_ticker} by ${portfolio_vs_bench:,.0f} ({((curr_v/bench_final_value - 1)*100):+.1f}%)")
                        else:
                            benchmark_comparison_msg = ("info", f"📊 {benchmark_ticker} outperformed your portfolio by ${abs(portfolio_vs_bench):,.0f} ({((bench_final_value/curr_v - 1)*100):+.1f}%)")
                    else:
                        st.caption(f"⚠️ No benchmark data available for {benchmark_ticker}")
                except Exception as e:
                    st.caption(f"⚠️ Could not load benchmark {benchmark_ticker}")
            
            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='white',
                height=550,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=14,
                    font_family="Inter, sans-serif",
                    bordercolor="#e2e8f0"
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    title='Date',
                    title_font=dict(size=14, color='#64748b')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    title='Portfolio Value ($)',
                    title_font=dict(size=14, color='#64748b')
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12)
                ),
                margin=dict(l=60, r=40, t=40, b=60)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show benchmark comparison if available
            if benchmark_comparison_msg:
                msg_type, msg_text = benchmark_comparison_msg
                if msg_type == "success":
                    st.success(msg_text)
                else:
                    st.info(msg_text)
            
            st.divider()
            
            # Rebalance Analysis
            st.markdown("### ⚖️ Rebalance Analysis")
            st.caption("Review asset allocation drift and required trades to restore target percentages")
            
            rows = []
            total_turnover = 0
            total_current_val = 0
            
            for t in v_t:
                current_price = float(data[t].iloc[-1])
                try:
                    prev_price = float(data[t].iloc[-2])
                    daily_change_pct = ((current_price / prev_price) - 1) * 100
                except:
                    daily_change_pct = 0.0
                
                ticker_name = t
                try:
                    ticker_obj = yf.Ticker(t)
                    info = ticker_obj.info
                    if info and 'longName' in info:
                        ticker_name = info.get('longName', t)
                except:
                    pass
                
                cur_u = float(asset_dict[t]["units"])
                tar_w = float(asset_dict[t]['target'])
                
                act_val = cur_u * current_price
                act_w = (act_val / curr_v * 100)
                drift = act_w - tar_w
                
                tar_val = (tar_w / 100) * curr_v
                tar_u = tar_val / current_price
                
                val_diff = tar_val - act_val
                unit_diff = tar_u - cur_u
                
                total_turnover += abs(val_diff)
                total_current_val += act_val
                
                if abs(drift) < 0.1:
                    action = "—"
                else:
                    action = "BUY" if drift < 0 else "SELL"
                
                drift_display = f"{drift:+.2f}%"
                if abs(drift) >= prof.get("drift_tolerance", 5.0):
                    drift_display = f"🔴 {drift:+.2f}%"
                elif abs(drift) > 0.5:
                    drift_display = f"🟡 {drift:+.2f}%"
                else:
                    drift_display = f"🟢 {drift:+.2f}%"
                
                daily_change_display = f"{daily_change_pct:+.2f}%"
                
                rows.append({
                    "Asset Class": ticker_name,
                    "Fund": t,
                    "Units": f"{cur_u:.0f}",
                    "Unit Value": f"${current_price:.2f}",
                    "%Daily Change": daily_change_display,
                    "Amount": f"${act_val:,.0f}",
                    "Allocation": f"{act_w:.2f}%",
                    "Target": f"{tar_w:.2f}%",
                    "Drift": drift_display,
                    "Buy/Sell Amt": f"${abs(val_diff):,.0f}",
                    "Buy/Sell Shares": f"{unit_diff:+.0f}"
                })
            
            # Total row
            rows.append({
                "Asset Class": "**TOTAL**",
                "Fund": "",
                "Units": "",
                "Unit Value": "",
                "%Daily Change": "",
                "Amount": f"**${total_current_val:,.0f}**",
                "Allocation": "**100.00%**",
                "Target": "**100.00%**",
                "Drift": "—",
                "Buy/Sell Amt": f"**${total_turnover:,.0f}**",
                "Buy/Sell Shares": "—"
            })
            
            df_rebalance = pd.DataFrame(rows)
            st.dataframe(df_rebalance, use_container_width=True, hide_index=True)
            
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("CAGR", f"{profile_cagr:.2f}%", help="Compound Annual Growth Rate")
            with col_metric2:
                st.metric("Total Trade Volume", f"${total_turnover:,.0f}", help="Total dollar amount needed to rebalance")
            
            st.divider()
            
            # Execution
            col_exec1, col_exec2 = st.columns(2)
            
            with col_exec1:
                st.markdown("### 🚀 Execute Rebalance")
                st.caption("Adjust portfolio units to match target allocation")
                
                if needs_rebalance:
                    st.warning("⚠️ **Rebalancing recommended**")
                
                if st.button("⚡ Execute Rebalancing", type="primary", use_container_width=True, disabled=not needs_rebalance):
                    detail_log = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - "
                    changes = []
                    
                    for t in v_t:
                        old_units = float(asset_dict[t]["units"])
                        new_units = float((asset_dict[t]["target"] / 100 * curr_v) / data[t].iloc[-1])
                        asset_dict[t]["units"] = new_units
                        
                        change_val = new_units - old_units
                        if abs(change_val) > 0.0001:
                            action_color = "🟢" if change_val > 0 else "🔴"
                            action_text = "BUY" if change_val > 0 else "SELL"
                            changes.append(f"{action_color} {t} {action_text} {abs(change_val):.4f}")
                    
                    detail_log += ", ".join(changes) if changes else "No changes needed"
                    
                    prof.setdefault("rebalance_stats", []).insert(0, detail_log)
                    prof["rebalance_stats"] = prof["rebalance_stats"][:50]
                    prof["last_rebalanced"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    log_profile(prof, "Portfolio rebalanced to target allocations - Status: Balanced")
                    save_db(st.session_state.db)
                    
                    st.success("✅ Portfolio rebalanced successfully! Status: **Balanced** ✅")
                    st.balloons()
                    st.rerun()
                
                if not needs_rebalance:
                    st.info("✓ Portfolio is optimally balanced")
            
            with col_exec2:
                st.markdown("### 📊 Rebalance History Details")
                st.caption("Detailed log of past rebalancing events")
                
                total_events = len(prof.get('rebalance_stats', []))
                if total_events > 0:
                    st.caption(f"Total events: {total_events}")
                    for entry in prof.get("rebalance_stats", [])[:10]:
                        st.caption(entry)
                    
                    if total_events > 10:
                        with st.expander(f"📜 Show {total_events - 10} More Events"):
                            for entry in prof.get("rebalance_stats", [])[10:30]:
                                st.caption(entry)
                else:
                    st.info("No rebalancing history yet")
                
                st.divider()
                
                st.markdown("#### 💡 Quick Tips")
                st.caption("• Regular rebalancing maintains target allocation")
                st.caption("• Drift tolerance controls when alerts trigger")
                st.caption("• Check Activity Log in sidebar for history")
        
        except Exception as e:
            st.error(f"❌ Error analyzing portfolio: {str(e)}")
            st.info("💡 Please check your internet connection and verify all ticker symbols are valid.")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 20px;">
        <p><strong>AlphaStream Wealth Master</strong> • v4.0</p>
        <p style="font-size: 0.85rem;">Market data by Yahoo Finance • For informational purposes only</p>
    </div>
""", unsafe_allow_html=True)
