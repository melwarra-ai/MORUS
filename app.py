import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(page_title="Retirement Architect Pro", layout="wide")
st.title("🇨🇦 Retirement Optimization Simulator")
st.markdown("### Strategy: Early Retirement (Age 55) | High-Income Laddering")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("1. Financial Profile")
    age = st.number_input("Current Age", value=42)
    retire_age = st.number_input("Target Retirement Age", value=55)
    income = st.number_input("Gross Annual Income ($)", value=200000)
    
    st.header("2. Existing Assets")
    current_rrsp_balance = st.number_input("Current RRSP Balance ($)", value=150000)
    rrsp_room = st.number_input("Available RRSP Room ($)", value=146000)
    tfsa_room = st.number_input("Available TFSA Room ($)", value=102000)
    
    st.header("3. New Capital")
    cash = st.number_input("Available Cash to Invest Now ($)", value=100000)
    
    st.header("4. Market Assumptions")
    cagr = st.slider("Expected Annual Growth (CAGR %)", 0.0, 100.0, 7.0) / 100
    inflation = st.slider("Expected Inflation (%)", 0.0, 10.0, 2.2) / 100

# --- FINANCIAL ENGINE ---
def get_marginal_rate(inc):
    if inc > 246752: return 0.5353
    if inc > 173205: return 0.4548
    if inc > 111733: return 0.4341
    return 0.3148

current_rate = get_marginal_rate(income)
years_to_retire = retire_age - age

# Optimization: Maximize Year 1 RRSP to a strategic bracket floor ($173,205)
optimal_rrsp_lump = min(rrsp_room, max(0, income - 173205), cash)
refund = optimal_rrsp_lump * current_rate
tfsa_contribution = min(tfsa_room, cash - optimal_rrsp_lump + refund)

# --- PROJECTION SIMULATION ---
data = []
current_rrsp_total = current_rrsp_balance + optimal_rrsp_lump
current_tfsa_total = tfsa_contribution

for y in range(years_to_retire + 1):
    # Estimating a 25% tax rate for the retirement window
    after_tax_rrsp = current_rrsp_total * (1 - 0.25) 
    total_wealth = after_tax_rrsp + current_tfsa_total
    
    # Adjusted for inflation (Purchasing Power)
    purchasing_power = total_wealth / ((1 + inflation) ** y)
    
    data.append({
        "Year": 2025 + y,
        "Age": age + y,
        "RRSP (Pre-Tax)": current_rrsp_total,
        "TFSA (Tax-Free)": current_tfsa_total,
        "Total After-Tax Wealth": total_wealth,
        "Purchasing Power (Today's $)": purchasing_power
    })
    current_rrsp_total *= (1 + cagr)
    current_tfsa_total *= (1 + cagr)

df = pd.DataFrame(data)
final_rrsp = df.iloc[-1]['RRSP (Pre-Tax)']
final_tfsa = df.iloc[-1]['TFSA (Tax-Free)']
final_wealth = df.iloc[-1]['Total After-Tax Wealth']

# --- TOP METRICS ---
c1, c2, c3 = st.columns(3)
c1.metric("Year 1 RRSP Top-up", f"${optimal_rrsp_lump:,.0f}")
c2.metric("Estimated Tax Refund", f"${refund:,.0f}")
c3.metric("Year 1 TFSA Deposit", f"${tfsa_contribution:,.0f}")

st.divider()

# --- SECTION 1: GROWTH TRAJECTORY LOGIC ---
st.header("📈 The Growth Trajectory Engine")
st.markdown("""
The simulation uses a **Bi-Directional Growth Logic**. Your wealth does not just grow through contributions; 
it grows through the interplay of compounding and tax arbitrage.
""")

col_logic1, col_logic2 = st.columns(2)
with col_logic1:
    st.subheader("1. Compounding Mechanics")
    st.write(f"- **Starting Principal:** We combined your current ${current_rrsp_balance:,.0f} balance with new capital.")
    st.write(f"- **Growth Rate:** Applied an annual yield of **{cagr*100:.1f}%**.")
    st.write(f"- **Time Horizon:** Your money has **{years_to_retire} years** to double and re-double.")

with col_logic2:
    st.subheader("2. Tax Alpha")
    st.write("- **Immediate Return:** By deducting RRSP room at the 45% bracket, you 'earn' 45% before the market even moves.")
    st.write("- **Tax-Free Shielding:** The TFSA component grows with zero 'tax drag,' meaning 100% of the growth stays in your pocket.")

st.area_chart(df.set_index("Age")[["RRSP (Pre-Tax)", "TFSA (Tax-Free)"]])

st.divider()

# --- SECTION 2: WITHDRAWAL STRATEGY (NOW AT BOTTOM) ---
st.header(f"💰 Retirement Withdrawal Strategy (Age {retire_age})")
st.markdown("""
This section outlines how to transition from **Accumulation** (saving) to **Decumulation** (spending).
The goal is a 'Meltdown' strategy: emptying taxable accounts first while staying in low tax brackets.
""")

swr_pct = st.select_slider("Safe Withdrawal Rate (%)", options=[3.0, 3.5, 4.0, 4.5, 5.0], value=3.5)

total_annual_target = final_wealth * (swr_pct / 100)
monthly_income = total_annual_target / 12

# Withdrawal Split Logic
annual_rrsp_draw = min(final_rrsp / 20, 55000) 
annual_tfsa_draw = max(0, total_annual_target - (annual_rrsp_draw * 0.75)) # 0.75 accounts for tax on RRSP

wa, wb, wc = st.columns(3)
wa.metric("Total Monthly Paycheck", f"${monthly_income:,.0f}")
wb.metric("From RRSP (Taxable)", f"${(annual_rrsp_draw/12):,.0f}")
wc.metric("From TFSA (Tax-Free)", f"${(annual_tfsa_draw/12):,.0f}")

with st.expander("📝 Strategy Description & Methodology"):
    st.write("**Account Meltdown Logic:**")
    st.write("- **RRSP First:** We prioritize withdrawing up to ~$55,000 annually from your RRSP. This ensures you utilize the lowest federal/provincial tax brackets effectively.")
    st.write("- **TFSA Bridging:** The TFSA is used to 'top up' your income. Because TFSA withdrawals are not considered taxable income, they do not push you into a higher tax bracket.")
    st.write("- **OAS/CPP Protection:** By reducing your RRSP balance early, you minimize the risk of 'Old Age Security Clawbacks' that can happen at age 65 if your income is too high.")
