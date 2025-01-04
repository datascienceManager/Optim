import pulp
import streamlit as st

# Define the channels, cost per channel, and expected return per channel
channels = ["Social Media Ads", "Search Engine Marketing", "Email Campaigns", 
            "Influencer Partnerships", "Affiliate Marketing", "PR Coverage"]
cost_per_channel = [1000, 1500, 500, 3000, 2000, 1000]  # Example costs for each channel
expected_return = [10, 15, 8, 20, 12, 10]  # Example returns for each channel (number of new subscribers)

# Streamlit UI
st.title("Marketing Budget Optimization for OTT Platform")
total_budget = st.number_input("Enter your total marketing budget:", min_value=0, value=10000)

# Define optimization model
model = pulp.LpProblem("Maximize_Marketing_Return", pulp.LpMaximize)

# Decision variables: how much to spend on each channel
x = pulp.LpVariable.dicts("Budget_Allocation", channels, lowBound=0, cat='Continuous')

# Objective function: maximize the return (expected return per unit * budget allocated)
model += pulp.lpSum([expected_return[i] * x[channels[i]] for i in range(len(channels))])

# Budget constraint: total budget cannot exceed the provided value
model += pulp.lpSum([cost_per_channel[i] * x[channels[i]] for i in range(len(channels))]) <= total_budget

# Solve the model
if st.button("Optimize Marketing Budget"):
    model.solve()
    
    # Display the results
    if model.status == 1:
        st.write(f"Optimal budget allocation (Maximized Return):")
        for i in range(len(channels)):
            st.write(f"{channels[i]}: ${x[channels[i]].varValue:,.2f}")
        
        # Total expected return
        total_return = pulp.value(model.objective)
        st.write(f"Total Expected Return: {total_return:.2f} subscribers")
    else:
        st.write("No optimal solution found. Please check your inputs.")
