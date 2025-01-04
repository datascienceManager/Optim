import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, value
from fpdf import FPDF
import io
from datetime import datetime

def optimize_ott(budget, selected_channels, conversion_rates):
    """
    Optimize OTT advertising budget allocation across different channels
    
    Parameters:
    budget (float): Total available budget
    selected_channels (list): List of marketing channels
    conversion_rates (dict): Dictionary of conversion rates for each channel
    
    Returns:
    tuple: (success, allocation, total_subscribers)
    """
    # Create the optimization problem
    problem = LpProblem("OTT_Advertising_Optimization", LpMaximize)
    
    # Create variables for each channel
    x = {channel: LpVariable(f"Budget_{channel}", lowBound=0, upBound=budget) for channel in selected_channels}
    
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

# Streamlit interface
st.title("OTT Advertising Optimization with Predictions")

# Sidebar for inputs
st.sidebar.header("Budget Configuration")

# Total budget input
total_budget = st.sidebar.number_input(
    "Total Budget ($)",
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

# Conversion rates input section
st.sidebar.header("Channel Conversion Rates")
st.sidebar.markdown("Enter subscribers gained per $1000 spent")

conversion_rates = {}
for channel in channels:
    # Set default values for each channel
    default_value = {
        "Social Media Ads": 45,
        "Search Engine Marketing": 50,
        "Email Campaigns": 35,
        "Influencer Partnerships": 40,
        "Affiliate Marketing": 30,
        "PR Coverage": 25
    }.get(channel, 30)
    
    conversion_rates[channel] = st.sidebar.number_input(
        f"{channel} Conversion Rate",
        min_value=1,
        max_value=100,
        value=default_value,
        help=f"Number of subscribers gained per $1000 spent on {channel}"
    )

# Run optimization
success, allocation, total_subscribers = optimize_ott(total_budget, channels, conversion_rates)

# Display results
if success:
    st.success("✅ Optimization Successful!")
    
    # Create two columns for displaying results
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Allocation")
        for channel, spend in allocation.items():
            st.write(f"**{channel}:**")
            st.write(f"Budget: ${spend:,.2f}")
            st.write(f"Expected Subscribers: {int(conversion_rates[channel] * spend / 1000):,}")
            st.write("---")
    
    with col2:
        st.subheader("Summary")
        st.write(f"**Total Budget:** ${total_budget:,.2f}")
        st.write(f"**Total Estimated Subscribers:** {int(total_subscribers):,}")
        roi = total_subscribers / total_budget * 1000
        st.write(f"**Average ROI (Subscribers per $1000):** {roi:.2f}")
        
        # Add conversion rates summary
        st.write("**Current Conversion Rates:**")
        for channel, rate in conversion_rates.items():
            st.write(f"{channel}: {rate} subscribers/${1000:,}")
    
    # Create visualization
    st.subheader("Budget Allocation Visualization")
    
    # Create DataFrame for visualization
    allocation_data = pd.DataFrame({
        "Channel": list(allocation.keys()),
        "Budget": list(allocation.values()),
        "Expected Subscribers": [int(conversion_rates[channel] * spend / 1000) 
                               for channel, spend in allocation.items()]
    })
    
    # Create two tabs for different visualizations
    tab1, tab2 = st.tabs(["Budget Allocation", "Expected Subscribers"])
    
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        bars = ax1.bar(allocation_data["Channel"], allocation_data["Budget"])
        ax1.set_xlabel("Marketing Channel")
        ax1.set_ylabel("Budget Allocation ($)")
        ax1.set_title("Budget Allocation Across Channels")
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        st.pyplot(fig1)
    
    with tab2:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        bars = ax2.bar(allocation_data["Channel"], allocation_data["Expected Subscribers"])
        ax2.set_xlabel("Marketing Channel")
        ax2.set_ylabel("Expected Subscribers")
        ax2.set_title("Expected Subscribers by Channel")
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,.0f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        st.pyplot(fig2)
    
else:
    st.error("❌ Optimization Failed! Please adjust your budget or conversion rates.")




def generate_excel_report(allocation, conversion_rates, total_budget, total_subscribers):
    """
    Generate Excel report with complete analysis
    """
    # Create a buffer to store the Excel file
    buffer = io.BytesIO()
    
    # Create Excel writer object
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Create summary dataframe
        summary_data = {
            'Metric': ['Total Budget', 'Total Subscribers', 'Average ROI (Subscribers per $1000)'],
            'Value': [
                f'${total_budget:,.2f}',
                f'{int(total_subscribers):,}',
                f'{(total_subscribers / total_budget * 1000):.2f}'
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Create allocation dataframe
        allocation_data = []
        for channel, budget in allocation.items():
            expected_subscribers = int(conversion_rates[channel] * budget / 1000)
            roi = expected_subscribers / budget * 1000
            allocation_data.append({
                'Channel': channel,
                'Budget': budget,
                'Conversion Rate': conversion_rates[channel],
                'Expected Subscribers': expected_subscribers,
                'ROI (Subscribers per $1000)': roi
            })
        allocation_df = pd.DataFrame(allocation_data)
        
        # Write each dataframe to a different worksheet
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        allocation_df.to_excel(writer, sheet_name='Channel Analysis', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        
        # Add formats
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        number_format = workbook.add_format({'num_format': '#,##0'})
        
        # Format the Channel Analysis worksheet
        worksheet = writer.sheets['Channel Analysis']
        worksheet.set_column('B:B', 15, money_format)  # Budget column
        worksheet.set_column('D:D', 15, number_format)  # Expected Subscribers column
        
    return buffer.getvalue()

def generate_pdf_report(allocation, conversion_rates, total_budget, total_subscribers):
    """
    Generate PDF report with complete analysis
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Set up styles
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "OTT Advertising Optimization Report", ln=True, align="C")
    pdf.ln(10)
    
    # Add timestamp
    pdf.set_font("Arial", "", 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f"Generated on: {timestamp}", ln=True)
    pdf.ln(10)
    
    # Summary Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Total Budget: ${total_budget:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total Expected Subscribers: {int(total_subscribers):,}", ln=True)
    pdf.cell(0, 10, f"Average ROI: {(total_subscribers / total_budget * 1000):.2f} subscribers per $1000", ln=True)
    pdf.ln(10)
    
    # Channel Analysis Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Channel Analysis", ln=True)
    pdf.set_font("Arial", "", 12)
    
    # Add table headers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 10, "Channel", 1)
    pdf.cell(35, 10, "Budget", 1)
    pdf.cell(35, 10, "Conv. Rate", 1)
    pdf.cell(35, 10, "Subscribers", 1)
    pdf.cell(35, 10, "ROI", 1)
    pdf.ln()
    
    # Add table data
    pdf.set_font("Arial", "", 10)
    for channel, budget in allocation.items():
        expected_subscribers = int(conversion_rates[channel] * budget / 1000)
        roi = expected_subscribers / budget * 1000
        
        pdf.cell(50, 10, channel, 1)
        pdf.cell(35, 10, f"${budget:,.0f}", 1)
        pdf.cell(35, 10, f"{conversion_rates[channel]}", 1)
        pdf.cell(35, 10, f"{expected_subscribers:,}", 1)
        pdf.cell(35, 10, f"{roi:.1f}", 1)
        pdf.ln()
    
    return pdf.output(dest="S").encode("latin1")

# Add these buttons after your existing visualization code
st.subheader("Download Analysis")
col1, col2 = st.columns(2)

with col1:
    # Excel download button
    excel_data = generate_excel_report(allocation, conversion_rates, total_budget, total_subscribers)
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_data,
        file_name=f"ott_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    # PDF download button
    pdf_data = generate_pdf_report(allocation, conversion_rates, total_budget, total_subscribers)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name=f"ott_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )