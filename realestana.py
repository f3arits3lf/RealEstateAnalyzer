import streamlit as st
import numpy as np
import numpy_financial as npf
import json

# Function to calculate mortgage payment
def calculate_mortgage_payment(loan_amount, monthly_interest, num_payments):
    if monthly_interest == 0:
        return loan_amount / num_payments
    return loan_amount * (monthly_interest * (1 + monthly_interest) ** num_payments) / ((1 + monthly_interest) ** num_payments - 1)

# Function to calculate IRR
def calculate_irr(price, rent, total_expenses, loan_amount, loan_term, interest_rate):
    try:
        cash_flows = [-price] + [(rent - total_expenses - (loan_amount * (interest_rate / 12))) for _ in range(loan_term * 12)]
        irr = npf.irr(cash_flows)
        return irr * 100  # Return as percentage
    except Exception as e:
        return 0  # Handle any potential errors by returning 0 for IRR

# Function to calculate payback period
def calculate_payback_period(down_payment, cash_flow):
    if cash_flow > 0:
        return down_payment / cash_flow
    return float('inf')  # Return infinity if cash_flow is negative

# Streamlit App
def main():
    st.title("Real Estate Deal Analyzer")

    # Create tabs for different functionalities
    tabs = st.tabs(["Property Input", "Analysis Results", "Scenario Analysis", "Sensitivity Analysis", "Historical Comparisons", "Donate"])

    # Property Input Tab
    with tabs[0]:
        st.header("Property Input")
        property_price = st.number_input("Property Price ($):", min_value=0.0, value=100000.0, step=1000.0)
        rent_income = st.number_input("Monthly Rent Income ($):", min_value=0.0, value=1000.0, step=100.0)
        operating_expenses = st.number_input("Operating Expenses ($/month):", min_value=0.0, value=200.0, step=50.0)
        property_tax = st.number_input("Property Tax ($/year):", min_value=0.0, value=1200.0, step=100.0)
        loan_amount = st.number_input("Loan Amount ($):", min_value=0.0, value=80000.0, step=1000.0)
        down_payment = st.number_input("Down Payment ($):", min_value=0.0, value=20000.0, step=1000.0)
        interest_rate = st.number_input("Interest Rate (%):", min_value=0.0, value=5.0, step=0.1)
        loan_term = st.number_input("Loan Term (years):", min_value=1, value=30, step=1)

    # Analysis Results Tab
    with tabs[1]:
        st.header("Analysis Results")
        if st.button("Calculate Metrics"):
            try:
                # Extract Input Values
                rent = rent_income * 12  # Annual Rent
                expenses = operating_expenses * 12  # Annual Expenses
                monthly_interest = interest_rate / 100 / 12
                num_payments = loan_term * 12

                # Calculate Mortgage Payment
                mortgage_payment = calculate_mortgage_payment(loan_amount, monthly_interest, num_payments)
                annual_debt_service = mortgage_payment * 12

                # Calculate Key Metrics
                total_expenses = expenses + property_tax
                noi = rent - total_expenses
                cash_flow = noi - annual_debt_service
                cap_rate = (noi / property_price) * 100 if property_price > 0 else 0
                dcr = noi / annual_debt_service if annual_debt_service > 0 else 0
                cash_on_cash_return = (cash_flow / down_payment) * 100 if down_payment > 0 else 0
                ltv = (loan_amount / property_price) * 100 if property_price > 0 else 0
                opex_ratio = (total_expenses / rent) * 100 if rent > 0 else 0

                # Advanced Metrics
                irr = calculate_irr(property_price, rent, total_expenses, loan_amount, loan_term, interest_rate / 100)
                payback_period = calculate_payback_period(down_payment, cash_flow)

                # Display Results
                st.write(f"Net Operating Income (NOI): ${noi:,.2f}")
                st.write(f"Annual Cash Flow: ${cash_flow:,.2f}")
                st.write(f"Monthly Mortgage Payment: ${mortgage_payment:,.2f}")
                st.write(f"Cap Rate: {cap_rate:.2f}%")
                st.write(f"Debt Coverage Ratio (DCR): {dcr:.2f}")
                st.write(f"Cash-on-Cash Return: {cash_on_cash_return:.2f}%")
                st.write(f"Loan-to-Value Ratio (LTV): {ltv:.2f}%")
                st.write(f"Operating Expense Ratio (OER): {opex_ratio:.2f}%")
                st.write(f"Internal Rate of Return (IRR): {irr:.2f}%")
                st.write(f"Payback Period: {'Not Applicable' if cash_flow <= 0 else f'{payback_period:.2f} years'}")
            except ValueError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Scenario Analysis Tab
    with tabs[2]:
        st.header("Scenario Analysis")
        adjusted_rent = st.slider("Adjusted Monthly Rent Income ($):", min_value=0, max_value=10000, value=int(rent_income), step=100)
        adjusted_expenses = st.slider("Adjusted Operating Expenses ($/month):", min_value=0, max_value=5000, value=int(operating_expenses), step=50)
        if st.button("Calculate Scenario Metrics"):
            try:
                # Calculate Scenario Metrics
                adjusted_annual_rent = adjusted_rent * 12
                adjusted_annual_expenses = adjusted_expenses * 12
                adjusted_noi = adjusted_annual_rent - (adjusted_annual_expenses + property_tax)
                adjusted_cash_flow = adjusted_noi - annual_debt_service
                st.write(f"Scenario Net Operating Income (NOI): ${adjusted_noi:,.2f}")
                st.write(f"Scenario Annual Cash Flow: ${adjusted_cash_flow:,.2f}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Sensitivity Analysis Tab
    with tabs[3]:
        st.header("Sensitivity Analysis")
        interest_rates = np.linspace(interest_rate - 2, interest_rate + 2, 5)
        rent_values = np.linspace(rent_income * 0.8, rent_income * 1.2, 5)
        if st.button("Perform Sensitivity Analysis"):
            try:
                sensitivity_results = []
                for rate in interest_rates:
                    for rent in rent_values:
                        adjusted_rent = rent * 12
                        total_expenses = (operating_expenses * 12) + property_tax
                        mortgage_payment = calculate_mortgage_payment(loan_amount, rate / 100 / 12, loan_term * 12)
                        annual_debt_service = mortgage_payment * 12
                        noi = adjusted_rent - total_expenses
                        cash_flow = noi - annual_debt_service
                        sensitivity_results.append(f"Interest Rate: {rate:.2f}%, Rent: ${rent:.2f} -> NOI: ${noi:,.2f}, Cash Flow: ${cash_flow:,.2f}")
                st.write("\n".join(sensitivity_results))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Historical Comparisons Tab
    with tabs[4]:
        st.header("Historical Comparisons")
        st.write("Comparison of multiple properties loaded here.")
        # Placeholder for future implementation of data loading and comparison

    # Donate Tab
    with tabs[5]:
        st.header("Support My Work")
        st.write("If you enjoy using this tool, consider supporting my work!")
        if st.button("Buy Me a Coffee"):
            st.markdown("[Buy Me a Coffee](https://buymeacoffee.com/scottalafol)")

if __name__ == "__main__":
    main()
