import streamlit as st
import sqlite3
import hashlib
import base64
import openpyxl
import pandas as pd 
import os
from streamlit.components.v1 import html



# ---- Helper Functions ----
def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """Get a database connection."""
    return sqlite3.connect("users.db")

def create_user_table():
    """Create a user table if not exists."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()

def add_user(username, email, password):
    """Add a new user to the database."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hash_password(password)))
        conn.commit()

def authenticate_user(username, password):
    """Check if the username and password match."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                  (username, hash_password(password)))
        user = c.fetchone()
    return user

def update_password(email, new_password):
    """Update the user's password."""
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE email = ?",
                  (hash_password(new_password), email))
        conn.commit()

# ---- Initialize Database ----
create_user_table()

# ---- Page Configurations ----
st.set_page_config(
    page_title="Air Pollution Analysis Dashboard",
    page_icon="🌬️",
    layout="centered"
)

# ---- Custom Styling ----
st.markdown(
    """<style>
        .stButton button { 
            background-color: #4CAF50; 
            color: white; 
            border-radius: 8px;
        }
        .stTextInput > div > input {
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        .stApp {
            background: #f0f2f6;  /* Light grey background color */
            padding: 20px;
        }
        .css-1aumxhk {
            background-color: #f0f2f6;  /* Light grey background color for main container */
        }
        .stMarkdown p {
            font-size: 16px; 
            line-height: 1.6;
        }
        .blurred-label {
            font-weight: bold; /* Make text bold */
            display: inline-block;
            background: rgba(255, 255, 255, 0.2); /* Transparent white background */
            backdrop-filter: blur(5px); /* Apply blur effect */
            -webkit-backdrop-filter: blur(5px); /* Apply blur for Safari */
            padding: 5px 10px; /* Padding around the text */
            border-radius: 8px; /* Rounded corners */
            color: black; /* Text color */
        }
    </style>""",
    unsafe_allow_html=True
)

# Function to encode image in base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to add a background image using custom CSS
def add_background_image(image_file):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/png;base64,{image_file});
            background-size: cover;
            
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Replace 'background.jpg' with your image file path
image_path = "smoke.jpg"
if os.path.exists(image_path):
    image_base64 = get_base64_image(image_path)
    add_background_image(image_base64)
else:
    st.warning("Background image not found.")

# ---- App State Management ----
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "register"

