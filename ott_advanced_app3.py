import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpProblem, LpVariable, value
from sklearn.linear_model import LinearRegression
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

# Optimization function
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

# Function to create PDF report
def generate_pdf(direct_spend, indirect_spend, total_subscribers, budget, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="OTT Advertising Optimization Report", ln=True, align="C")
    pdf.image("logo.png", x=10, y=8, w=30)  # Add logo
    pdf.ln(20)
    pdf.cell(200, 10, txt=f"Report Generated: {timestamp}", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Budget: ${budget:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Optimal Spending on Direct Advertising: ${direct_spend:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Optimal Spending on Indirect Advertising: ${indirect_spend:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Subscribers Gained: {total_subscribers:,.0f}", ln=True)
    return pdf.output(dest="S").encode("latin1")

# Streamlit app
st.title("OTT Advertising Optimization with Predictions")

# Sidebar inputs
st.sidebar.header("Adjust Parameters in Real-Time")
budget = st.sidebar.slider("Total Budget ($)", min_value=50000, max_value=500000, value=200000, step=10000)
min_indirect = st.sidebar.slider("Minimum Indirect Spend ($)", min_value=10000, max_value=200000, value=50000, step=5000)
direct_cap = st.sidebar.slider("Direct Advertising Cap (% of total spend)", min_value=0.1, max_value=1.0, value=0.6, step=0.1)
a = st.sidebar.slider("Direct Diminishing Returns Factor (a)", min_value=0.01, max_value=0.05, value=0.02, step=0.005)
b = st.sidebar.slider("Indirect Diminishing Returns Factor (b)", min_value=0.01, max_value=0.05, value=0.015, step=0.005)

# Run optimization instantly as sliders change
success, direct_spend, indirect_spend, total_subscribers = optimize_ott(
    budget, min_indirect, direct_cap, a, b
)

if success:
    st.success("Optimization Successful!")
    st.write(f"**Optimal spending on direct advertising**: ${direct_spend:,.2f}")
    st.write(f"**Optimal spending on indirect advertising**: ${indirect_spend:,.2f}")
    st.write(f"**Total subscribers gained**: {total_subscribers:,.0f}")

    # Visualization
    allocation_data = pd.DataFrame({
        "Category": ["Direct Advertising", "Indirect Advertising"],
        "Spending": [direct_spend, indirect_spend]
    })
    st.bar_chart(allocation_data.set_index("Category"))

    # Sensitivity Analysis
    st.subheader("Sensitivity Analysis")
    budgets = range(50000, 500001, 50000)
    results = []
    for bgt in budgets:
        success, ds, is_, ts = optimize_ott(bgt, min_indirect, direct_cap, a, b)
        if success:
            results.append((bgt, ds, is_, ts))

    sensitivity_df = pd.DataFrame(results, columns=["Budget", "Direct Spend", "Indirect Spend", "Total Subscribers"])
    st.write("How varying the total budget affects the results:")
    st.line_chart(sensitivity_df.set_index("Budget"))

    # PDF Report Download
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_data = generate_pdf(direct_spend, indirect_spend, total_subscribers, budget, timestamp)
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="OTT_Optimization_Report.pdf",
        mime="application/pdf"
    )
else:
    st.error("Optimization Failed! Please adjust your inputs.")

# Machine Learning Model for Future Subscriber Prediction
st.subheader("Future Subscriber Prediction")
st.write("Upload historical data for predictions. Format: `Year`, `Subscribers`")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    if "Year" in data.columns and "Subscribers" in data.columns:
        st.write("Uploaded Data:")
        st.write(data)

        # Train linear regression model
        X = data["Year"].values.reshape(-1, 1)
        y = data["Subscribers"].values
        model = LinearRegression().fit(X, y)

        # Predict future subscribers
        future_years = st.slider("Future Years to Predict", min_value=1, max_value=10, value=5)
        future_X = pd.DataFrame({"Year": range(data["Year"].max() + 1, data["Year"].max() + 1 + future_years)})
        future_X["Predicted Subscribers"] = model.predict(future_X["Year"].values.reshape(-1, 1))

        st.write("Predicted Future Subscribers:")
        st.write(future_X)

        # Visualization of predictions
        plt.figure(figsize=(10, 5))
        plt.scatter(data["Year"], data["Subscribers"], color="blue", label="Historical Data")
        plt.plot(future_X["Year"], future_X["Predicted Subscribers"], color="red", label="Predictions")
        plt.xlabel("Year")
        plt.ylabel("Subscribers")
        plt.legend()
        st.pyplot(plt)
    else:
        st.error("Invalid data format. Ensure the columns are `Year` and `Subscribers`.")
