

# How It Works
# Sidebar Inputs:
# Users can dynamically adjust the following:
# Budget: The total budget for advertising.
# Minimum Indirect Spend: Minimum spend required for indirect advertising.
# Direct Advertising Cap: The maximum percentage of the total budget that can go to direct advertising.
# Diminishing Returns Factors: Adjust 
# a
# a and 
# b
# b for direct and indirect advertising.
# Optimization Function:
# The optimize_ott function implements the optimization using PuLP.
# The objective and constraints are dynamically applied based on user inputs.
# Results Display:
# Optimal spending on direct and indirect advertising.
# Total subscribers gained.
# If the optimization fails (e.g., due to conflicting constraints), an error message is displayed.






import streamlit as st
from pulp import LpMaximize, LpProblem, LpVariable, value

# Function to solve the optimization problem
def optimize_ott(budget, min_indirect, direct_cap, a, b):
    # Define the problem
    problem = LpProblem("OTT_Advertising_Optimization", LpMaximize)

    # Decision variables
    x = LpVariable("Direct_Advertising", lowBound=0)  # Amount spent on direct ads
    y = LpVariable("Indirect_Advertising", lowBound=0)  # Amount spent on indirect ads

    # Objective function
    direct_subscribers = (
        50 * x / 1000 if x <= 100000 else 50 * 100 + a * (x - 100000) ** 0.5
    )
    indirect_subscribers = (
        30 * y / 1000 if y <= 75000 else 30 * 75 + b * (y - 75000) ** 0.6
    )

    problem += direct_subscribers + indirect_subscribers, "Total_Subscribers"

    # Constraints
    problem += x + y + 10000 + 7500 <= budget, "Budget_Constraint"
    problem += y >= min_indirect, "Indirect_Minimum"
    problem += x <= direct_cap * (x + y), "Direct_Channel_Limit"

    # Solve the problem
    problem.solve()

    # Extract results
    if problem.status == 1:  # Solution found
        direct_spend = value(x)
        indirect_spend = value(y)
        total_subscribers = value(problem.objective)
        return True, direct_spend, indirect_spend, total_subscribers
    else:
        return False, None, None, None

# Streamlit app
st.title("OTT Advertising Optimization Tool")

# Sidebar inputs
st.sidebar.header("Input Parameters")
budget = st.sidebar.number_input("Total Budget ($)", min_value=50000, value=200000, step=1000)
min_indirect = st.sidebar.number_input("Minimum Indirect Spend ($)", min_value=10000, value=50000, step=5000)
direct_cap = st.sidebar.slider("Direct Advertising Cap (% of total spend)", min_value=0.1, max_value=1.0, value=0.6, step=0.1)
a = st.sidebar.number_input("Direct Diminishing Returns Factor (a)", min_value=0.01, value=0.02, step=0.005)
b = st.sidebar.number_input("Indirect Diminishing Returns Factor (b)", min_value=0.01, value=0.015, step=0.005)

# Run optimization
if st.button("Optimize"):
    success, direct_spend, indirect_spend, total_subscribers = optimize_ott(
        budget, min_indirect, direct_cap, a, b
    )

    if success:
        st.success("Optimization Successful!")
        st.write(f"**Optimal spending on direct advertising**: ${direct_spend:,.2f}")
        st.write(f"**Optimal spending on indirect advertising**: ${indirect_spend:,.2f}")
        st.write(f"**Total subscribers gained**: {total_subscribers:,.0f}")
    else:
        st.error("Optimization Failed! Please adjust your inputs.")

# Additional notes
st.write("This tool helps optimize advertising spending for an OTT platform based on direct and indirect marketing constraints.")
st.write("Adjust the inputs on the left panel and click 'Optimize' to see the results.")
