"""
Streamlit Frontend for Premium Care Financial Agent
Interactive dashboard for bank statement analysis and financial optimization
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Premium Care - Financial Analysis",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .recommendation-card {
            background-color: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #0066cc;
            margin: 10px 0;
            border-radius: 5px;
        }
        .anomaly-card {
            background-color: #ffe8e8;
            padding: 15px;
            border-left: 4px solid #cc0000;
            margin: 10px 0;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:8000"

def get_auth_header():
    """Get authorization header with token"""
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def register_user(username: str, email: str, password: str):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("✅ Registration successful! Please login.")
            return True
        else:
            st.error(f"❌ Registration failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

def login_user(email: str, password: str):
    """Login user and save token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.user = data["user"]
            st.success("✅ Login successful!")
            st.session_state.current_page = "dashboard"
            return True
        else:
            st.error(f"❌ Login failed: {response.json().get('detail', 'Invalid credentials')}")
            return False
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

def logout_user():
    """Logout user"""
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.current_page = "login"
    st.success("✅ Logged out successfully")

# ============================================================================
# LOGIN PAGE
# ============================================================================

def show_login_page():
    """Display login/register page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 💰 Premium Care")
        st.markdown("### Financial Analysis & Optimization Agent")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        # LOGIN TAB
        with tab1:
            st.markdown("### Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("🔓 Login", use_container_width=True, key="login_button"):
                if email and password:
                    login_user(email, password)
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter email and password")
        
        # REGISTER TAB
        with tab2:
            st.markdown("### Create New Account")
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            password_confirm = st.text_input("Confirm Password", type="password", key="register_confirm")
            
            if st.button("📝 Register", use_container_width=True, key="register_button"):
                if not all([username, email, password, password_confirm]):
                    st.warning("⚠️ Please fill all fields")
                elif password != password_confirm:
                    st.warning("⚠️ Passwords do not match")
                else:
                    register_user(username, email, password)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def show_dashboard_page():
    """Display main dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        if st.session_state.user:
            st.write(f"**{st.session_state.user['username']}**")
            st.write(f"📧 {st.session_state.user['email']}")
        
        st.markdown("---")
        
        selected_page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📤 Upload Statement", "📈 Analysis", "💡 Recommendations"]
        )
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Main content
    if selected_page == "📊 Dashboard":
        show_main_dashboard()
    elif selected_page == "📤 Upload Statement":
        show_upload_page()
    elif selected_page == "📈 Analysis":
        show_analysis_page()
    elif selected_page == "💡 Recommendations":
        show_recommendations_page()

