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
    
    .premium-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
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
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); /* Light blue background for optimized state */
    }
    
    .profile-tile-warning {
        border-left: 4px solid #ef4444;
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { border-left-color: #f59e0b; }
        50% { border-left-color: #ef4444; }
    }
    
    .drift-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        animation: pulse-badge 1.5s infinite; /* Blinking animation for rebalance required */
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
            box-shadow: 0 6px 12px rgba(239, 68, 68, 0.6); /* Enhanced blink effect */
        }
    }
    
    .success-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%); /* Green gradient for optimized state */
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3); /* Green shadow for emphasis */
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
        word-wrap: break-word; /* Prevent overflow */
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
        margin-bottom: 8px; /* Reduce gap between button and card */
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 2px solid #e2e8f0;
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
                        "last_rebalanced": None
                    }
                    save_db(st.session_state.db)
                    log_profile(st.session_state.db["profiles"][n_name], "Profile created")
                    st.success(f"✅ Profile '{n_name}' created!")
                    st.rerun()
                elif not n_name:
                    st.error("Please enter a profile name")
                else:
                    st.warning(f"Profile '{n_name}' already exists")
    
    # ===== ASSET ALLOCATION SECTION (IN SIDEBAR) =====
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
        
        # Get active profile
        prof = st.session_state.db["profiles"][st.session_state.active_profile]
        p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
        
        st.divider()
        
        # Drift Strategy Settings
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
        
        # ===== ASSET ALLOCATION - NOW IN SIDEBAR =====
        st.markdown("### 🎯 Asset Allocation")
        st.caption("Add assets to your portfolio and set target percentages")
        st.markdown("**Add or Update Assets**")
        
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
            # If editing existing, exclude its current allocation
            other_allocs = current_alloc - prof["assets"][a_sym].get("target", 0)
        else:
            other_allocs = current_alloc
        
        max_available = 100.0 - other_allocs
        
        # Check if new asset is blocked
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
        
        # Validate ticker if entered and not blocked
        if a_sym and not block_new:
            try:
                with st.spinner(f"🔍 Validating {a_sym}..."):
                    t_check = yf.Ticker(a_sym)
                    hist = t_check.history(period="1d")
                    if not hist.empty:
                        last_price = hist['Close'].iloc[-1]
                        ticker_info = t_check.info
                        ticker_name = ticker_info.get('longName', a_sym)
                        st.success(f"✓ {ticker_name}")
                        st.caption(f"**Current Price:** {p_flag} ${last_price:,.2f}")
                        valid_ticker = True
                    else:
                        st.error(f"❌ No data found for {a_sym}")
            except Exception as e:
                if a_sym:
                    st.error(f"❌ Invalid ticker: {a_sym}")
        
        # Asset allocation form (only if valid ticker)
        if valid_ticker:
            st.markdown("---")
            
            # Get default values if editing
            default_target = prof.get("assets", {}).get(a_sym, {}).get("target", 0.0)
            default_units = prof.get("assets", {}).get(a_sym, {}).get("units", 0.0)
            
            # Target percentage with STRICT maximum enforcement
            a_w = st.number_input(
                f"Target Allocation %",
                min_value=0.0,
                max_value=max_available,
                value=min(float(default_target), max_available),
                step=0.5,
                help=f"Maximum available: {max_available:.1f}%",
                key="target_weight"
            )
            
            # BUYING GUIDE - Shows immediately when target > 0
            if a_w > 0:
                target_value = (a_w / 100) * prof['principal']
                suggested_units = target_value / last_price
                
                st.markdown(f"""
                    <div class="buying-guide">
                        💡 <strong>Buy Guide:</strong> To reach {a_w}% → Buy <span class="buying-guide-highlight">{suggested_units:.4f} units</span> (${target_value:,.0f} @ ${last_price:,.2f}/unit)
                    </div>
                """, unsafe_allow_html=True)
            
            # Units owned input
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
            
            # Action buttons
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
        
        # Activity Log in Sidebar
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
        # Fetch all prices once
        all_tickers = set()
        for p in profiles.values():
            all_tickers.update(p.get("assets", {}).keys())
        
        prices = {}
        if all_tickers:
            try:
                with st.spinner("📊 Fetching market data..."):
                    raw_px = yf.download(list(all_tickers), period="1d", progress=False)['Close']
                    if len(all_tickers) == 1:
                        prices = {list(all_tickers)[0]: float(raw_px.iloc[-1])}
                    else:
                        prices = {k: float(v) for k, v in raw_px.iloc[-1].to_dict().items()}
            except Exception as e:
                st.warning(f"⚠️ Could not fetch prices: {str(e)}")
        
        # Summary Metrics
        total_value = 0
        total_drift_count = 0
        
        for p_data in profiles.values():
            p_assets = p_data.get("assets", {})
            curr_v = float(sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets))
            total_value += curr_v
            
            # Check if rebalance required
            has_rebalanced = p_data.get("last_rebalanced") is not None
            has_assets = len(p_assets) > 0
            
            # Count as needing rebalance if: (1) never rebalanced with assets OR (2) has drift after rebalancing
            if not has_rebalanced and has_assets:
                # Never rebalanced but has assets - needs rebalance
                total_drift_count += 1
            elif has_rebalanced and curr_v > 0:
                # Check for actual drift only if previously rebalanced
                for t in p_assets:
                    actual_pct = float((p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100))
                    target_pct = float(p_assets[t]["target"])
                    if abs(actual_pct - target_pct) >= p_data.get("drift_tolerance", 5.0):
                        total_drift_count += 1
                        break
        
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
            
            # Check if profile has been rebalanced
            has_rebalanced = p_data.get("last_rebalanced") is not None
            
            # Check for drift
            has_drift = False
            drift_details = []
            if curr_v > 0 and has_rebalanced:
                for t in p_assets:
                    actual_pct = float((p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100))
                    target_pct = float(p_assets[t]["target"])
                    drift = abs(actual_pct - target_pct)
                    if drift >= p_data.get("drift_tolerance", 5.0):
                        has_drift = True
                        drift_details.append(f"{t}: {drift:.1f}% drift")
            
            # Calculate ROI and CAGR
            start_val = float(p_data.get('principal', 0))
            roi_pct = ((curr_v / start_val) - 1) * 100 if start_val > 0 else 0
            
            # Calculate CAGR (Compound Annual Growth Rate)
            start_date = datetime.strptime(p_data.get('start_date', str(date.today())), '%Y-%m-%d')
            years_elapsed = max((date.today() - start_date.date()).days / 365.25, 0.01)
            cagr = ((curr_v / start_val) ** (1 / years_elapsed) - 1) * 100 if start_val > 0 and years_elapsed > 0 else 0
            
            p_flag = "🇺🇸" if p_data.get("currency") == "USD" else "🇨🇦"
            
            # Determine status - show rebalance required if never rebalanced with assets OR has drift
            if not has_rebalanced and len(p_assets) > 0:
                # Profile has assets but never rebalanced - show blinking rebalance required
                tile_class = "profile-tile-warning"
                status_badge = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            elif not has_rebalanced:
                # Profile has no assets yet
                tile_class = "profile-tile"
                status_badge = '<span style="background: #94a3b8; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚪ Not Rebalanced</span>'
            elif has_drift:
                # Profile rebalanced before but now has drift - show blinking rebalance required
                tile_class = "profile-tile-warning"
                status_badge = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            else:
                # Profile is optimized - green status after rebalance execution
                tile_class = "profile-tile-optimized"
                status_badge = '<span class="success-badge">✅ Optimized</span>'
            
            with cols[i % 2]:
                # Clickable title button - navigates to profile page on click
                if st.button(f"{p_flag} {name}", key=f"title_{name}", use_container_width=True, type="secondary"):
                    st.session_state.active_profile = name
                    st.rerun()
                
                # Profile tile with clean layout
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
                            <div style="text-align: right;">
                                <div style="font-size: 0.75rem; opacity: 0.8;">ROI</div>
                                <div style="font-weight: 700; color: {'#10b981' if roi_pct >= 0 else '#ef4444'};">
                                    {roi_pct:+.1f}%
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if has_drift:
                    with st.expander("⚠️ View Drift Details", expanded=False):
                        for detail in drift_details:
                            st.caption(f"• {detail}")
                
                # Add spacing between tiles
                st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

