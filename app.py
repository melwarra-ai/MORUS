import streamlit as st
import pandas as pd
import altair as alt
import json
import os

# --- PERSISTENCE ENGINE (JSON) ---
SAVE_FILE = "retirement_data.json"

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

# Load existing data at startup
saved_state = load_data()

# --- CONFIGURATION ---
st.set_page_config(page_title="Retirement Architect Pro", layout="wide")
st.title("🏛️ Retirement Architect: Master Strategy Pro")

# --- SIDEBAR: ALL INPUTS ---
with st.sidebar:
    st.header("👤 Income Profile")
    
    # 1. T4 Gross Income (Requirement: No extra text)
    t4_gross_other = st.number_input(
        "T4 Gross Income", 
        value=saved_state.get("t4_gross_other", 0), 
        help="This is the T4 gross reported in T4 document",
        key="t4_gross_other"
    )
    
    base_salary = st.number_input(
        "Annual Base Salary ($)", 
        value=saved_state.get("base_salary", 180000), 
        step=5000, 
        key="base_salary"
    )
    
    bonus_pct = st.slider(
        "Target Bonus (%)", 
        0, 50, 
        value=saved_state.get("bonus_pct", 15), 
        key="bonus_pct"
    )
    
    st.header("💰 RRSP & TFSA")
    biweekly_pct = st.slider(
        "Biweekly Contribution (%)", 
        0.0, 18.0, 
        value=saved_state.get("biweekly_pct", 6.0), 
        key="biweekly_pct"
    )
    
    employer_match = st.slider(
        "Employer Match (%)", 
        0.0, 10.0, 
        value=saved_state.get("employer_match", 4.0), 
        key="employer_match"
    )
    
    rrsp_room = st.number_input(
        "Unused RRSP Room ($)", 
        value=saved_state.get("rrsp_room", 146000), 
        key="rrsp_room"
    )
    
    tfsa_room = st.number_input(
        "Unused TFSA Room ($)", 
        value=saved_state.get("tfsa_room", 102000), 
        key="tfsa_room"
    )

    # Save logic triggered by button or change
    current_inputs = {
        "t4_gross_other": t4_gross_other,
        "base_salary": base_salary,
        "bonus_pct": bonus_pct,
        "biweekly_pct": biweekly_pct,
        "employer_match": employer_match,
        "rrsp_room": rrsp_room,
        "tfsa_room": tfsa_room
    }
    if st.button("💾 Save My Data Permanently"):
        save_data(current_inputs)
        st.success("Data saved to local storage!")

# --- CALCULATIONS ---
bonus_amt = base_salary * (bonus_pct / 100)
# Note: Total Gross calc still runs for the chart, but title is removed per request
gross_income = base_salary + bonus_amt + t4_gross_other

annual_rrsp_periodic = base_salary * ((biweekly_pct + employer_match) / 100)
taxable_income = gross_income - annual_rrsp_periodic
tax_cliff = 181440 

# --- TAX BRACKETS ---
BRACKETS = [
    {"Floor": "Floor 1", "low": 0, "top": 53891, "rate": 0.1905},
    {"Floor": "Floor 2", "low": 53891, "top": 58523, "rate": 0.2315},
    {"Floor": "Floor 3", "low": 58523, "top": 94907, "rate": 0.2965},
    {"Floor": "Floor 4", "low": 94907, "top": 117045, "rate": 0.3148},
    {"Floor": "Floor 5", "low": 117045, "top": 181440, "rate": 0.4497}, 
    {"Floor": "Penthouse", "low": 181440, "top": 258482, "rate": 0.4829}
]

# --- VISUALIZER ---
st.header("🏢 The Tax Building Visualizer")
building_data = []
for b in BRACKETS:
    total_in_bracket = min(gross_income, b['top']) - b['low']
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

# --- ACTION ITEMS ---
st.divider()
st.header("📅 Tax Season Action: March 2nd")
premium_lump_sum = max(0, taxable_income - tax_cliff)
actual_lump = min(premium_lump_sum, rrsp_room)
tax_refund = (annual_rrsp_periodic + actual_lump) * 0.46 

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Income in 'Penthouse'", f"${premium_lump_sum:,.0f}")
with c2:
    st.metric("Lump Sum Target", f"${actual_lump:,.0f}")
with c3:
    st.success(f"Est. Strategy Refund: ${tax_refund:,.0f}")

st.divider()
tax_on_bonus = bonus_amt * 0.4829
st.info(f"**Bonus Shield:** Your ${bonus_amt:,.0f} bonus will lose **${tax_on_bonus:,.0f}** to tax if taken as cash.")
