import streamlit as st
from pulp import LpMaximize, LpProblem, LpVariable

# Function to solve the optimization problem
def optimize_ads(budget, min_viewers, direct_roi, indirect_roi, direct_viewers, indirect_viewers):
    # Define the problem
    problem = LpProblem("Maximize_Profit_and_Leads", LpMaximize)

    # Define decision variables
    x = LpVariable("Direct_Advertising", lowBound=0)  # Amount spent on direct ads
    y = LpVariable("Indirect_Advertising", lowBound=0)  # Amount spent on indirect ads

    # Objective function: Maximize profit
    problem += direct_roi * x + indirect_roi * y, "Total_Profit"

    # Constraints
    problem += x + y <= budget, "Budget_Constraint"  # Total budget
    problem += x >= 0.4 * (x + y), "Direct_Minimum"  # Direct ads at least 40%
    problem += y <= 0.5 * budget, "Indirect_Cap"    # Indirect ads max 50% of budget
    problem += (direct_viewers * x / 1000) + (indirect_viewers * y / 1000) >= min_viewers, "Viewer_Constraint"

    # Solve the problem
    problem.solve()

    # Extract results
    status = problem.status
    optimal_profit = problem.objective.value()
    direct_spend = x.value()
    indirect_spend = y.value()
    total_viewers = (direct_viewers * direct_spend / 1000) + (indirect_viewers * indirect_spend / 1000)

    return status, optimal_profit, direct_spend, indirect_spend, total_viewers

# Streamlit app
st.title("Marketing Optimization Tool")

st.sidebar.header("Input Parameters")
# Input parameters
budget = st.sidebar.number_input("Total Budget ($)", min_value=1000, value=100000, step=1000)
min_viewers = st.sidebar.number_input("Minimum Viewers", min_value=100000, value=700000, step=50000)
direct_roi = st.sidebar.number_input("Direct ROI ($ per $ spent)", min_value=1.0, value=5.0, step=0.1)
indirect_roi = st.sidebar.number_input("Indirect ROI ($ per $ spent)", min_value=1.0, value=3.0, step=0.1)
direct_viewers = st.sidebar.number_input("Direct Viewers per $1000", min_value=1000, value=8000, step=500)
indirect_viewers = st.sidebar.number_input("Indirect Viewers per $1000", min_value=1000, value=5000, step=500)

# Solve the problem
if st.button("Optimize"):
    status, optimal_profit, direct_spend, indirect_spend, total_viewers = optimize_ads(
        budget, min_viewers, direct_roi, indirect_roi, direct_viewers, indirect_viewers
    )

    if status == 1:  # Optimal solution found
        st.success("Optimization Successful!")
        st.write(f"**Optimal Profit**: ${optimal_profit:,.2f}")
        st.write(f"**Direct Advertising Spend**: ${direct_spend:,.2f}")
        st.write(f"**Indirect Advertising Spend**: ${indirect_spend:,.2f}")
        st.write(f"**Estimated Viewers Generated**: {total_viewers:,.0f}")
    else:
        st.error("Optimization Failed! Please check your constraints.")