import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURATION ---
st.set_page_config(page_title="Retirement Architect Pro", layout="wide")
st.title("🏢 Retirement Architect: Path to Age 55")
st.markdown("### Strategy: High-Income Optimization (Official 2026 Estimates)")

# --- SIDEBAR: PROFILE & INPUTS ---
with st.sidebar:
    st.header("👤 Income Profile")
    gross_income = st.number_input("Total Gross (Salary + Bonus) ($)", value=200000, step=5000)
    base_salary = st.number_input("Annual Base Salary ($)", value=180000, step=5000)
    
    st.header("💰 RRSP Contributions")
    biweekly_pct = st.slider("Biweekly Contribution (% of Base)", 0.0, 18.0, 6.0)
    employer_match = st.slider("Employer Match (% of Base)", 0.0, 10.0, 4.0)
    lump_sum = st.number_input("March 2nd Lump Sum ($)", value=10000, step=1000)
    
    st.header("📁 Available Room")
    rrsp_room = st.number_input("Unused RRSP Room ($)", value=146000)
    tfsa_room = st.number_input("Unused TFSA Room ($)", value=102000)

# --- 2026 ONTARIO/FEDERAL TAX DATA ---
# Includes the Federal drop to 14% and indexed Ontario brackets
BRACKETS = [
    {"Floor": "Floor 1", "low": 0, "top": 53891, "rate": 0.1905},
    {"Floor": "Floor 2", "low": 53891, "top": 58523, "rate": 0.2315},
    {"Floor": "Floor 3", "low": 58523, "top": 94907, "rate": 0.2965},
    {"Floor": "Floor 4", "low": 94907, "top": 117045, "rate": 0.3148},
    {"Floor": "Floor 5", "low": 117045, "top": 181440, "rate": 0.4497}, 
    {"Floor": "Penthouse", "low": 181440, "top": 258482, "rate": 0.4829}
]

# --- CALCULATIONS ---
annual_rrsp_periodic = base_salary * ((biweekly_pct + employer_match) / 100)
total_rrsp = annual_rrsp_periodic + lump_sum
taxable_income = gross_income - total_rrsp
tax_cliff = 181440 # The 48% marginal rate threshold

# --- VISUALIZER: SPLIT-BAR TAX BUILDING ---
st.header("🏛️ The Tax Building (Partial Shielding)")
st.write(f"Your RRSP has removed **${total_rrsp:,.0f}** from your highest tax floors.")

building_data = []
for b in BRACKETS:
    total_in_bracket = min(gross_income, b['top']) - b['low']
    if total_in_bracket <= 0: continue
    
    # Split logic: Blue is shielded (removed from top-down)
    taxed_amt = max(0, min(b['top'], taxable_income) - b['low'])
    shielded_amt = total_in_bracket - taxed_amt
    
    if shielded_amt > 0:
        building_data.append({"Floor": b['Floor'], "Amount": shielded_amt, "Status": "Shielded (Saved)", "Rate": f"{b['rate']*100:.1f}%"})
    if taxed_amt > 0:
        building_data.append({"Floor": b['Floor'], "Amount": taxed_amt, "Status": "Taxed (Still Paying)", "Rate": f"{b['rate']*100:.1f}%"})

df_building = pd.DataFrame(building_data)
chart = alt.Chart(df_building).mark_bar().encode(
    x=alt.X('Floor:N', sort=None),
    y=alt.Y('Amount:Q', title="Income ($)"),
    color=alt.Color('Status:N', scale=alt.Scale(domain=['Shielded (Saved)', 'Taxed (Still Paying)'], range=['#3b82f6', '#f59e0b'])),
    tooltip=['Floor', 'Amount', 'Rate', 'Status']
).properties(height=400)
st.altair_chart(chart, use_container_width=True)

# --- FEATURE 1: MARCH 2nd CHECKLIST ---
st.divider()
st.header("📅 Action: March 2nd Tax Deadline")
premium_lump_sum_needed = max(0, (gross_income - annual_rrsp_periodic) - tax_cliff)
actual_recommendation = min(premium_lump_sum_needed, rrsp_room)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Income in 'Penthouse'", f"${max(0, taxable_income - tax_cliff):,.0f}")
    st.caption("Income currently taxed at 48.3%.")
with col2:
    st.metric("Recommended Lump Sum", f"${actual_recommendation:,.0f}")
    st.caption("To clear the 48% tax bracket.")
with col3:
    refund = total_rrsp * 0.44 # Average conservative refund rate
    st.success(f"Est. Total Refund: **${refund:,.0f}**")
    st.caption("Strategy: Direct this into your TFSA.")

# --- FEATURE 2: BONUS SHIELD & T1213 ---
st.divider()
st.subheader("🛡️ Bonus Shield & Cash Flow")
bonus_amt = gross_income - base_salary
tax_on_bonus = bonus_amt * 0.4829

c_a, c_b = st.columns(2)
with c_a:
    st.info(f"**Bonus Shield:** Your ${bonus_amt:,.0f} bonus will lose **${tax_on_bonus:,.0f}** to tax if taken as cash. Tell HR to move it directly to your RRSP.")
with c_b:
    with st.expander("📝 Data for T1213 (Tax Waiver)"):
        st.write("Use these to get your refund on every paycheck instead of once a year:")
        st.write(f"- Annual RRSP Deduction: **${total_rrsp:,.0f}**")
        st.write(f"- Requested Tax Reduction: ~**${total_rrsp * 0.45:,.0f}**")

# --- FEATURE 3: RETIREMENT BRIDGE (AGE 55) ---
st.divider()
st.subheader("🌉 The Age 55 Retirement Bridge")
st.write("To retire early, you need to survive on **TFSA** funds to avoid 'clawbacks' of government benefits later.")

# Simplified Bridge Visual
bridge_data = pd.DataFrame({
    "Asset": ["TFSA (The Bridge)", "RRSP (The Foundation)", "CPP/OAS (Gov)"],
    "Withdrawal Age": ["55 - 65", "65+", "65+"],
    "Tax Status": ["Tax-Free", "Taxable", "Taxable"]
})
st.table(bridge_df := bridge_data)

st.warning(f"**Strategy Note:** You have ${tfsa_room:,.0f} TFSA room. Prioritize filling this *after* your taxable income drops below ${tax_cliff:,.0f}.")
