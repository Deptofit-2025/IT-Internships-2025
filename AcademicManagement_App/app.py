# app.py
import streamlit as st

# MUST BE FIRST AND ONLY Streamlit command
st.set_page_config(
    page_title="Academic Manager",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

def main():
    try:
        # Initialize database
        from database import db
        db.init_db()
        
        # Import other modules AFTER db initialization
        from management import dashboard as m_dashboard
        from teachers import dashboard as t_dashboard
        from parents import dashboard as p_dashboard

        # UI Components
        st.sidebar.title("Academic Manager")
        module = st.sidebar.radio(
            "Choose Module",
            ["Management", "Teachers", "Parents"],
            label_visibility="collapsed"
        )

        # Module routing
        if module == "Management":
            m_dashboard.show()
        elif module == "Teachers":
            t_dashboard.show()
        elif module == "Parents":
            p_dashboard.show()

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()