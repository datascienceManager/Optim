import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, value
from datetime import datetime
from fpdf import FPDF
from sklearn.linear_model import LinearRegression



def optimize_ott(budget, selected_channels):
    """
    Optimize OTT advertising budget allocation across different channels
    
    Parameters:
    budget (float): Total available budget
    selected_channels (list): List of marketing channels
    
    Returns:
    tuple: (success, allocation, total_subscribers)
    """
    # Create the optimization problem
    problem = LpProblem("OTT_Advertising_Optimization", LpMaximize)
    
    # Create variables for each channel
    x = {channel: LpVariable(f"Budget_{channel}", lowBound=0, upBound=budget) for channel in selected_channels}
    
    # Define conversion rates for each channel (subscribers per $1000 spent)
    conversion_rates = {
        "Social Media Ads": 45,
        "Search Engine Marketing": 50,
        "Email Campaigns": 35,
        "Influencer Partnerships": 40,
        "Affiliate Marketing": 30,
        "PR Coverage": 25
    }
    
    # Calculate total subscribers (objective function)
    total_subscribers = sum(conversion_rates[channel] * x[channel] / 1000 for channel in selected_channels)
    
    # Set objective
    problem += total_subscribers, "Total_Subscribers"
    
    # Add constraints
    problem += sum(x.values()) <= budget, "Budget_Constraint"  # Total budget constraint
    
    # Add minimum allocation constraints (at least 5% of budget for each channel)
    min_allocation = budget * 0.05
    for channel in selected_channels:
        problem += x[channel] >= min_allocation, f"Minimum_{channel}"
    
    # Solve the problem
    problem.solve()
    
    # Check if solution was found
    if problem.status == 1:  # Optimal solution found
        allocation = {channel: value(x[channel]) for channel in selected_channels}
        total_subs = value(problem.objective)
        return True, allocation, total_subs
    else:
        return False, None, None


def generate_pdf(allocation, total_subscribers, budget, timestamp):
    """
    Generate PDF report with optimization results
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.cell(200, 10, txt="OTT Advertising Optimization Report", ln=True, align="C")
    pdf.ln(10)
    
    # Add timestamp
    pdf.cell(200, 10, txt=f"Report Generated: {timestamp}", ln=True, align="C")
    pdf.ln(10)
    
    # Add budget
    pdf.cell(200, 10, txt=f"Total Budget: QR {budget:,.2f}", ln=True)
    
    # Add channel allocations
    for channel, spend in allocation.items():
        pdf.cell(200, 10, txt=f"{channel}: QR {spend:,.2f}", ln=True)
    
    # Add total subscribers with error handling
    if total_subscribers is not None:
        try:
            subscriber_text = f"Total Subscribers Gained: {int(total_subscribers):,}"
        except (ValueError, TypeError):
            subscriber_text = f"Total Subscribers Gained: {total_subscribers}"
    else:
        subscriber_text = "Total Subscribers Gained: Not Available"
    
    pdf.cell(200, 10, txt=subscriber_text, ln=True)
    
    return pdf.output(dest="S").encode("latin1")


# Streamlit app
def main():

    # Streamlit interface
    st.title("OTT Advertising Optimization with Predictions")

# Sidebar for budget input
    st.sidebar.header("Budget Configuration")

# Total budget input
total_budget = st.sidebar.number_input(
    "Total Budget (QR)",
    min_value=10000,
    max_value=1000000,
    value=100000,
    step=10000
)

# Define channels
channels = [
    "Social Media Ads",
    "Search Engine Marketing",
    "Email Campaigns",
    "Influencer Partnerships",
    "Affiliate Marketing",
    "PR Coverage"
]

# Run optimization
success, allocation, total_subscribers = optimize_ott(total_budget, channels)

# Display results
if success:
    st.success("✅ Optimization Successful!")
    
    # Create two columns for displaying results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Allocation")
        for channel, spend in allocation.items():
            st.write(f"**{channel}:** QR{spend:,.2f}")
    
    with col2:
        st.subheader("Summary")
        st.write(f"**Total Budget:** QR {total_budget:,.2f}")
        st.write(f"**Estimated Subscribers:** {int(total_subscribers):,}")
        roi = total_subscribers / total_budget * 1000
        st.write(f"**ROI (Subscribers per QR 1000):** {roi:.2f}")
    
    # Create visualization
    st.subheader("Budget Allocation Visualization")
    allocation_data = pd.DataFrame({
        "Channel": list(allocation.keys()),
        "Budget": list(allocation.values())
    })
    
    # Create a bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(allocation_data["Channel"], allocation_data["Budget"])
    ax.set_xlabel("Marketing Channel")
    ax.set_ylabel("Budget Allocation (QR )")
    ax.set_title("Budget Allocation Across Channels")
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f' QR {height:,.0f}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    st.pyplot(fig)
    
else:
    st.error("❌ Optimization Failed! Please adjust your budget.")
    
if __name__ == "__main__":
    main()