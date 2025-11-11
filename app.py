import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date
from dotenv import load_dotenv
import os
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🐾 Pet Adoption Center",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
/* ===== General Page Styling ===== */
.main {
    background: #7A1F45;
}

.stApp {
    background: #7A1F45;
}

/* ===== Headings ===== */
h1, h2, h3 {
    color: #FFFFFF;
    font-family: 'Comic Sans MS', cursive, sans-serif;
}

/* ===== Pet Cards ===== */
.pet-card {
    background: #FFFFFF;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(122, 31, 69, 0.15);
    margin: 15px 0;
    border: 1px solid rgba(122, 31, 69, 0.2);
    color: #000000;
}

/* ===== Buttons ===== */
.stButton>button {
    background-color: #7A1F45;
    color: #FFFFFFF; /* changed from white */
    border-radius: 25px;
    border: none;
    padding: 10px 28px;
    font-weight: bold;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background-color: #FFFFFF;
    color: #7A1F45; /* contrast text color on hover */
    transform: scale(1.05);
}

/* ===== Tabs ===== */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: bold;
    color: #7A1F45;
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 12px 12px 0 0;
    margin-right: 6px;
    border: 1px solid rgba(122, 31, 69, 0.2);
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #f0e1e6ff;
    color: #000000;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #edc0d9;
    color: #000000; /* changed from white */
    border-bottom: 2px solid #000000;
}

/* ===== Streamlit Input/Widget Tweaks ===== */
.stTextInput>div>div>input, 
.stSelectbox>div>div>div>div {
    border-radius: 10px;
    border: 1px solid rgba(122, 31, 69, 0.3);
    color: #FFFFFF;
}

.stTextInput>div>div>input:focus {
    border-color: #7A1F45;
    box-shadow: 0 0 0 2px rgba(122, 31, 69, 0.1);
}
</style>


""", unsafe_allow_html=True)

# Database functions
def create_connection():
    try:
        connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
)
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            st.error(f"Query error: {e}")
            return False
    return False

def fetch_data(query, params=None):
    conn = create_connection()
    if not conn:
        return pd.DataFrame()

    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Fetch all rows safely
        rows = cursor.fetchall() or []

        # Build DataFrame manually (avoids Streamlit’s auto-rendering)
        df = pd.DataFrame(rows)

        cursor.close()
        conn.close()
        return df

    except Error as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

# === MAIN APP WITH TABS ===
st.markdown("<h1 style='text-align: center; color: #ff6b6b;'>🐾 Pet Adoption Center 🐾</h1>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 Home",
    "🐶 View Pets",
    "➕ Add Pet",
    "👨‍👩‍👧 Pet Parents",
    "🏥 Medical Reports",
    "👨‍⚕️ Veterinarians",
    "🍖 Food Providers",
    "👥 Employees"
])

# === TAB 1: HOME ===
with tab1:
    st.markdown("### Find your perfect furry friend today! 💕")

    col1, col2, col3 = st.columns(3)

    def safe_count(query):
        df = fetch_data(query)
        if df is not None and not df.empty and 'count' in df.columns:
            return int(df['count'].iloc[0])
        return 0

    pets_count = safe_count("SELECT COUNT(*) as count FROM pets")
    parents_count = safe_count("SELECT COUNT(*) as count FROM pet_parent")
    vets_count = safe_count("SELECT COUNT(*) as count FROM vet")

    with col1:
        st.metric("🐾 Available Pets", pets_count)
    with col2:
        st.metric("👨‍👩‍👧 Happy Families", parents_count)
    with col3:
        st.metric("👨‍⚕️ Veterinarians", vets_count)

    # This ensures no extra 'None' is rendered
    st.empty()

    st.image(
        r"C:\Users\Sucheta\OneDrive\Desktop\DBMS Course Project\dog.jpg",
        use_column_width=True,
        caption="Adopt, Don't Shop! 🐕💖"
    )


# === TAB 2: VIEW PETS ===
with tab2:
    st.markdown("## 🐶 Available Pets for Adoption")
    
    col1, col2 = st.columns(2)
    with col1:
        pet_type_filter = st.selectbox("Filter by Type", ["All", "Dog", "Cat", "Bird"], key="type_filter")
    with col2:
        gender_filter = st.selectbox("Filter by Gender", ["All", "Male", "Female"], key="gender_filter")
    
    query = "SELECT * FROM pets WHERE 1=1"
    if pet_type_filter != "All":
        query += f" AND pet_type = %s"
    if gender_filter != "All":
        query += f" AND pet_gender = %s"
    
    params = []
    if pet_type_filter != "All": params.append(pet_type_filter)
    if gender_filter != "All": params.append(gender_filter)
    
    pets_df = fetch_data(query, tuple(params)) if params else fetch_data(query)
    
    if not pets_df.empty:
        for _, pet in pets_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.markdown("🐕" if pet['pet_type'] == 'Dog' else "🐱" if pet['pet_type'] == 'Cat' else "🦜")
                with col2:
                    st.markdown(f"### {pet['pet_name']}")
                    st.write(f"**Breed:** {pet['pet_breed']} | **Type:** {pet['pet_type']}")
                    st.write(f"**Gender:** {pet['pet_gender']} | **Color:** {pet['pet_color']}")
                    st.write(f"**Date of Birth:** {pet['pet_dob']}")
                with col3:
                    if st.button(f"Adopt {pet['pet_name']}", key=f"adopt_{pet['pet_id']}"):
                        st.success(f"Interested in adopting {pet['pet_name']}! 💕")
                st.divider()
    else:
        st.info("No pets found matching your criteria.")

# === TAB 3: ADD NEW PET ===
with tab3:
    st.markdown("## ➕ Add New Pet to Database")
    
    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            pet_id = st.number_input("Pet ID", min_value=1, step=1, key="add_pet_id")
            pet_name = st.text_input("Pet Name", key="add_pet_name")
            pet_type = st.selectbox("Pet Type", ["Dog", "Cat", "Bird", "Other"], key="add_pet_type")
            pet_breed = st.text_input("Breed", key="add_pet_breed")
        with col2:
            pet_dob = st.date_input("Date of Birth", max_value=date.today(), key="add_pet_dob")
            pet_gender = st.selectbox("Gender", ["Male", "Female"], key="add_pet_gender")
            pet_color = st.text_input("Color", key="add_pet_color")
        
        submit = st.form_submit_button("🐾 Add Pet")
        if submit:
            query = """INSERT INTO pets (pet_id, pet_name, pet_type, pet_breed, pet_dob, pet_gender, pet_color) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (pet_id, pet_name, pet_type, pet_breed, pet_dob, pet_gender, pet_color)
            if execute_query(query, params):
                st.success(f"✅ {pet_name} has been added successfully!")
                st.rerun()
            else:
                st.error("Failed to add pet. Check if Pet ID already exists.")