# ---- Navigation Functions ----
def show_register_page():
    st.markdown("<h1 style='text-align: center; color: black;'>Hi! Unlock the Story Behind the Data</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .st-emotion-cache-ue6h4q{
            min-height: 0.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Register")

    # username = st.text_input("Username*", key="register_username")
    st.markdown('<label class="blurred-label">Username*</label>', unsafe_allow_html=True)
    username = st.text_input("", key="register_username")
    # Email Field
    st.markdown('<label class="blurred-label">Email*</label>', unsafe_allow_html=True)
    email = st.text_input("", key="register_email")

    # Password Field
    st.markdown('<label class="blurred-label">Password*</label>', unsafe_allow_html=True)
    password = st.text_input("", type="password", key="register_password")

    # Confirm Password Field
    st.markdown('<label class="blurred-label">Confirm Password*</label>', unsafe_allow_html=True)
    confirm_password = st.text_input("", type="password", key="register_confirm_password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        else:
            try:
                add_user(username, email, password)
                st.success("Account created successfully!")
                st.session_state["current_page"] = "login"
            except sqlite3.IntegrityError:
                st.error("Username or Email already exists! Try Again ")

    # Display inline text and button
    col1, col2 = st.columns([3, 1])  # Adjust column widths
    with col1:
        st.markdown('<div style="text-align: right;font-weight:bold">Are You Already Registered?</div>', unsafe_allow_html=True)
    with col2:
        if st.button("go to Login page"):
            st.session_state["current_page"] = "login"
            


def show_login_page():
    st.markdown(
        """
        <style>
        .st-emotion-cache-ue6h4q{
            min-height: 0.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Please Log In")
    st.markdown('<label class="blurred-label">Username*</label>', unsafe_allow_html=True)
    username = st.text_input("", key="login_username")
    st.markdown('<label class="blurred-label">Password*</label>', unsafe_allow_html=True)
    password = st.text_input("", type="password", key="login_password")

    if st.button("Log In"):
        if authenticate_user(username, password):
            st.success(f"Welcome, {username}!")
            st.session_state["authenticated_user"] = username
            st.session_state["current_page"] = "description"
        else:
            st.error("Invalid Username or Password!")

    col1, col2 = st.columns([2, 1])  # Adjust column widths
    with col1:
        st.markdown(
            '<div style="text-align: right;font-weight:bold">'
            'Forgot password ? '
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Go to Reset Password"):
            st.session_state["current_page"] = "reset_password"
    

def show_reset_password_page():
    st.markdown(
        """
        <style>
        .st-emotion-cache-ue6h4q{
            min-height: 0.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Reset Password")
    st.markdown('<label class="blurred-label">Enter your registered email</label>', unsafe_allow_html=True)
    email = st.text_input("")
    st.markdown('<label class="blurred-label">New Password</label>', unsafe_allow_html=True)
    new_password = st.text_input("", type="password",key="new_password")
    st.markdown('<label class="blurred-label">Confirm New Password</label>', unsafe_allow_html=True)
    confirm_password = st.text_input("", type="password",key="confirm_password")

    if st.button("Reset Password"):
        if new_password != confirm_password:
            st.error("Passwords do not match!")
        else:
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = c.fetchone()

            if user:
                update_password(email, new_password)
                st.success("Password reset successfully! Redirecting to login...")
                st.session_state["current_page"] = "login"
            else:
                st.error("Email not found!")

def show_description_page():
    # Apply CSS for styling
    st.markdown(
        """
        <style>
        .description-container {
            background-color: #E8F8FF; /* Mild sky blue background */
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #B3E5FC; /* Subtle border */
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); /* Soft shadow */
        }

        h2 {
            color: #01579B; /* Deep blue for headings */
        }

        p {
            color: #2E3B4E; /* Darker shade for paragraph text */
            line-height: 1.6;
        }

        .question {
            color: #1A73E8; /* Bright blue for questions */
            font-weight: bold;
        }

        .answer {
            color: #444444; /* Dark gray for answers */
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # Description container
    st.markdown('<div class="description-container">', unsafe_allow_html=True)
    st.title("Insightful Description")

    st.markdown("""
        <h2>Overview</h2>
        <p>
        This comprehensive dashboard provides an insightful analysis of air quality data across multiple stations in India. The visualizations offer detailed perspectives on key pollutants and their distribution across different locations, enabling users to explore trends and gain actionable insights.
        </p>

        <h2>Key Features</h2>
        <h3 style="color: #01579B;">1. Overall Air Quality Insights</h3>
        <p>
        - <strong style="color: #06402B;">Sum of AQI (Air Quality Index) by Station</strong>: A donut chart visualizes the cumulative AQI across stations, showcasing the contributions of various cities to air quality levels.
        - <strong style="color: #06402B;">Key Pollutant Metrics</strong>: Highlights maximum recorded values for critical pollutants such as CO (Carbon Monoxide), NO₂ (Nitrogen Dioxide), SO₂ (Sulfur Dioxide), and O₃ (Ozone).
        </p>

        <h3 style="color: #01579B;">2. Station-Specific Details</h3>
        <p>
        - <strong style="color: #06402B;">CO Quantity by Station</strong>: A bar chart presents the distribution of Carbon Monoxide emissions across different stations, helping identify hotspots with higher pollution levels.
        - <strong style="color:  #06402B;">Max of PM2.5 and PM10 by Station</strong>: The area chart tracks particulate matter (PM2.5 and PM10) peaks across cities, revealing temporal trends and critical periods of pollution.
        </p>

        <h3 style="color: #01579B;">3. Filter and Interaction Features</h3>
        <p>
        - Dynamic filters for year and city selection allow users to drill down into specific datasets, making the dashboard customizable to diverse analytical needs.
        - A map view of stations pinpoints locations geographically, offering a spatial perspective on air quality metrics.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('<h2 style="color: #01579B;">Frequently Asked Questions (FAQ)</h2>', unsafe_allow_html=True)

    # FAQ Section with Expanders
    with st.expander("Q1: How does the AQI donut chart work?"):
        st.markdown("<div class='question'>The AQI donut chart visualizes the cumulative AQI values for each station, offering a quick comparison of air quality across locations.</div>", unsafe_allow_html=True)
    
    with st.expander("Q2: Can I filter data by year or city?"):
        st.markdown("<div class='question'>Yes, you can use the dynamic filters to focus on specific years or cities and analyze the corresponding air quality data.</div>", unsafe_allow_html=True)

    with st.expander("Q3: What pollutants are monitored in this dashboard?"):
        st.markdown("<div class='question'>The dashboard monitors key pollutants such as CO, NO₂, SO₂, O₃, PM2.5, and PM10, providing a comprehensive view of air quality.</div>", unsafe_allow_html=True)

    with st.expander("Q4: Who can benefit from this dashboard?"):
        st.markdown("<div class='question'>Policymakers, environmental researchers, and citizens can use this dashboard to monitor air quality, assess trends, and make informed decisions.</div>", unsafe_allow_html=True)

    st.markdown("""
        <h2 style="color: #01579B;">Purpose and Utility</h2>
        <p>
        This dashboard is an essential tool for understanding trends and pollutants. By leveraging its insights, users can contribute to informed decision-making and the formulation of effective strategies to combat air pollution.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close the description container

    st.button("Explore the Dashboard", on_click=lambda: st.session_state.update({"current_page": "dashboard"}))

def show_dashboard_page():
    st.title("Air Pollution Dashboard")
    st.markdown("Here is my embedded Power BI dashboard:")
    
    iframe = f"""
        <iframe title="Station Day Air Pollution updated" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiZjc5MDc5NTktNGJkZi00MTdkLTkwNDItYTMxZjVmY2MzZTdlIiwidCI6ImI0NmU5ZjZlLTQyOTAtNDIzZS04NjA2LTViZWJjN2RjMDM1YyJ9" frameborder="0" allowFullScreen="true"></iframe>
    """
    st.components.v1.html(iframe, height=600)
    st.button("Back to Description", on_click=lambda: st.session_state.update({"current_page": "description"}))

    # Dataset loading and display
    excel_file = "InfosysDataset.xlsx"
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)

        # Dataset Overview
        with st.expander(" Air Pollution "):
            st.subheader("Columns in the Dataset")
            st.write(df.columns.tolist())

            st.subheader("Dataset")
            st.dataframe(df)  # Display the full dataset
    else:
        st.warning("Dataset not found.")

def logout():
    st.session_state["authenticated_user"] = None
    st.session_state["current_page"] = "login"

# ---- Main Logic ----
if st.session_state["current_page"] == "register":
    show_register_page()
elif st.session_state["current_page"] == "login":
    show_login_page()
elif st.session_state["current_page"] == "reset_password":
    show_reset_password_page()
elif st.session_state["current_page"] == "description":
    show_description_page()
elif st.session_state["current_page"] == "dashboard":
    show_dashboard_page()

# Logout button for authenticated users
if st.session_state.get("authenticated_user"):
    st.sidebar.button("Logout", on_click=logout) 