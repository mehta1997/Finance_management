import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json

# Configure Streamlit page
st.set_page_config(
    page_title="FinanceFlow Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Helper functions
def make_api_request(endpoint, method="GET", data=None, headers=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if headers is None:
            headers = {}
        
        if st.session_state.token:
            headers["Authorization"] = f"Bearer {st.session_state.token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.user_info = None
            st.error("Session expired. Please login again.")
            return None
            
        return response
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FinanceFlow API. Make sure the server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def login_page():
    """Login/Register page"""
    st.title("🚀 FinanceFlow Dashboard")
    st.markdown("### Advanced Personal Wealth Management System")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    # Login API call
                    response = make_api_request("/auth/token", "POST", {
                        "username": username,
                        "password": password
                    })
                    
                    if response and response.status_code == 200:
                        token_data = response.json()
                        st.session_state.token = token_data["access_token"]
                        st.session_state.user_info = {"username": username}
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Create new account")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_full_name = st.text_input("Full Name", key="reg_name")
            register = st.form_submit_button("Register")
            
            if register:
                if reg_username and reg_email and reg_password and reg_full_name:
                    # Validate email format
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, reg_email):
                        st.error("Please enter a valid email address")
                        return
                    
                    response = make_api_request("/auth/register", "POST", {
                        "username": reg_username,
                        "email": reg_email,
                        "password": reg_password
                    })
                    
                    if response and response.status_code == 201:
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error("❌ Registration failed. Username or email might already exist.")
                else:
                    st.error("Please fill all fields")

def dashboard_page():
    """Main dashboard page"""
    st.title("💰 FinanceFlow Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.user_info['username']}**!")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose a page", [
            "📊 Overview", 
            "📈 Wealth Insights", 
            "🔍 Spending Patterns",
            "💸 Transactions",
            "➕ Add Transaction"
        ])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.user_info = None
            st.rerun()
    
    # Main content based on selected page
    if page == "📊 Overview":
        overview_page()
    elif page == "📈 Wealth Insights":
        wealth_insights_page()
    elif page == "🔍 Spending Patterns":
        spending_patterns_page()
    elif page == "💸 Transactions":
        transactions_page()
    elif page == "➕ Add Transaction":
        add_transaction_page()

def overview_page():
    """Overview dashboard page"""
    st.header("📊 Financial Overview")
    
    # Get transaction summary
    response = make_api_request("/transactions/summary/")
    if response and response.status_code == 200:
        summary = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Income",
                value=f"${summary['total_income']:,.2f}"
            )
        
        with col2:
            st.metric(
                label="💸 Total Expenses", 
                value=f"${summary['total_expenses']:,.2f}"
            )
        
        with col3:
            st.metric(
                label="📊 Net Income",
                value=f"${summary['net_income']:,.2f}",
                delta=f"${summary['net_income']:,.2f}"
            )
        
        with col4:
            st.metric(
                label="📋 Transactions",
                value=summary['transaction_count']
            )
    
    # Quick actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Income", type="primary"):
            st.session_state.quick_transaction_type = "income"
            st.rerun()
    
    with col2:
        if st.button("➖ Add Expense", type="secondary"):
            st.session_state.quick_transaction_type = "expense"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", type="secondary"):
            st.rerun()

