import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import hashlib

# Configure page
st.set_page_config(
    page_title="FinanceFlow Dashboard",
    page_icon="💰",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    
    # Create transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, type TEXT, date TEXT)''')
    
    conn.commit()
    conn.close()

# User authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    try:
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                 (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute("SELECT id FROM users WHERE username=? AND password_hash=?", 
              (username, password_hash))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_transaction(user_id, amount, description, trans_type):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    date_str = datetime.now().strftime('%Y-%m-%d')
    c.execute("INSERT INTO transactions (user_id, amount, description, type, date) VALUES (?, ?, ?, ?, ?)",
              (user_id, amount, description, trans_type, date_str))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    conn = sqlite3.connect('simple_finance.db')
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC", 
                          conn, params=(user_id,))
    conn.close()
    return df

def delete_transaction(transaction_id):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()

def update_transaction(transaction_id, amount, description, trans_type):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    c.execute("UPDATE transactions SET amount=?, description=?, type=? WHERE id=?", 
              (amount, description, trans_type, transaction_id))
    conn.commit()
    conn.close()

def get_transaction_by_id(transaction_id):
    conn = sqlite3.connect('simple_finance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id=?", (transaction_id,))
    result = c.fetchone()
    conn.close()
    return result

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Initialize database
init_db()

# Main app
def main():
    st.title("💰 FinanceFlow Dashboard")
    st.markdown("### Advanced Personal Wealth Management System")
    st.markdown("**Built by Abhishek - Full-Stack Developer**")
    
    if st.session_state.user_id is None:
        # Login/Register page
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login")
                
                if login_btn:
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
        
        with tab2:
            st.subheader("Register")
            with st.form("register_form"):
                new_username = st.text_input("Username", key="reg_user")
                new_password = st.text_input("Password", type="password", key="reg_pass")
                register_btn = st.form_submit_button("Register")
                
                if register_btn:
                    if create_user(new_username, new_password):
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error("❌ Username already exists!")
    
    else:
        # Dashboard
        with st.sidebar:
            st.header(f"Welcome, {st.session_state.username}!")
            page = st.selectbox("Choose a page", [
                "📊 Overview",
                "➕ Add Transaction", 
                "💸 Transactions",
                "📈 Analytics",
                "🎯 Budgets",
                "🔍 Search"
            ])
            
            if st.button("🚪 Logout"):
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()
        
        if page == "📊 Overview":
            overview_page()
        elif page == "➕ Add Transaction":
            add_transaction_page()
        elif page == "💸 Transactions":
            transactions_page()
        elif page == "📈 Analytics":
            analytics_page()
        elif page == "🎯 Budgets":
            budgets_page()
        elif page == "🔍 Search":
            search_page()

def overview_page():
    st.header("📊 Financial Overview")
    
    df = get_transactions(st.session_state.user_id)
    
    if not df.empty:
        # Calculate metrics
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        net = income - expenses
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Income", f"£{income:,.2f}")
        with col2:
            st.metric("💸 Total Expenses", f"£{expenses:,.2f}")
        with col3:
            st.metric("📊 Net Income", f"£{net:,.2f}")
        with col4:
            st.metric("📋 Transactions", len(df))
        
        # Recent transactions
        st.subheader("🕐 Recent Transactions")
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.info("No transactions yet. Add your first transaction!")

def add_transaction_page():
    st.header("➕ Add New Transaction")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_type = st.selectbox("Type", ["income", "expense"])
            amount = st.number_input("Amount (£)", min_value=0.01, step=0.01)
        
        with col2:
            description = st.text_input("Description")
        
        submit = st.form_submit_button("Add Transaction", type="primary")
        
        if submit:
            if amount and description:
                add_transaction(st.session_state.user_id, amount, description, trans_type)
                st.success("✅ Transaction added successfully!")
                st.rerun()
            else:
                st.error("Please fill all fields")

def transactions_page():
    st.header("💸 Transaction Management")
    
    df = get_transactions(st.session_state.user_id)
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox("Filter by type", ["All", "income", "expense"])
        with col2:
            st.info("💡 Use Edit/Delete buttons on each transaction below")
        
        # Apply filter
        filtered_df = df.copy()
        if filter_type != "All":
            filtered_df = df[df['type'] == filter_type]
        
        # Display transactions with action buttons
        st.subheader("Your Transactions")
        
        for idx, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{row['date']}**")
                with col2:
                    st.write(f"**{row['description']}**")
                with col3:
                    color = "green" if row['type'] == 'income' else "red"
                    st.markdown(f"<span style='color:{color}'>**£{row['amount']:,.2f}**</span>", unsafe_allow_html=True)
                with col4:
                    type_emoji = "💰" if row['type'] == 'income' else "💸"
                    st.write(f"{type_emoji} {row['type'].title()}")
                with col5:
                    if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                        st.session_state[f'editing_{row["id"]}'] = True
                        st.rerun()
                with col6:
                    if st.button("🗑️ Delete", key=f"delete_{row['id']}", type="secondary"):
                        delete_transaction(row['id'])
                        st.success(f"Deleted: {row['description']}")
                        st.rerun()
                
                # Edit form
                if st.session_state.get(f'editing_{row["id"]}', False):
                    with st.form(f"edit_form_{row['id']}"):
                        st.write(f"**Editing: {row['description']}**")
                        edit_col1, edit_col2, edit_col3 = st.columns(3)
                        
                        with edit_col1:
                            new_amount = st.number_input("Amount (£)", value=float(row['amount']), min_value=0.01, step=0.01, key=f"amount_{row['id']}")
                        with edit_col2:
                            new_desc = st.text_input("Description", value=row['description'], key=f"desc_{row['id']}")
                        with edit_col3:
                            new_type = st.selectbox("Type", ["income", "expense"], index=0 if row['type']=='income' else 1, key=f"type_{row['id']}")
                        
                        edit_col4, edit_col5 = st.columns(2)
                        with edit_col4:
                            if st.form_submit_button("💾 Save Changes"):
                                update_transaction(row['id'], new_amount, new_desc, new_type)
                                st.session_state[f'editing_{row["id"]}'] = False
                                st.success("Transaction updated successfully!")
                                st.rerun()
                        with edit_col5:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f'editing_{row["id"]}'] = False
                                st.rerun()
                
                st.markdown("---")
        
        # Bulk actions
        st.subheader("📊 Bulk Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Clear all transactions
            if st.button("🗑️ Clear All Transactions", type="secondary"):
                if st.session_state.get('confirm_clear', False):
                    # Actually delete all
                    conn = sqlite3.connect('simple_finance.db')
                    c = conn.cursor()
                    c.execute("DELETE FROM transactions WHERE user_id=?", (st.session_state.user_id,))
                    conn.commit()
                    conn.close()
                    st.success("All transactions cleared!")
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm deletion of ALL transactions!")
        
        with col3:
            # Statistics
            total_transactions = len(filtered_df)
            st.metric("📋 Filtered Results", total_transactions)
        
    else:
        st.info("No transactions found. Add your first transaction!")
        if st.button("➕ Add Transaction"):
            st.switch_page("Add Transaction")

def analytics_page():
    st.header("📈 Financial Analytics")
    
    df = get_transactions(st.session_state.user_id)
    
    if not df.empty and len(df) > 1:
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Income vs Expenses chart
        summary = df.groupby('type')['amount'].sum().reset_index()
        
        fig = px.pie(
            summary, 
            values='amount', 
            names='type',
            title="Income vs Expenses",
            color_discrete_map={'income': 'green', 'expense': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trends
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby(['month', 'type'])['amount'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        
        fig2 = px.bar(
            monthly,
            x='month',
            y='amount',
            color='type',
            title="Monthly Trends",
            barmode='group'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Financial Health Score
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        
        if income > 0:
            savings_rate = ((income - expenses) / income) * 100
            health_score = min(100, max(0, savings_rate))
            
            fig3 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health_score,
                title={'text': "Financial Health Score"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            st.plotly_chart(fig3, use_container_width=True)
            
            # Insights
            st.subheader("💡 Financial Insights")
            if savings_rate > 20:
                st.success(f"🎉 Excellent! You're saving {savings_rate:.1f}% of your income!")
            elif savings_rate > 0:
                st.info(f"👍 Good job! You're saving {savings_rate:.1f}% of your income. Try to increase it!")
            else:
                st.warning("⚠️ You're spending more than you earn. Consider reducing expenses.")
    else:
        st.info("Add more transactions to see analytics.")

def budgets_page():
    st.header("🎯 Budget Management")
    
    df = get_transactions(st.session_state.user_id)
    
    if not df.empty:
        # Calculate current month expenses
        df['date'] = pd.to_datetime(df['date'])
        current_month = datetime.now().strftime('%Y-%m')
        monthly_expenses = df[
            (df['type'] == 'expense') & 
            (df['date'].dt.strftime('%Y-%m') == current_month)
        ]['amount'].sum()
        
        # Budget setter
        st.subheader("📊 Set Monthly Budget")
        
        # Get/set budget from session state
        if 'monthly_budget' not in st.session_state:
            st.session_state.monthly_budget = 1000.0  # Default budget
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_budget = st.number_input(
                "Monthly Budget (£)", 
                value=st.session_state.monthly_budget, 
                min_value=0.01, 
                step=10.0
            )
            
            if st.button("💾 Update Budget"):
                st.session_state.monthly_budget = new_budget
                st.success("Budget updated successfully!")
        
        with col2:
            # Budget progress
            budget_used_pct = (monthly_expenses / st.session_state.monthly_budget) * 100
            remaining_budget = st.session_state.monthly_budget - monthly_expenses
            
            st.metric("Monthly Budget", f"£{st.session_state.monthly_budget:,.2f}")
            st.metric("Spent This Month", f"£{monthly_expenses:,.2f}")
            st.metric("Remaining", f"£{remaining_budget:,.2f}")
        
        # Budget visualization
        st.subheader("📈 Budget Progress")
        
        # Progress bar
        progress_color = "normal"
        if budget_used_pct > 100:
            progress_color = "error"
        elif budget_used_pct > 80:
            progress_color = "warning"
        
        st.progress(min(budget_used_pct / 100, 1.0))
        
        if budget_used_pct > 100:
            st.error(f"⚠️ You've exceeded your budget by £{monthly_expenses - st.session_state.monthly_budget:.2f}!")
        elif budget_used_pct > 80:
            st.warning(f"⚠️ You've used {budget_used_pct:.1f}% of your budget. Be careful!")
        else:
            st.success(f"✅ You've used {budget_used_pct:.1f}% of your budget. Good job!")
        
        # Category breakdown
        st.subheader("💳 Expense Categories This Month")
        monthly_df = df[
            (df['type'] == 'expense') & 
            (df['date'].dt.strftime('%Y-%m') == current_month)
        ]
        
        if not monthly_df.empty:
            # Group by description (as a simple category system)
            category_spending = monthly_df.groupby('description')['amount'].sum().reset_index()
            category_spending = category_spending.sort_values('amount', ascending=False)
            
            fig = px.bar(
                category_spending,
                x='description',
                y='amount',
                title="Spending by Category This Month",
                labels={'description': 'Category', 'amount': 'Amount (£)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Add some transactions to set up budgets!")

def search_page():
    st.header("🔍 Search Transactions")
    
    df = get_transactions(st.session_state.user_id)
    
    if not df.empty:
        # Search filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("Search Description", placeholder="Enter keywords...")
        
        with col2:
            amount_range = st.slider(
                "Amount Range (£)", 
                min_value=0.0, 
                max_value=float(df['amount'].max()), 
                value=(0.0, float(df['amount'].max())),
                step=1.0
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                max_value=datetime.now()
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Text search
        if search_term:
            filtered_df = filtered_df[filtered_df['description'].str.contains(search_term, case=False, na=False)]
        
        # Amount range filter
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) & 
            (filtered_df['amount'] <= amount_range[1])
        ]
        
        # Date range filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df['date'] = pd.to_datetime(filtered_df['date'])
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= start_date) & 
                (filtered_df['date'].dt.date <= end_date)
            ]
        
        # Display results
        st.subheader(f"Search Results ({len(filtered_df)} transactions found)")
        
        if not filtered_df.empty:
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_income = filtered_df[filtered_df['type'] == 'income']['amount'].sum()
                st.metric("Total Income", f"£{total_income:,.2f}")
            
            with col2:
                total_expenses = filtered_df[filtered_df['type'] == 'expense']['amount'].sum()
                st.metric("Total Expenses", f"£{total_expenses:,.2f}")
            
            with col3:
                st.metric("Net Amount", f"£{total_income - total_expenses:,.2f}")
            
            # Results table
            st.dataframe(filtered_df[['date', 'description', 'amount', 'type']], use_container_width=True)
            
            # Export filtered results
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Search Results",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No transactions match your search criteria.")
    
    else:
        st.info("No transactions to search. Add some transactions first!")

if __name__ == "__main__":
    main()