# === TAB 4: PET PARENTS ===
with tab4:
    st.markdown("## 👨‍👩‍👧 Pet Parents Directory")
    
    parents_df = fetch_data("""
        SELECT pp.*, p.pet_name 
        FROM pet_parent pp
        LEFT JOIN pets p ON pp.pp_pet_id = p.pet_id
    """)
    
    if not parents_df.empty:
        st.dataframe(parents_df, use_container_width=True)
    else:
        st.info("No pet parents registered yet.")
    
    st.markdown("### Add New Pet Parent")
    with st.form("add_parent_form"):
        col1, col2 = st.columns(2)
        with col1:
            pp_id = st.number_input("Parent ID", min_value=1, step=1, key="pp_id")
            pp_fname = st.text_input("First Name", key="pp_fname")
            pp_lname = st.text_input("Last Name", key="pp_lname")
            pp_phone = st.text_input("Phone Number", key="pp_phone")
        with col2:
            pets_list = fetch_data("SELECT pet_id, pet_name FROM pets")
            pet_options = {f"{row['pet_name']} (ID: {row['pet_id']})": row['pet_id'] 
                          for _, row in pets_list.iterrows()} if not pets_list.empty else {}
            selected_pet = st.selectbox("Select Pet", options=list(pet_options.keys()), key="pp_pet")
            pp_experience = st.text_area("Pet Experience", key="pp_exp")
            pp_address = st.text_input("Address", key="pp_addr")
        
        if st.form_submit_button("Add Pet Parent"):
            if pet_options:
                query = """INSERT INTO pet_parent (pp_id, pp_fname, pp_lname, pp_pet_id, pp_phone, pp_pet_experience, pp_address)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params = (pp_id, pp_fname, pp_lname, pet_options[selected_pet], pp_phone, pp_experience, pp_address)
                if execute_query(query, params):
                    st.success("Parent added successfully!")
                    st.rerun()
            else:
                st.error("No pets available to assign.")

# === TAB 5: MEDICAL REPORTS ===
# === TAB 5: MEDICAL REPORTS ===
with tab5:
    st.markdown("## 🏥 Medical Reports")

    # --- Fetch and display reports ---
    reports_df = fetch_data("""
        SELECT mr.*, p.pet_name, v.vet_name 
        FROM medical_report mr
        LEFT JOIN pets p ON mr.mr_pet_id = p.pet_id
        LEFT JOIN vet v ON mr.mr_vet_id = v.vet_id
        ORDER BY mr.report_date DESC
    """)

    if not reports_df.empty:
        st.dataframe(reports_df, use_container_width=True)
    else:
        st.info("No medical reports available.")

    st.markdown("---")

    # --- Add New Medical Report ---
    st.markdown("### ➕ Add New Medical Report")
    with st.form("add_report_form"):
        report_id = st.number_input("Report ID", min_value=1, step=1, key="report_id")

        # Fetch pets
        pets_list = fetch_data("SELECT pet_id, pet_name FROM pets")
        pet_dict = {f"{row['pet_name']} (ID: {row['pet_id']})": row['pet_id'] for _, row in pets_list.iterrows()} if not pets_list.empty else {}
        selected_pet = st.selectbox("Select Pet", options=list(pet_dict.keys()), key="report_pet")

        # Fetch vets
        vet_list = fetch_data("SELECT vet_id, vet_name FROM vet")
        vet_dict = {f"{row['vet_name']} (ID: {row['vet_id']})": row['vet_id'] for _, row in vet_list.iterrows()} if not vet_list.empty else {}
        selected_vet = st.selectbox("Select Veterinarian", options=list(vet_dict.keys()), key="report_vet")

        report_date = st.date_input("Report Date", value=date.today(), key="report_date")
        diagnosis = st.text_area("Diagnosis", key="diagnosis")

        if st.form_submit_button("✅ Add Report"):
            if pet_dict and vet_dict:
                query = """
                    INSERT INTO medical_report (report_id, mr_pet_id, mr_vet_id, report_date, diagnosis)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = (report_id, pet_dict[selected_pet], vet_dict[selected_vet], report_date, diagnosis)
                if execute_query(query, params):
                    st.success("✅ Medical report added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add medical report.")
            else:
                st.error("Please ensure pets and vets exist in the database.")

    st.markdown("---")

    # --- Delete Medical Report ---
    if not reports_df.empty:
        st.markdown("### 🗑️ Delete Medical Report")
        col1, col2 = st.columns([3, 1])
        with col1:
            report_to_delete = st.selectbox(
                "Select Report to Delete",
                options=reports_df['report_id'].tolist(),
                format_func=lambda x: f"Report ID: {x} - {reports_df[reports_df['report_id']==x]['pet_name'].values[0]} ({reports_df[reports_df['report_id']==x]['report_date'].values[0]})",
                key="delete_report"
            )
        with col2:
            if st.button("🗑️ Delete Report", key="delete_report_btn"):
                query = "DELETE FROM medical_report WHERE report_id = %s"
                if execute_query(query, (report_to_delete,)):
                    st.success(f"✅ Report ID {report_to_delete} deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete report.")
    else:
        st.info("No reports to delete.")




