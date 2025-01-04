import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value
from datetime import datetime
from fpdf import FPDF

# Linearize or approximate the nonlinear terms
def approximate_subscribers(var, factor1, factor2):
    """Approximates a subscriber gain function for optimization."""
    # Replace `x[channel]**0.5` with a scaled linear approximation
    return factor1 * var + factor2 * var

# Optimization function
def optimize_ott(channel_budgets, min_indirect, direct_cap, a, b, direct_channels, indirect_channels):
    # Define the problem
    problem = LpProblem("OTT_Advertising_Optimization", LpMaximize)

    # Decision variables for each channel
    channels = list(channel_budgets.keys())
    x = {channel: LpVariable(f"Budget_{channel}", lowBound=0) for channel in channels}

    # Objective function: Subscribers from direct and indirect channels
    direct_subscribers = lpSum(
        [approximate_subscribers(x[channel], 50 / 1000, a) for channel in direct_channels]
    )
    indirect_subscribers = lpSum(
        [approximate_subscribers(x[channel], 30 / 1000, b) for channel in indirect_channels]
    )
    problem += direct_subscribers + indirect_subscribers, "Total_Subscribers"

    # Constraints
    problem += lpSum([x[channel] for channel in channels]) <= sum(channel_budgets.values()), "Budget_Constraint"
    problem += lpSum([x[channel] for channel in indirect_channels]) >= min_indirect, "Indirect_Minimum"
    problem += lpSum([x[channel] for channel in direct_channels]) <= direct_cap * sum(channel_budgets.values()), "Direct_Channel_Limit"

    # Solve the problem
    problem.solve()

    # Extract results
    if problem.status == 1:  # Solution found
        allocation = {channel: value(x[channel]) for channel in channels}
        total_subscribers = value(problem.objective)
        return True, allocation, total_subscribers
    else:
        return False, None, None

# Streamlit app
st.title("OTT Advertising Optimization")

# Define direct and indirect channels
direct_channels = ["Social Media Ads", "Search Engine Marketing", "Email Campaigns"]
indirect_channels = ["Influencer Partnerships", "Affiliate Marketing", "PR Coverage"]

st.sidebar.header("Input Channel Budgets")
channel_budgets = {}

# Input boxes for direct channels
st.sidebar.subheader("Direct Channels")
for channel in direct_channels:
    channel_budgets[channel] = st.sidebar.number_input(
        f"Budget for {channel} ($)", min_value=0.0, value=20000.0, step=5000.0
    )

# Input boxes for indirect channels
st.sidebar.subheader("Indirect Channels")
for channel in indirect_channels:
    channel_budgets[channel] = st.sidebar.number_input(
        f"Budget for {channel} ($)", min_value=0.0, value=20000.0, step=5000.0
    )

# Optimization parameters
st.sidebar.header("Optimization Parameters")
min_indirect = st.sidebar.slider("Minimum Indirect Spend ($)", min_value=0.0, max_value=200000.0, value=50000.0, step=5000.0)
direct_cap = st.sidebar.slider("Direct Advertising Cap (% of total spend)", min_value=0.1, max_value=1.0, value=0.6, step=0.1)
a = st.sidebar.slider("Direct Diminishing Returns Factor (a)", min_value=0.01, max_value=0.05, value=0.02, step=0.005)
b = st.sidebar.slider("Indirect Diminishing Returns Factor (b)", min_value=0.01, max_value=0.05, value=0.015, step=0.005)

# Run optimization when inputs change
success, allocation, total_subscribers = optimize_ott(
    channel_budgets, min_indirect, direct_cap, a, b, direct_channels, indirect_channels
)

if success:
    st.success("Optimization Successful!")

    # Display results
    st.write("### Optimal Allocation")
    for channel, spend in allocation.items():
        st.write(f"{channel}: ${spend:,.2f}")
    
    st.write(f"**Total Subscribers Gained**: {total_subscribers:,.0f}")

    # Visualization
    allocation_data = pd.DataFrame({
        "Channel": list(allocation.keys()),
        "Spending": list(allocation.values())
    })
    st.bar_chart(allocation_data.set_index("Channel"))
else:
    st.error("Optimization Failed! Please adjust your inputs.")