def show_main_dashboard():
    """Display main dashboard overview"""
    
    st.markdown("# 📊 Dashboard")
    st.markdown("Welcome back! Here's your financial overview.")
    
    try:
        # Get user's statements
        response = requests.get(
            f"{API_BASE_URL}/user/statements",
            params={"token": st.session_state.access_token}
        )
        
        if response.status_code == 200:
            statements = response.json()
            
            if statements:
                st.markdown("## 📋 Recent Statements")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Statements", len(statements))
                with col2:
                    total_transactions = sum(s["transaction_count"] for s in statements)
                    st.metric("Total Transactions", total_transactions)
                with col3:
                    total_amount = sum(s["total_amount"] for s in statements)
                    st.metric("Total Amount", f"${total_amount:,.2f}")
                
                st.markdown("---")
                
                # Display statements in table
                df = pd.DataFrame(statements)
                df["uploaded_at"] = pd.to_datetime(df["uploaded_at"]).dt.strftime("%Y-%m-%d %H:%M")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("📭 No statements uploaded yet. Start by uploading a bank statement!")
        else:
            st.error("❌ Error loading statements")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_upload_page():
    """Display file upload page"""
    
    st.markdown("# 📤 Upload Bank Statement")
    st.markdown("Upload your bank statement PDF to analyze your finances")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file:
        st.info(f"📄 Selected: {uploaded_file.name}")
        
        if st.button("🔄 Process Statement", use_container_width=True):
            with st.spinner("Processing your statement..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/upload/statement",
                        files={"file": uploaded_file},
                        params={"token": st.session_state.access_token}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Statement processed successfully!")
                        st.info(f"📊 Found {data['transaction_count']} transactions")
                        
                        # Store statement_id for later use
                        st.session_state.current_statement_id = data["statement_id"]
                        
                        st.balloons()
                    else:
                        st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def show_analysis_page():
    """Display analysis results"""
    
    st.markdown("# 📈 Financial Analysis")
    
    try:
        # Get user's statements
        response = requests.get(
            f"{API_BASE_URL}/user/statements",
            params={"token": st.session_state.access_token}
        )
        
        if response.status_code == 200:
            statements = response.json()
            
            if statements:
                # Select statement
                statement_options = {s["filename"]: s["id"] for s in statements}
                selected_statement = st.selectbox("Select Statement", list(statement_options.keys()))
                statement_id = statement_options[selected_statement]
                
                if st.button("📊 Analyze", use_container_width=True):
                    with st.spinner("Analyzing statement..."):
                        try:
                            response = requests.get(
                                f"{API_BASE_URL}/analysis/{statement_id}",
                                params={"token": st.session_state.access_token}
                            )
                            
                            if response.status_code == 200:
                                analysis = response.json()
                                
                                # Summary metrics
                                st.markdown("## 📊 Summary")
                                summary = analysis["summary"]
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Expenses", f"${summary['total_expenses']:,.2f}")
                                with col2:
                                    st.metric("Total Income", f"${summary['total_income']:,.2f}")
                                with col3:
                                    st.metric("Net Flow", f"${summary['net_flow']:,.2f}")
                                with col4:
                                    st.metric("Transactions", summary['transaction_count'])
                                
                                st.markdown("---")
                                
                                # Spending by category pie chart
                                if analysis["spending_by_category"]:
                                    st.markdown("## 💳 Spending by Category")
                                    
                                    fig = px.pie(
                                        values=list(analysis["spending_by_category"].values()),
                                        names=list(analysis["spending_by_category"].keys()),
                                        title="Spending Distribution"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Recurring transactions
                                if analysis["recurring_transactions"]:
                                    st.markdown("## 🔄 Recurring Transactions")
                                    
                                    recurring_data = []
                                    for merchant, data in analysis["recurring_transactions"].items():
                                        recurring_data.append({
                                            "Merchant": merchant,
                                            "Amount": f"${data['amount']:.2f}",
                                            "Frequency": data.get('frequency', 'Unknown')
                                        })
                                    
                                    st.dataframe(pd.DataFrame(recurring_data), use_container_width=True)
                                
                                # Anomalies
                                if analysis["anomalies"]:
                                    st.markdown("## ⚠️ Unusual Transactions")
                                    
                                    for anomaly in analysis["anomalies"][:5]:
                                        with st.container():
                                            st.markdown(f"""
                                            <div class="anomaly-card">
                                                <strong>{anomaly['description']}</strong><br>
                                                Amount: ${anomaly['amount']:.2f} | Date: {anomaly['date']}<br>
                                                Severity: {anomaly.get('z_score', 0):.2f}σ
                                            </div>
                                            """, unsafe_allow_html=True)
                                
                                # Top merchants
                                if analysis["merchant_analysis"]["top_merchants"]:
                                    st.markdown("## 🏪 Top Merchants")
                                    
                                    merchants = analysis["merchant_analysis"]["top_merchants"][:10]
                                    fig = px.bar(
                                        x=[m['merchant'] for m in merchants],
                                        y=[m['total_amount'] for m in merchants],
                                        labels={'x': 'Merchant', 'y': 'Total Spent'},
                                        title="Top Spending Merchants"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            else:
                                st.error("❌ Error analyzing statement")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                st.info("📭 No statements uploaded yet. Upload one first!")
        
        else:
            st.error("❌ Error loading statements")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_recommendations_page():
    """Display AI recommendations"""
    
    st.markdown("# 💡 Smart Recommendations")
    st.markdown("AI-powered suggestions to optimize your finances")
    
    try:
        # Get user's statements
        response = requests.get(
            f"{API_BASE_URL}/user/statements",
            params={"token": st.session_state.access_token}
        )
        
        if response.status_code == 200:
            statements = response.json()
            
            if statements:
                # Select statement
                statement_options = {s["filename"]: s["id"] for s in statements}
                selected_statement = st.selectbox("Select Statement", list(statement_options.keys()), key="rec_select")
                statement_id = statement_options[selected_statement]
                
                if st.button("💡 Get Recommendations", use_container_width=True):
                    with st.spinner("Generating recommendations..."):
                        try:
                            response = requests.get(
                                f"{API_BASE_URL}/recommendations/{statement_id}",
                                params={"token": st.session_state.access_token}
                            )
                            
                            if response.status_code == 200:
                                recommendations = response.json()
                                
                                if recommendations:
                                    # Filter by priority
                                    priority_filter = st.multiselect(
                                        "Filter by Priority",
                                        ["high", "medium", "low"],
                                        default=["high", "medium", "low"]
                                    )
                                    
                                    filtered_recs = [r for r in recommendations if r["priority"] in priority_filter]
                                    
                                    total_savings = sum(r["potential_savings"] for r in filtered_recs)
                                    st.metric("💰 Total Potential Savings", f"${total_savings:,.2f}")
                                    
                                    st.markdown("---")
                                    
                                    for i, rec in enumerate(filtered_recs, 1):
                                        priority_color = {
                                            "high": "🔴",
                                            "medium": "🟡",
                                            "low": "🟢"
                                        }.get(rec["priority"], "⚪")
                                        
                                        with st.expander(f"{priority_color} {i}. {rec['title']} (Save: ${rec['potential_savings']:.2f})"):
                                            st.markdown(f"**Category:** {rec['category']}")
                                            st.markdown(f"**Description:** {rec['description']}")
                                            st.markdown(f"**Priority:** {rec['priority'].upper()}")
                                            
                                            if rec["action_steps"]:
                                                st.markdown("**Action Steps:**")
                                                for step in rec["action_steps"]:
                                                    st.write(f"✓ {step}")
                                else:
                                    st.info("No recommendations generated. Try a different statement.")
                            
                            else:
                                st.error("❌ Error generating recommendations")
                        
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                st.info("📭 No statements uploaded yet. Upload one first!")
        
        else:
            st.error("❌ Error loading statements")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main app logic"""
    
    if st.session_state.access_token:
        show_dashboard_page()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