# === TAB 6: VETERINARIANS ===
with tab6:
    st.markdown("## 👨‍⚕️ Our Veterinarians")
    
    vets_df = fetch_data("SELECT * FROM vet")
    
    if not vets_df.empty:
        for _, vet in vets_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {vet['vet_name']}")
                    st.write(f"**Qualification:** {vet['vet_qualification']}")
                    st.write(f"**Experience:** {vet['vet_exp']} years")
                    st.write(f"**Phone:** {vet['vet_phone']}")
                with col2:
                    st.markdown("👨‍⚕️")
                st.divider()
    else:
        st.info("No veterinarians registered.")

# === TAB 7: FOOD PROVIDERS ===
with tab7:
    st.markdown("## 🍖 Food Providers")
    
    providers_df = fetch_data("SELECT * FROM food_providers")
    
    if not providers_df.empty:
        st.dataframe(providers_df, use_container_width=True)
    else:
        st.info("No food providers registered.")

# === TAB 8: EMPLOYEES ===
with tab8:
    st.markdown("## 👥 Our Team")
    
    employees_df = fetch_data("SELECT * FROM employees")
    
    if not employees_df.empty:
        st.dataframe(employees_df, use_container_width=True)
    else:
        st.info("No employees registered.")

# === SIDEBAR (Optional Branding) ===

with st.sidebar:
    st.image(r"C:\Users\Sucheta\OneDrive\Desktop\DBMS Course Project\cat.jpg", use_column_width=True)
    st.markdown("---")
    st.markdown("### 💕 Made with love for pets")
    st.markdown("🐾 Pet Adoption Center © 2025")
    st.markdown("---")
    