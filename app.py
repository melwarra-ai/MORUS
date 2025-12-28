import streamlit as st
import pandas as pd
import altair as alt

# --- APP CONFIG ---
st.set_page_config(page_title="Retirement Architect Pro", layout="wide")
st.title("🏛️ Retirement Architect: Partial Shielding Visualizer")

# --- SIDEBAR: USER PROFILE ---
with st.sidebar:
    st.header("👤 Income & Goals")
    gross_income = st.number_input("Total Gross (Salary + Bonus) ($)", value=200000, step=5000)
    base_salary = st.number_input("Annual Base Salary ($)", value=180000, step=5000)
    
    st.header("💰 RRSP Contributions")
    biweekly_pct = st.slider("Biweekly Contribution (% of Base)", 0.0, 18.0, 6.0)
    employer_match = st.slider("Employer Match (% of Base)", 0.0, 10.0, 4.0)
    lump_sum = st.number_input("March 2nd Lump Sum ($)", value=5000, step=1000)

# --- 2026 COMBINED ON/FED TAX BRACKETS ---
BRACKETS = [
    {"Floor": "Floor 1", "low": 0, "top": 53891, "rate": 0.1905},
    {"Floor": "Floor 2", "low": 53891, "top": 58523, "rate": 0.2315},
    {"Floor": "Floor 3", "low": 58523, "top": 94907, "rate": 0.2965},
    {"Floor": "Floor 4", "low": 94907, "top": 117045, "rate": 0.3148},
    {"Floor": "Floor 5", "low": 117045, "top": 181440, "rate": 0.4497}, 
    {"Floor": "Penthouse", "low": 181440, "top": 258482, "rate": 0.4829}
]

# --- CALCULATIONS ---
total_rrsp = (base_salary * ((biweekly_pct + employer_match) / 100)) + lump_sum
taxable_income = gross_income - total_rrsp

# --- LOGIC FOR SPLIT BARS ---
chart_data = []
for b in BRACKETS:
    # 1. Total amount of income that falls into this bracket
    total_in_bracket = min(gross_income, b['top']) - b['low']
    if total_in_bracket <= 0: continue
    
    # 2. How much of THIS bracket is still taxable?
    # Anything above our 'taxable_income' is shielded
    taxed_amt = max(0, min(b['top'], taxable_income) - b['low'])
    shielded_amt = total_in_bracket - taxed_amt
    
    # Add Shielded portion
    if shielded_amt > 0:
        chart_data.append({"Floor": b['Floor'], "Amount": shielded_amt, "Status": "Shielded (Saved)", "Rate": f"{b['rate']*100:.1f}%"})
    # Add Taxed portion
    if taxed_amt > 0:
        chart_data.append({"Floor": b['Floor'], "Amount": taxed_amt, "Status": "Taxed (Still Paying)", "Rate": f"{b['rate']*100:.1f}%"})

df_building = pd.DataFrame(chart_data)

# --- VISUALIZER ---
st.header("🏢 The Tax Building (Partial Shielding)")
st.write(f"Your RRSP has removed **${total_rrsp:,.0f}** from your top tax brackets.")

chart = alt.Chart(df_building).mark_bar().encode(
    x=alt.X('Floor:N', sort=None, title="Tax Brackets"),
    y=alt.Y('Amount:Q', title="Income Dollars ($)"),
    color=alt.Color('Status:N', 
        scale=alt.Scale(domain=['Shielded (Saved)', 'Taxed (Still Paying)'], 
                        range=['#3b82f6', '#f59e0b']),
        title="Status"),
    tooltip=['Floor', 'Amount', 'Rate', 'Status']
).properties(height=450)

st.altair_chart(chart, use_container_width=True)

# --- IMPACT SUMMARY ---
st.divider()
st.subheader("📊 Your Shielding Impact")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total RRSP Shield", f"${total_rrsp:,.0f}")
    st.caption("Income removed from your top tax brackets.")
with col2:
    potential_savings = total_rrsp * 0.4829 # Simple estimate for highest bracket
    st.metric("Estimated Tax Savings", f"${potential_savings:,.0f}")
    st.caption("Approximate refund/savings at your marginal rate.")