else:  # Portfolio Manager
    if not st.session_state.active_profile or st.session_state.active_profile not in st.session_state.db["profiles"]:
        st.warning("⚠️ No profile selected. Please select a profile from the sidebar.")
        st.stop()
    
    prof = st.session_state.db["profiles"][st.session_state.active_profile]
    p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
    
    st.title(f"{p_flag} {st.session_state.active_profile}")
    
    # Calculate CAGR for header display
    prof_start_date = datetime.strptime(prof.get('start_date', str(date.today())), '%Y-%m-%d')
    prof_years = max((date.today() - prof_start_date.date()).days / 365.25, 0.01)
    
    st.caption(f"Portfolio Manager • Inception: {prof.get('start_date', 'N/A')} • Drift Tolerance: {prof.get('drift_tolerance', 5.0)}%")
    
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
            
            # Calculate daily portfolio value
            daily_val = data[v_t].apply(
                lambda r: sum(r[t] * asset_dict[t]["units"] for t in v_t if t in r.index),
                axis=1
            )
            
            curr_v = float(daily_val.iloc[-1])
            start_val = float(prof['principal'])
            
            # Calculate time-based metrics
            years = max((data.index[-1] - data.index[0]).days / 365.25, 0.01)
            target_val = start_val * (1 + (float(prof['yearly_goal_pct'])/100))**years
            perc_diff = ((curr_v / target_val) - 1) * 100
            roi_pct = ((curr_v / start_val) - 1) * 100
            
            # DRIFT DETECTION
            needs_rebalance = False
            drift_assets = []
            
            for t in v_t:
                actual_pct = float((asset_dict[t]["units"] * data[t].iloc[-1] / curr_v * 100))
                target_pct = float(asset_dict[t]["target"])
                drift = float(abs(actual_pct - target_pct))
                
                if drift >= prof.get("drift_tolerance", 5.0):
                    needs_rebalance = True
                    drift_assets.append((t, drift, actual_pct, target_pct))
            
            # DRIFT ALERT BANNER
            if needs_rebalance:
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                border: 4px solid #ef4444; border-radius: 16px; padding: 28px; 
                                margin-bottom: 28px; animation: pulse-alert 2s infinite;">
                        <h2 style="color: #991b1b; margin: 0 0 16px 0; font-size: 1.8rem;">
                            🚨 DRIFT ALERT: Immediate Rebalancing Required
                        </h2>
                        <p style="color: #7f1d1d; font-size: 1.2rem; margin: 0; line-height: 1.6;">
                            <strong>{0} asset(s)</strong> have exceeded your <strong>{1}% drift tolerance</strong>.<br>
                            Your portfolio allocation has shifted significantly. Review the analysis below and execute rebalancing.
                        </p>
                    </div>
                    <style>
                    @keyframes pulse-alert {{
                        0%, 100% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.01); }}
                    }}
                    </style>
                """.format(len(drift_assets), prof.get('drift_tolerance', 5.0)), unsafe_allow_html=True)
                
                # Drift details
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
            
            # Determine status badge - consistent with global dashboard
            has_rebalanced = prof.get("last_rebalanced") is not None
            has_assets = len(asset_dict) > 0
            
            if not has_rebalanced and has_assets:
                # Profile has assets but never rebalanced - show blinking rebalance required
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            elif not has_rebalanced:
                # Profile has no assets yet
                alert_html = '<span style="background: #94a3b8; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚪ Not Rebalanced</span>'
            elif needs_rebalance:
                # Profile rebalanced before but now has drift - show blinking rebalance required
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            else:
                # Profile is optimized - green status after rebalance execution
                alert_html = '<span class="success-badge">✅ Optimized</span>'
            
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
                # Calculate CAGR for display
                profile_cagr = ((curr_v / start_val) ** (1 / prof_years) - 1) * 100 if start_val > 0 else 0
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
            st.caption("Track your portfolio's actual performance against your target growth trajectory")
            
            fig = go.Figure()
            
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
            
            st.divider()
            
            # Rebalance Analysis
            st.markdown("### ⚖️ Rebalance Analysis")
            st.caption("Review asset allocation drift and required trades to restore target percentages")
            
            rows = []
            total_turnover = 0
            total_current_val = 0
            total_target_val = 0
            
            for t in v_t:
                p = float(data[t].iloc[-1])
                cur_u = float(asset_dict[t]["units"])
                tar_w = float(asset_dict[t]['target'])
                
                act_val = cur_u * p
                act_w = (act_val / curr_v * 100)
                drift = act_w - tar_w
                
                tar_val = (tar_w / 100) * curr_v
                tar_u = tar_val / p
                
                val_diff = tar_val - act_val
                unit_diff = tar_u - cur_u
                
                total_turnover += abs(val_diff)
                total_current_val += act_val
                total_target_val += tar_val
                
                if abs(drift) < 0.1:
                    action = "—"
                else:
                    action = "BUY" if drift < 0 else "SELL"
                
                # Color code drift
                drift_color = "🔴" if drift < -0.5 else ("🟢" if drift > 0.5 else "⚪")
                
                rows.append({
                    "Ticker": t,
                    "Current %": f"{act_w:.2f}%",
                    "Target %": f"{tar_w:.2f}%",
                    "Drift": f"{drift_color} {drift:+.2f}%",
                    "Action": action,
                    "Units Δ": f"{unit_diff:+.4f}",
                    "Value Δ": f"${val_diff:+,.2f}"
                })
            
            # Add total row
            rows.append({
                "Ticker": "**TOTAL**",
                "Current %": "100.00%",
                "Target %": "100.00%",
                "Drift": "—",
                "Action": "—",
                "Units Δ": "—",
                "Value Δ": f"**${total_turnover:,.2f}**"
            })
            
            df_rebalance = pd.DataFrame(rows)
            st.dataframe(df_rebalance, use_container_width=True, hide_index=True)
            
            st.caption(f"📊 Total Trade Volume: **${total_turnover:,.2f}**")
            
            st.divider()
            
            # Execution
            col_exec1, col_exec2 = st.columns(2)
            
            with col_exec1:
                st.markdown("### 🚀 Execute Rebalance")
                st.caption("Adjust portfolio units to match target allocation")
                
                if needs_rebalance:
                    st.warning("⚠️ **Rebalancing recommended**")
                else:
                    st.success("✓ **Portfolio optimally balanced**")
                
                if st.button("⚡ Execute Rebalancing", type="primary", use_container_width=True, disabled=not needs_rebalance):
                    detail_log = f"Rebalanced at {datetime.now().strftime('%Y-%m-%d %H:%M')} - "
                    changes = []
                    
                    for t in v_t:
                        old_units = float(asset_dict[t]["units"])
                        new_units = float((asset_dict[t]["target"] / 100 * curr_v) / data[t].iloc[-1])
                        asset_dict[t]["units"] = new_units
                        changes.append(f"{t}: {new_units-old_units:+.4f}")
                    
                    detail_log += ", ".join(changes)
                    prof.setdefault("rebalance_stats", []).insert(0, detail_log)
                    prof["rebalance_stats"] = prof["rebalance_stats"][:20]
                    log_profile(prof, "Portfolio rebalanced")
                    save_db(st.session_state.db)
                    
                    st.success("✅ Rebalanced!")
                    st.balloons()
                    st.rerun()
                
                st.markdown("#### 📊 Rebalance History")
                for entry in prof.get("rebalance_stats", [])[:5]:
                    st.caption(entry)
            
            with col_exec2:
                st.markdown("### 📜 Activity Log")
                for log_entry in prof.get("rebalance_logs", [])[:10]:
                    st.caption(f"**{log_entry['date']}**: {log_entry['event']}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 20px;">
        <p><strong>AlphaStream Wealth Master</strong> • v4.0</p>
        <p style="font-size: 0.85rem;">Market data by Yahoo Finance • For informational purposes only</p>
    </div>
""", unsafe_allow_html=True)
