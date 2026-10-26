import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Behavioral Scorecard Engine", layout="wide")
st.title("💳 Behavioral Credit Scorecard Engine")
st.markdown("This dashboard simulates a **Behavioral Credit Scorecard** for an existing borrower at Month 24. Adjust their behavioral history to see the resulting score and the **Credit Strategy Action**.")
st.info("💡 **Business Context:** Behavioral scores are not used to 'decline' an existing customer. They are used for Limit Management, Early Warning Systems (EWS), Collections Triage, and IFRS 9 Stage 2 (SICR) triggers.")

# Constants
BASE_SCORE = 600
OFFSET = 487.12 
FACTOR = 28.8539
SCORE_CUTOFF = 510

# ==========================================
# SIDEBAR INPUTS
# ==========================================
with st.sidebar:
    st.header("👤 Borrower Behavior (Months 1-24)")
    
    # 1. Delinquency
    max_delinq = st.selectbox(
        "Worst Delinquency Status (24M)", 
        options=[0, 1, 2, 3, 5],
        format_func=lambda x: {0: "0 - Never missed", 1: "1 - 30 DPD", 2: "2 - 60 DPD", 3: "3 - 90+ DPD", 5: "5 - REO/Foreclosure"}[x]
    )
    
    # 2. FICO
    fico = st.slider("Classic FICO Score", 300, 850, 720)
    
    # 3. Balance Reduction
    bal_reduction = st.slider("Balance Reduction % (Principal Paid)", 0.0, 0.20, 0.05, format="%.2f")
    
    # 4. DTI
    dti = st.slider("Original DTI (%)", 1, 60, 35)
    
    # 5. LTV
    ltv = st.slider("Original LTV (%)", 10, 120, 80)

# ==========================================
# SCORECARD LOGIC (Points Calculation)
# ==========================================
score = 0
# [Insert the same points calculation logic here as before]
delinq_points = {0: 151.6, 1: 87.3, 2: 43.3, 3: 25.4, 5: 5.0}
score += delinq_points[max_delinq]

if fico <= 695: score += 101.4
elif fico <= 734: score += 112.1
elif fico <= 765: score += 118.4
elif fico <= 789: score += 126.1
else: score += 131.9

if bal_reduction <= 0.0238: score += 96.8
elif bal_reduction <= 0.0296: score += 113.4
elif bal_reduction <= 0.0405: score += 125.4
elif bal_reduction <= 0.08: score += 120.6
else: score += 125.6

if dti <= 26: score += 123.8
elif dti <= 34: score += 117.5
elif dti <= 39: score += 113.6
elif dti <= 45: score += 110.9
else: score += 103.6

if ltv <= 59: score += 119.4
elif ltv <= 73: score += 112.0
elif ltv <= 80: score += 111.1
elif ltv <= 89: score += 110.4
else: score += 111.2

# Calculate Probability of Default
logit = (OFFSET - score) / FACTOR
pd = 1 / (1 + np.exp(-logit))

# ==========================================
# MAIN DASHBOARD UI
# ==========================================
st.subheader("📊 Scoring Results")

col1, col2, col3 = st.columns(3)
col1.metric("Behavioral Credit Score", f"{score:.0f}")
col2.metric("Estimated Probability of Default", f"{pd:.2%}")
col3.metric("Stage 2 (SICR) Threshold", f"< {SCORE_CUTOFF}")

# Strategy Action Box
if score >= 600:
    st.success(f"✅ **ACTION: PRE-APPROVED OFFERS / LIMIT INCREASE**\n\nThe borrower scored **{score:.0f}**. They are a premium, low-risk customer. The bank should proactively offer credit limit increases or cross-sell products.")
elif score >= SCORE_CUTOFF:
    st.warning(f"⚠️ **ACTION: MONITOR / NO LIMIT CHANGES**\n\nThe borrower scored **{score:.0f}**. They are performing adequately but do not qualify for limit increases. Maintain current facility and monitor.")
else:
    st.error(f"🚨 **ACTION: EARLY WARNING / REDUCE LIMITS / COLLECTIONS**\n\nThe borrower scored **{score:.0f}**, which is below the SICR threshold of 510. Their risk has increased significantly. **Actions:** Trigger IFRS 9 Stage 2 (SICR), reduce credit limits, and route to the collections team for proactive outreach.")

st.divider()

# ==========================================
# VISUALIZATION: Score Distribution
# ==========================================
st.subheader("📈 Where does this borrower fall in the population?")
st.markdown("The chart below shows the distribution of scores for Good (Green) and Bad (Red) borrowers. The black line is the Stage 2 SICR threshold.")

np.random.seed(42)
good_scores = np.random.normal(loc=610, scale=25, size=5000)
bad_scores = np.random.normal(loc=480, scale=40, size=1000)

fig, ax = plt.subplots(figsize=(10, 4))
sns.kdeplot(good_scores, color='green', fill=True, label='Good (Paid)', ax=ax)
sns.kdeplot(bad_scores, color='red', fill=True, label='Bad (Defaulted)', ax=ax)
ax.axvline(SCORE_CUTOFF, color='black', linestyle='--', label=f'SICR Cutoff ({SCORE_CUTOFF})')
ax.axvline(score, color='blue', linewidth=3, linestyle='-', label=f'This Borrower ({score:.0f})')

ax.set_xlabel("Credit Score")
ax.set_ylabel("Density")
ax.set_title("Score Distribution (Out-of-Time)")
ax.legend()
st.pyplot(fig)