def wealth_insights_page():
    """Wealth insights analytics page"""
    st.header("📈 Wealth Insights")
    
    # Period selector
    period_days = st.selectbox("Analysis Period", [7, 30, 90, 180, 365], index=1)
    
    response = make_api_request(f"/transactions/analytics/wealth-insights?period_days={period_days}")
    
    if response and response.status_code == 200:
        insights = response.json()
        
        if "message" in insights:
            st.info(insights["message"])
            return
        
        # Financial Health Score
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Create gauge chart for financial health score
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = insights["financial_health_score"],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Financial Health Score"},
                delta = {'reference': 80},
                gauge = {'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps' : [{'range': [0, 50], 'color': "lightgray"},
                                  {'range': [50, 80], 'color': "gray"}],
                        'threshold' : {'line': {'color': "red", 'width': 4},
                                      'thickness': 0.75, 'value': 90}}))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.metric("💰 Total Income", f"${insights['total_income']:,.2f}")
            st.metric("💸 Total Expenses", f"${insights['total_expenses']:,.2f}")
            st.metric("📊 Net Wealth Change", f"${insights['net_wealth_change']:,.2f}")
            st.metric("💾 Savings Rate", f"{insights['savings_rate_percent']}%")
        
        # Spending Distribution
        st.subheader("💳 Spending Distribution")
        if insights["spending_distribution"]:
            categories = list(insights["spending_distribution"].keys())
            amounts = [insights["spending_distribution"][cat]["amount"] for cat in categories]
            percentages = [insights["spending_distribution"][cat]["percentage"] for cat in categories]
            
            fig = px.pie(
                values=amounts, 
                names=categories,
                title="Spending by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Insights & Recommendations
        st.subheader("🎯 Insights & Recommendations")
        insights_data = insights["insights"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🔝 Top Expense Category: **{insights_data.get('top_expense_category', 'N/A')}**")
            st.info(f"📊 Average Transaction: **${insights_data.get('average_transaction', 0):.2f}**")
        
        with col2:
            st.info(f"📈 Transaction Frequency: **{insights_data.get('transaction_frequency', 0):.1f}/day**")
            st.success(f"💡 {insights_data.get('recommendation', 'Keep tracking your finances!')}")

def spending_patterns_page():
    """Spending patterns analysis page"""
    st.header("🔍 Spending Pattern Analysis")
    
    response = make_api_request("/transactions/analytics/spending-patterns")
    
    if response and response.status_code == 200:
        patterns = response.json()
        
        if "message" in patterns:
            st.info(patterns["message"])
            return
        
        st.markdown(f"**{patterns['analysis_summary']}**")
        st.caption(f"Data Period: {patterns['data_period']}")
        
        # Weekly patterns
        st.subheader("📅 Weekly Spending Patterns")
        weekly_data = patterns["weekly_patterns"]
        
        if weekly_data:
            days = list(weekly_data.keys())
            amounts = [weekly_data[day]["total_spent"] for day in days]
            
            fig = px.bar(
                x=days,
                y=amounts,
                title="Spending by Day of Week",
                labels={"x": "Day of Week", "y": "Total Spent ($)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trends
        st.subheader("📈 Monthly Trends")
        monthly_data = patterns["monthly_trends"]
        
        if monthly_data:
            months = list(monthly_data.keys())
            amounts = list(monthly_data.values())
            
            fig = px.line(
                x=months,
                y=amounts,
                title="Monthly Spending Trends",
                labels={"x": "Month", "y": "Total Spent ($)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Anomaly detection
        st.subheader("⚠️ Spending Anomalies")
        anomalies = patterns["anomaly_detection"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("High Spending Threshold", f"${anomalies['high_spending_threshold']:.2f}")
        with col2:
            st.metric("Total Anomalies Detected", anomalies['total_anomalies'])
        
        # Show anomalous transactions
        if anomalies["anomalous_transactions"]:
            st.subheader("🚨 High Spending Days")
            anomaly_df = pd.DataFrame(anomalies["anomalous_transactions"])
            st.dataframe(anomaly_df, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        for rec in patterns["recommendations"]:
            st.info(f"• {rec}")

def transactions_page():
    """Transactions management page"""
    st.header("💸 Transaction History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        transaction_type = st.selectbox("Type", ["All", "income", "expense"])
    with col2:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col3:
        end_date = st.date_input("End Date", value=date.today())
    
    # Build query parameters
    params = []
    if transaction_type != "All":
        params.append(f"transaction_type={transaction_type}")
    params.append(f"start_date={start_date}")
    params.append(f"end_date={end_date}")
    
    query_string = "&".join(params)
    response = make_api_request(f"/transactions/?{query_string}")
    
    if response and response.status_code == 200:
        transactions = response.json()
        
        if transactions:
            # Convert to DataFrame for better display
            df = pd.DataFrame(transactions)
            df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
            
            # Display transactions
            st.dataframe(df[['transaction_date', 'description', 'amount', 'transaction_type']], 
                        use_container_width=True)
            
            st.caption(f"Showing {len(transactions)} transactions")
        else:
            st.info("No transactions found for the selected criteria")

def add_transaction_page():
    """Add new transaction page"""
    st.header("➕ Add New Transaction")
    
    with st.form("add_transaction"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.selectbox("Type", ["income", "expense"])
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            description = st.text_input("Description")
        
        with col2:
            transaction_date = st.date_input("Date", value=date.today())
            # You would need to get actual accounts/categories from API
            account_id = st.number_input("Account ID", min_value=1, value=1)
            category_id = st.number_input("Category ID", min_value=1, value=1)
        
        submitted = st.form_submit_button("Add Transaction", type="primary")
        
        if submitted:
            if amount and description:
                transaction_data = {
                    "amount": amount,
                    "description": description,
                    "transaction_type": transaction_type,
                    "transaction_date": transaction_date.isoformat(),
                    "account_id": account_id,
                    "category_id": category_id
                }
                
                response = make_api_request("/transactions/", "POST", transaction_data)
                
                if response and response.status_code == 200:
                    st.success("✅ Transaction added successfully!")
                else:
                    st.error("❌ Failed to add transaction")
            else:
                st.error("Please fill in all required fields")

# Main app logic
def main():
    if st.session_state.token is None:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
