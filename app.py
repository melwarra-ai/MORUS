import streamlit as st
import pandas as pd
import altair as alt
import json
import os
import streamlit.components.v1 as components

# --- 1. PERSISTENCE ENGINE (Save Data to File) ---
SAVE_FILE = "retirement_data.json"

def save_to_file(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        return False

def load_from_file():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Load data immediately on app startup
saved_data = load_from_file()

# --- 2. CONFIGURATION & PRINT STYLING ---
st.set_page_config(page_title="Retirement Architect Pro", layout="wide")

# CSS to hide buttons/sidebar when printing to PDF
st.markdown("""
    <style>
    @media print {
        div[data-testid="stSidebar"], div.stButton, button, header, footer, .stDownloadButton { display: none !important; }
        .main .block-container { padding-top: 1rem !important; max-width: 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Retirement Architect: Master Strategy Pro")

# --- 3. SIDEBAR: INPUTS WITH PERSISTENCE ---
with st.sidebar:
    st.header("👤 Income Profile")
    
    # T4 Gross Input (Specific Label & Help Text)
    t4_gross_other = st.number_input(
        "T4 Gross Income", 
        value=saved_data.get("t4_gross_other", 0), 
        help="This is the T4 gross reported in T4 document",
        key="t4_gross_other"
    )
    
    base_salary = st.number_input(
        "Annual Base Salary ($)", 
        value=saved_data.get("base_salary", 180000), 
        step=5000, 
        key="base_salary"
    )
    
    bonus_pct = st.slider(
        "Target Bonus (%)", 
        0, 50, 
        value=saved_data.get("bonus_pct", 15), 
        key="bonus_pct"
    )
    
    st.header("💰 RRSP & TFSA")
    biweekly_pct = st.slider(
        "Biweekly Contribution (%)", 0.0, 18.0, 
        value=saved_data.get("biweekly_pct", 6.0), 
        key="biweekly_pct"
    )
    
    employer_match = st.slider(
        "Employer Match (%)", 0.0, 10.0, 
        value=saved_data.get("employer_match", 4.0), 
        key="employer_match"
    )
    
    lump_sum = st.number_input(
        "March 2nd Lump Sum ($)", 
        value=saved_data.get("lump_sum", 10000),
        step=1000,
        key="lump_sum"
    )
    
    rrsp_room = st.number_input(
        "Unused RRSP Room ($)", 
        value=saved_data.get("rrsp_room", 146000), 
        key="rrsp_room"
    )
    
    tfsa_room = st.number_input(
        "Unused TFSA Room ($)", 
        value=saved_data.get("tfsa_room", 102000), 
        key="tfsa_room"
    )

    st.divider()
    
    # PERSISTENCE BUTTONS
    c_save, c_reset = st.columns(2)
    with c_save:
        if st.button("💾 Save Inputs"):
            # Collect current state
            current_state = {
                "t4_gross_other": t4_gross_other,
                "base_salary": base_salary,
                "bonus_pct": bonus_pct,
                "biweekly_pct": biweekly_pct,
                "employer_match": employer_match,
                "lump_sum": lump_sum,
                "rrsp_room": rrsp_room,
                "tfsa_room": tfsa_room
            }
            if save_to_file(current_state):
                st.success("Saved!")
    
    with c_reset:
        if st.button("🔄 Reset"):
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            st.rerun()

# --- 4. CALCULATIONS ---
bonus_amt = base_salary * (bonus_pct / 100)
# Total Gross Logic (Base + Bonus + T4 Other)
total_gross_income = base_salary + bonus_amt + t4_gross_other

annual_rrsp_periodic = base_salary * ((biweekly_pct + employer_match) / 100)
total_rrsp_contributions = annual_rrsp_periodic + lump_sum
taxable_income = total_gross_income - total_rrsp_contributions
tax_cliff = 181440 

# Room Logic
final_rrsp_room = max(0, rrsp_room - total_rrsp_contributions)
est_refund = total_rrsp_contributions * 0.46
final_tfsa_room = max(0, tfsa_room - est_refund)

# --- 5. HEADER & PRINT BUTTON ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.header("📊 Strategy Execution & Room Status")
with col_h2:
    # Javascript Print Trigger
    print_btn = """
    <script>function print_page() { window.print(); }</script>
    <button onclick="print_page()" style="padding: 10px 20px; background-color: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold;">
        🖨️ Print / Save PDF
    </button>
    """
    components.html(print_btn, height=60)

# --- 6. ROOM TRACKER TABLE ---
room_df = pd.DataFrame({
    "Account": ["RRSP Room", "TFSA Room"],
    "Starting Room": [f"${rrsp_room:,.0f}", f"${tfsa_room:,.0f}"],
    "Strategy Usage": [f"-${total_rrsp_contributions:,.0f}", f"-${est_refund:,.0f}"],
    "Post-Strategy Room": [f"${final_rrsp_room:,.0f}", f"${final_tfsa_room:,.0f}"]
})
st.table(room_df)
st.metric("Total RRSP Contribution", f"${total_rrsp_contributions:,.0f}")

# --- 7. TAX BUILDING VISUALIZER ---
st.divider()
st.subheader("🏢 The Tax Building (Progressive Shielding)")
BRACKETS = [
    {"Floor": "Floor 1", "low": 0, "top": 53891, "rate": 0.1905},
    {"Floor": "Floor 2", "low": 53891, "top": 58523, "rate": 0.2315},
    {"Floor": "Floor 3", "low": 58523, "top": 94907, "rate": 0.2965},
    {"Floor": "Floor 4", "low": 94907, "top": 117045, "rate": 0.3148},
    {"Floor": "Floor 5", "low": 117045, "top": 181440, "rate": 0.4497}, 
    {"Floor": "Penthouse", "low": 181440, "top": 258482, "rate": 0.4829}
]

building_data = []
for b in BRACKETS:
    total_in_bracket = min(total_gross_income, b['top']) - b['low']
    if total_in_bracket <= 0: continue
    taxed_amt = max(0, min(b['top'], taxable_income) - b['low'])
    shielded_amt = total_in_bracket - taxed_amt
    
    if shielded_amt > 0:
        building_data.append({"Floor": b['Floor'], "Amount": shielded_amt, "Status": "Shielded", "Rate": f"{b['rate']*100:.1f}%"})
    if taxed_amt > 0:
        building_data.append({"Floor": b['Floor'], "Amount": taxed_amt, "Status": "Taxed", "Rate": f"{b['rate']*100:.1f}%"})

chart = alt.Chart(pd.DataFrame(building_data)).mark_bar().encode(
    x=alt.X('Floor:N', sort=None),
    y=alt.Y('Amount:Q', title="Income ($)"),
    color=alt.Color('Status:N', scale=alt.Scale(domain=['Shielded', 'Taxed'], range=['#3b82f6', '#f59e0b'])),
    tooltip=['Floor', 'Amount', 'Rate', 'Status']
).properties(height=400)
st.altair_chart(chart, use_container_width=True)

# --- 8. ACTION ITEMS & BONUS LOGIC ---
st.divider()
st.header("🛡️ Strategic Action Items")
tax_on_bonus = bonus_amt * 0.4829

st.warning(f"**Bonus Shield:** If you receive your **${bonus_amt:,.0f}** bonus as cash, you lose roughly **${tax_on_bonus:,.0f}** to immediate tax. Execute the direct-to-RRSP transfer to keep the full amount.")

c1, c2 = st.columns(2)
with c1:
    with st.expander("📝 March 2nd Checklist", expanded=True):
        st.write(f"- **March 2 Lump Sum:** Deposit **${lump_sum:,.0f}**.")
        st.write(f"- **T1213 Form:** File using **${total_rrsp_contributions:,.0f}** total deduction.")
with c2:
    st.success(f"**TFSA Pivot:** Inject the estimated refund of **${est_refund:,.0f}** into your TFSA.")

# --- 9. RETIREMENT BRIDGE ---
st.divider()
st.subheader("🌉 The Age 55 Retirement Bridge")
bridge_df = pd.DataFrame({
    "Asset": ["TFSA (The Bridge)", "RRSP (The Foundation)", "CPP/OAS (Gov)"],
    "Role": ["Income Age 55-65", "Income Age 65+", "Supplement Age 65+"],
    "Tax Status": ["Tax-Free", "Taxable", "Taxable"]
})
st.table(bridge_df)
