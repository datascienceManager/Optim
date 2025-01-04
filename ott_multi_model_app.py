import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

# Function to predict using Linear Regression
def linear_regression_model(X, y, future_years):
    model = LinearRegression().fit(X, y)
    future_X = np.array(future_years).reshape(-1, 1)
    predictions = model.predict(future_X)
    return predictions

# Function to predict using Random Forest
def random_forest_model(X, y, future_years):
    model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
    future_X = np.array(future_years).reshape(-1, 1)
    predictions = model.predict(future_X)
    return predictions

# Function to predict using ARIMA
def arima_model(data, future_years):
    model = ARIMA(data, order=(1, 1, 1)).fit()
    future_predictions = model.forecast(steps=len(future_years))
    return future_predictions

# Function to generate a PDF report
def generate_pdf_report(models, predictions, future_years, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Subscriber Prediction Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Generated on: {timestamp}", ln=True, align="C")
    pdf.ln(10)
    for model_name, pred in predictions.items():
        pdf.cell(200, 10, txt=f"Model: {model_name}", ln=True)
        for year, value in zip(future_years, pred):
            pdf.cell(200, 10, txt=f"Year {year}: {value:.2f} subscribers", ln=True)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin1")

# Streamlit app
st.title("Subscriber Prediction with Multiple Models")

# Upload historical data
st.subheader("Upload Historical Data")
st.write("Upload a CSV file with columns `Year` and `Subscribers`.")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    if "Year" in data.columns and "Subscribers" in data.columns:
        st.write("Uploaded Data:")
        st.write(data)

        # Prepare data
        X = data["Year"].values.reshape(-1, 1)
        y = data["Subscribers"].values
        future_years = st.slider("Years to Predict", min_value=1, max_value=10, value=5)
        future_years_list = list(range(data["Year"].max() + 1, data["Year"].max() + 1 + future_years))

        # Model selection
        st.subheader("Select Models")
        model_options = ["Linear Regression", "Random Forest", "ARIMA"]
        selected_models = st.multiselect("Choose models for prediction", model_options, default=["Linear Regression"])

        # Run predictions
        predictions = {}
        if "Linear Regression" in selected_models:
            predictions["Linear Regression"] = linear_regression_model(X, y, future_years_list)

        if "Random Forest" in selected_models:
            predictions["Random Forest"] = random_forest_model(X, y, future_years_list)

        if "ARIMA" in selected_models:
            predictions["ARIMA"] = arima_model(y, future_years_list)

        # Display predictions
        st.subheader("Predicted Subscriber Numbers")
        results_df = pd.DataFrame({"Year": future_years_list})
        for model_name, pred in predictions.items():
            results_df[model_name] = pred
        st.write(results_df)

        # Plot predictions
        st.subheader("Comparison of Predictions")
        plt.figure(figsize=(10, 5))
        plt.plot(data["Year"], data["Subscribers"], label="Historical Data", marker="o", color="black")
        for model_name, pred in predictions.items():
            plt.plot(future_years_list, pred, label=model_name, marker="o")
        plt.xlabel("Year")
        plt.ylabel("Subscribers")
        plt.legend()
        st.pyplot(plt)

        # Download report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf_data = generate_pdf_report(selected_models, predictions, future_years_list, timestamp)
        st.download_button(
            label="Download Prediction Report as PDF",
            data=pdf_data,
            file_name="Subscriber_Prediction_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Invalid data format. Ensure the columns are `Year` and `Subscribers`.")
else:
    st.info("Awaiting file upload...")

