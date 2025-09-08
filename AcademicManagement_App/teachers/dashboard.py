import streamlit as st
import pandas as pd
import json
import os
import calendar
from datetime import datetime, timedelta
import uuid
from streamlit_option_menu import option_menu
import hashlib

# ======================
# DATA MANAGEMENT
# ======================

DATA_DIR = "data"
# Ensure data directory and sub-directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "attachments"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "leave_attachments"), exist_ok=True)

TEACHER_DATA_FILE = os.path.join(DATA_DIR, "teacher_data.json")
STUDENT_DATA_FILE = os.path.join(DATA_DIR, "student_data.json")
ATTENDANCE_DATA_FILE = os.path.join(DATA_DIR, "attendance_data.json")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
PERFORMANCE_DATA_FILE = os.path.join(DATA_DIR, "performance_data.json")
TIMETABLE_DATA_FILE = os.path.join(DATA_DIR, "timetable_data.json")
MESSAGES_DATA_FILE = os.path.join(DATA_DIR, "messages_data.json")
RESOURCES_DATA_FILE = os.path.join(DATA_DIR, "resources_data.json")
LEAVE_DATA_FILE = os.path.join(DATA_DIR, "leave_data.json")
ORDERS_DATA_FILE = os.path.join(DATA_DIR, "orders_data.json")

# Grade levels and sections for sample data generation
GRADE_LEVELS = ["Nursery", "LKG", "UKG"] + [f"Grade {i}" for i in range(1, 11)]
CLASS_SECTIONS = ["A", "B", "C", "D"]
COMMON_SUBJECTS = ["Mathematics", "Science", "English", "History", "Geography", "Computer Science", "Arts", "Physical Education", "Other"]

# ======================
# HELPER FUNCTIONS
# ======================

def load_data(filename, default_value={}):
    """Load data from JSON file, returning a default value if file is empty or corrupted."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                content = f.read()
                if content:
                    return json.loads(content)
                else:
                    return default_value
            except json.JSONDecodeError:
                st.warning(f"Error decoding JSON from {filename}. File might be corrupted. Re-initializing with default value.")
                return default_value
    return default_value

def save_data(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_orders():
    """Load orders data from file."""
    return load_data(ORDERS_DATA_FILE, default_value={})

def save_orders(data):
    """Save orders data to file."""
    save_data(data, ORDERS_DATA_FILE)

def hash_password(password):
    """Hash a password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_full_class_list():
    """Generate a list of all possible classes"""
    classes = []
    for grade in GRADE_LEVELS:
        if grade in ["Nursery", "LKG", "UKG"]:
            classes.append(grade)
        else:
            for section in CLASS_SECTIONS:
                classes.append(f"{grade}{section}")
    return classes

def get_students_by_class(class_name):
    """Return a list of student records for a given class."""
    student_data = load_data(STUDENT_DATA_FILE, default_value={})
    return student_data.get(class_name, [])

# ======================
# TEACHER MODULE
# ======================

def teacher_module():
    """Main teacher dashboard function"""
    # This code assumes a teacher is already logged in for simplicity,
    # and directly displays the dashboard to fix the blank screen issue.
    # We will use a mock teacher ID for demonstration.
    
    # Check if a teacher ID is already in session state (for continuity)
    if 'teacher_id' not in st.session_state:
        # If not, create a mock teacher data entry and set the session state.
        # This bypasses the login and ensures the page always loads.
        teacher_id = str(uuid.uuid4())
        mock_teacher_data = {
            teacher_id: {
                "id": teacher_id,
                "name": "Jane Doe",
                "subject": "Mathematics",
                "email": "jane.doe@example.com",
                "phone": "123-456-7890",
                "join_date": "2020-09-01",
                "is_admin": False,
                "username": "janedoe",
                "password": hash_password("password123") # Mock password
            }
        }
        all_teachers = load_data(TEACHER_DATA_FILE, default_value={})
        all_teachers.update(mock_teacher_data)
        save_data(all_teachers, TEACHER_DATA_FILE)
        
        st.session_state['teacher_id'] = teacher_id
        st.session_state['teacher_data'] = mock_teacher_data[teacher_id]
        st.session_state['logged_in'] = True
    
    teacher_id = st.session_state['teacher_id']
    teacher_data = st.session_state['teacher_data']
    
    st.title(f"👨‍🏫 Teacher Dashboard - {teacher_data.get('name', '')}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
    
    # Navigation menu
    selected = option_menu(
        None,
        ["Profile", "Attendance", "Assignments", "Timetable", "Student Management", 
         "Performance", "Communication", "Resources", "Leave", "Export Data", "School Essentials"],
        icons=['person', 'calendar-check', 'journal-text', 'calendar-range', 'people', 
               'graph-up', 'chat', 'folder', 'clock', 'download', 'bag'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
            "nav-link-selected": {"background-color": "#0d6efd"},
        }
    )

    # Profile Section
    if selected == "Profile":
        st.header("👤 Teacher Profile")
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        
        with col2:
            st.write(f"**Name:** {teacher_data.get('name', '')}")
            st.write(f"**Subject:** {teacher_data.get('subject', '')}")
            st.write(f"**Email:** {teacher_data.get('email', '')}")
            st.write(f"**Phone:** {teacher_data.get('phone', '')}")
            st.write(f"**Joined:** {teacher_data.get('join_date', '')}")
            
            with st.expander("Update Profile"):
                with st.form("update_profile"):
                    new_email = st.text_input("Email", value=teacher_data.get('email', ''))
                    new_phone = st.text_input("Phone", value=teacher_data.get('phone', ''))
                    new_password = st.text_input("New Password (leave blank to keep current)", type="password")
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        teacher_data['email'] = new_email
                        teacher_data['phone'] = new_phone
                        if new_password:
                            teacher_data['password'] = hash_password(new_password)
                        
                        all_data = load_data(TEACHER_DATA_FILE)
                        all_data[str(teacher_id)] = teacher_data
                        save_data(all_data, TEACHER_DATA_FILE)
                        st.success("Profile updated successfully")
                        st.rerun()

    # Attendance Section
    elif selected == "Attendance":
        st.header("📅 Attendance Tracking")
        
        today = datetime.today()
        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.selectbox("Year", range(today.year-1, today.year+2), index=1)
        with col2:
            month_name = st.selectbox("Month", list(calendar.month_name[1:]), index=today.month-1)
            month = list(calendar.month_name).index(month_name)
        with col3:
            day = st.selectbox("Day", range(1, 32), index=today.day-1)
        
        selected_date = f"{year}-{month:02d}-{day:02d}"
        selected_class = st.selectbox("Select Class", get_full_class_list())
        
        students = get_students_by_class(selected_class)
        attendance_data = load_data(ATTENDANCE_DATA_FILE).get(str(teacher_id), {})
        
        if selected_date not in attendance_data:
            attendance_data[selected_date] = {}
        if selected_class not in attendance_data[selected_date]:
            attendance_data[selected_date][selected_class] = {str(s['id']): "Present" for s in students}
        
        attendance_status = {}
        for student in students:
            current_status = attendance_data[selected_date][selected_class].get(str(student['id']), "Present")
            status = st.radio(
                f"{student.get('name', 'N/A')} (Adm No: {student.get('admission_no', 'N/A')})",
                ["Present", "Absent", "Late", "Excused"],
                index=["Present", "Absent", "Late", "Excused"].index(current_status),
                key=f"att_{student['id']}_{selected_date}",
                horizontal=True
            )
            attendance_status[str(student['id'])] = status
        
        if st.button("Save Attendance"):
            attendance_data[selected_date][selected_class] = attendance_status
            all_data = load_data(ATTENDANCE_DATA_FILE)
            all_data[str(teacher_id)] = attendance_data
            save_data(all_data, ATTENDANCE_DATA_FILE)
            st.success("Attendance saved successfully!")
            
            present_count = list(attendance_status.values()).count("Present")
            absent_count = list(attendance_status.values()).count("Absent")
            st.metric("Present", present_count)
            st.metric("Absent", absent_count)

    # Student Management Section
    elif selected == "Student Management":
        st.header("👥 Student Management")
        
        tab1, tab2, tab3 = st.tabs(["Add Student", "Manage Students", "Bulk Operations"])
        
        with tab1:
            with st.form("add_student", clear_on_submit=True):
                st.subheader("Add New Student")
                col1, col2 = st.columns(2)
                with col1:
                    student_admission_no = st.text_input("Student Admission Number*", help="Unique admission number for the student.").strip()
                    name = st.text_input("Full Name*", help="Full legal name of the student.").strip()
                    roll_no = st.text_input("Roll No.", help="Student's roll number in class (optional).").strip()
                    class_name = st.selectbox("Class*", get_full_class_list())
                    dob = st.date_input("Date of Birth*", max_value=datetime.today().date())
                    date_of_joining = st.date_input("Date of Joining*", max_value=datetime.today().date())
                    date_of_tc = st.date_input("Date of TC (Optional)", value=None, help="Date of Transfer Certificate issuance, if applicable.")
                with col2:
                    adhar_number = st.text_input("Aadhar Number (Optional)").strip()
                    father_name = st.text_input("Father's Name*").strip()
                    mother_name = st.text_input("Mother's Name*").strip()
                    parent_email = st.text_input("Parent Email*").strip()
                    parent_phone = st.text_input("Parent Phone*").strip()
                    address = st.text_area("Address").strip()
                    emergency_contact = st.text_input("Emergency Contact (Name & Number)*").strip()
                    contact_number = st.text_input("Student's Contact Number (Optional)").strip()
                    blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
                    financial_status = st.text_input("Financial Status (e.g., Paid, Scholarship, Partial)").strip()
                    passport_photo = st.file_uploader("Upload Passport Photo (Optional)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Add Student"):
                    required_fields = [student_admission_no, name, class_name, dob, date_of_joining, father_name, mother_name, parent_email, parent_phone, emergency_contact]
                    if not all(required_fields):
                        st.error("Please fill all required fields (*)")
                    else:
                        student_data = load_data(STUDENT_DATA_FILE)
                        
                        admission_exists = False
                        for cls_students in student_data.values():
                            if any(s.get('admission_no') == student_admission_no for s in cls_students):
                                admission_exists = True
                                break
                        
                        if admission_exists:
                            st.error(f"Student Admission Number '{student_admission_no}' already exists. Please use a unique admission number.")
                        else:
                            if class_name not in student_data:
                                student_data[class_name] = []

                            photo_path = None
                            if passport_photo:
                                photo_filename = f"student_photo_{student_admission_no}_{passport_photo.name}"
                                photo_save_path = os.path.join(DATA_DIR, "attachments", photo_filename)
                                try:
                                    with open(photo_save_path, "wb") as f:
                                        f.write(passport_photo.getbuffer())
                                    photo_path = photo_save_path
                                except Exception as e:
                                    st.error(f"Error saving photo: {e}")
                                    photo_path = None

                            new_student_record = {
                                "id": str(uuid.uuid4()),
                                "admission_no": student_admission_no,
                                "name": name,
                                "roll_no": roll_no,
                                "class": class_name,
                                "dob": str(dob),
                                "date_of_joining": str(date_of_joining),
                                "date_of_tc": str(date_of_tc) if date_of_tc else None,
                                "adhar_number": adhar_number,
                                "father_name": father_name,
                                "mother_name": mother_name,
                                "parent_name": father_name,
                                "parent_email": parent_email,
                                "parent_phone": parent_phone,
                                "address": address,
                                "emergency_contact": emergency_contact,
                                "contact_number": contact_number,
                                "blood_group": blood_group,
                                "financial_status": financial_status,
                                "passport_photo_path": photo_path
                            }
                            student_data[class_name].append(new_student_record)
                            save_data(student_data, STUDENT_DATA_FILE)
                            st.success(f"Student '{name}' (Admission No: {student_admission_no}) added successfully to {class_name}!")
                            st.rerun()
        
        with tab2:
            st.subheader("Manage Existing Students")
            student_data = load_data(STUDENT_DATA_FILE)
            
            all_students_list = []
            for class_name_key, students_in_class in student_data.items():
                for student in students_in_class:
                    all_students_list.append({**student, "class_name_display": class_name_key})

            if not all_students_list:
                st.info("No student records available.")
                return

            df_students = pd.DataFrame(all_students_list)
            display_columns = [
                "admission_no", "name", "roll_no", "class_name_display", "dob", "date_of_joining",
                "father_name", "mother_name", "parent_email", "parent_phone", "contact_number",
                "emergency_contact", "blood_group", "financial_status"
            ]
            st.dataframe(df_students[display_columns], use_container_width=True)

            st.subheader("Edit or Delete Student")
            
            student_admission_numbers = [s['admission_no'] for s in all_students_list if 'admission_no' in s]
            student_to_manage_admission_no = st.selectbox(
                "Select Student by Admission Number to Edit/Delete",
                [""] + student_admission_numbers,
                key="edit_delete_student_admission_no_teacher"
            )

            selected_student_obj = None
            if student_to_manage_admission_no:
                for cls_students in student_data.values():
                    for s in cls_students:
                        if s.get('admission_no') == student_to_manage_admission_no:
                            selected_student_obj = s
                            break
                    if selected_student_obj:
                        break

            if selected_student_obj:
                st.write(f"**Selected Student:** {selected_student_obj['name']} (Admission No: {selected_student_obj['admission_no']}) in {selected_student_obj['class']}")

                action = st.radio("Choose Action", ["Edit", "Delete"], key="student_action_radio_teacher")

                if action == "Edit":
                    st.subheader(f"Edit Details for {selected_student_obj['name']}")
                    with st.form(f"edit_student_form_{selected_student_obj['id']}"):
                        col1_edit, col2_edit = st.columns(2)
                        with col1_edit:
                            new_name = st.text_input("Full Name", value=selected_student_obj.get('name', ''))
                            new_roll_no = st.text_input("Roll No.", value=selected_student_obj.get('roll_no', ''))
                            new_dob = st.date_input("Date of Birth", value=datetime.strptime(selected_student_obj['dob'], '%Y-%m-%d').date())
                            new_date_of_joining = st.date_input("Date of Joining", value=datetime.strptime(selected_student_obj.get('date_of_joining', str(datetime.today().date())), '%Y-%m-%d').date())
                            new_date_of_tc = st.date_input("Date of TC (Optional)", value=datetime.strptime(selected_student_obj['date_of_tc'], '%Y-%m-%d').date() if selected_student_obj.get('date_of_tc') else None)
                            new_adhar_number = st.text_input("Aadhar Number (Optional)", value=selected_student_obj.get('adhar_number', ''))
                            new_contact_number = st.text_input("Student's Contact Number (Optional)", value=selected_student_obj.get('contact_number', ''))
                        with col2_edit:
                            new_parent_name = st.text_input("Parent/Guardian Name", value=selected_student_obj.get('parent_name', ''))
                            new_father_name = st.text_input("Father's Name", value=selected_student_obj.get('father_name', ''))
                            new_mother_name = st.text_input("Mother's Name", value=selected_student_obj.get('mother_name', ''))
                            new_parent_email = st.text_input("Parent Email", value=selected_student_obj.get('parent_email', ''))
                            new_parent_phone = st.text_input("Parent Phone", value=selected_student_obj.get('parent_phone', ''))
                            new_address = st.text_area("Address", value=selected_student_obj.get('address', ''))
                            new_emergency_contact = st.text_input("Emergency Contact (Name & Number)", value=selected_student_obj.get('emergency_contact', ''))
                            new_blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(selected_student_obj.get('blood_group', 'Unknown')))
                            new_financial_status = st.text_input("Financial Status", value=selected_student_obj.get('financial_status', ''))
                            
                            current_photo_path = selected_student_obj.get('passport_photo_path')
                            if current_photo_path and os.path.exists(current_photo_path):
                                st.image(current_photo_path, caption="Current Passport Photo", width=150)
                                st.info("Upload a new photo to replace the current one.")
                            new_passport_photo = st.file_uploader("Upload New Passport Photo (Optional)", type=["jpg", "jpeg", "png"], key=f"edit_photo_{selected_student_obj['id']}_teacher")

                        if st.form_submit_button("Save Changes"):
                            student_data_to_update = None
                            for i, cls_students in enumerate(student_data.values()):
                                for j, s in enumerate(cls_students):
                                    if s.get('id') == selected_student_obj['id']:
                                        student_data_to_update = student_data[selected_student_obj['class']][j]
                                        break
                                if student_data_to_update:
                                    break

                            if student_data_to_update:
                                student_data_to_update.update({
                                    "name": new_name,
                                    "roll_no": new_roll_no,
                                    "dob": str(new_dob),
                                    "date_of_joining": str(new_date_of_joining),
                                    "date_of_tc": str(new_date_of_tc) if new_date_of_tc else None,
                                    "adhar_number": new_adhar_number,
                                    "parent_name": new_parent_name,
                                    "father_name": new_father_name,
                                    "mother_name": new_mother_name,
                                    "parent_email": new_parent_email,
                                    "parent_phone": new_parent_phone,
                                    "address": new_address,
                                    "emergency_contact": new_emergency_contact,
                                    "contact_number": new_contact_number,
                                    "blood_group": new_blood_group,
                                    "financial_status": new_financial_status
                                })
                                if new_passport_photo:
                                    photo_filename = f"student_photo_{selected_student_obj['admission_no']}_{new_passport_photo.name}"
                                    photo_save_path = os.path.join(DATA_DIR, "attachments", photo_filename)
                                    try:
                                        with open(photo_save_path, "wb") as f:
                                            f.write(new_passport_photo.getbuffer())
                                        student_data_to_update["passport_photo_path"] = photo_save_path
                                    except Exception as e:
                                        st.error(f"Error saving new photo: {e}")

                                save_data(student_data, STUDENT_DATA_FILE)
                                st.success("Student details updated successfully!")
                                st.rerun()
                            else:
                                st.error("Error: Student not found in data for update.")

                elif action == "Delete":
                    st.warning(f"Are you sure you want to delete {selected_student_obj['name']} (Admission No: {selected_student_obj['admission_no']})?")
                    if st.button("Confirm Delete", key=f"confirm_delete_{selected_student_obj['id']}_teacher"):
                        original_class = selected_student_obj['class']
                        if original_class in student_data:
                            student_data[original_class] = [
                                s for s in student_data[original_class]
                                if s['id'] != selected_student_obj['id']
                            ]
                            if not student_data[original_class]:
                                del student_data[original_class]

                        save_data(student_data, STUDENT_DATA_FILE)
                        st.success("Student deleted successfully!")
                        st.rerun()
            else:
                st.info("Please select a student by Admission Number to manage.")
        
        with tab3:
            st.subheader("Bulk Student Operations")
            
            with st.expander("Import Students from CSV"):
                uploaded_file = st.file_uploader("Choose CSV file", type="csv", key="bulk_import_students_teacher")
                if uploaded_file:
                    try:
                        df = pd.read_csv(uploaded_file)
                        st.write("Preview:")
                        st.dataframe(df.head())
                        
                        if st.button("Import Students", key="import_students_btn_teacher"):
                            student_data = load_data(STUDENT_DATA_FILE)
                            imported_count = 0
                            for _, row in df.iterrows():
                                class_name = row.get('class', 'Unknown Class')
                                if class_name not in student_data:
                                    student_data[class_name] = []
                                
                                admission_no = row.get('admission_no', str(uuid.uuid4()))
                                if any(s.get('admission_no') == admission_no for cls_students in student_data.values() for s in cls_students):
                                    st.warning(f"Skipping student with duplicate Admission No: {admission_no}")
                                    continue

                                photo_path = None
                                if row.get('passport_photo_path') and os.path.exists(row['passport_photo_path']):
                                    photo_path = row['passport_photo_path']

                                student_data[class_name].append({
                                    "id": str(uuid.uuid4()),
                                    "admission_no": admission_no,
                                    "name": row.get('name', 'New Student'),
                                    "roll_no": str(row.get('roll_no', '')),
                                    "class": class_name,
                                    "dob": str(row.get('dob', '2000-01-01')),
                                    "date_of_joining": str(row.get('date_of_joining', '2023-01-01')),
                                    "date_of_tc": str(row.get('date_of_tc', None)) if pd.notna(row.get('date_of_tc')) else None,
                                    "adhar_number": str(row.get('adhar_number', '')),
                                    "father_name": row.get('father_name', 'N/A'),
                                    "mother_name": row.get('mother_name', 'N/A'),
                                    "parent_name": row.get('parent_name', row.get('father_name', 'N/A')),
                                    "parent_email": row.get('parent_email', ''),
                                    "parent_phone": row.get('parent_phone', ''),
                                    "address": row.get('address', ''),
                                    "emergency_contact": row.get('emergency_contact', ''),
                                    "contact_number": str(row.get('contact_number', '')),
                                    "blood_group": row.get('blood_group', 'Unknown'),
                                    "financial_status": row.get('financial_status', 'N/A'),
                                    "passport_photo_path": photo_path
                                })
                                imported_count += 1
                            
                            save_data(student_data, STUDENT_DATA_FILE)
                            st.success(f"Imported {imported_count} students successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error reading or importing CSV file: {e}")
            
            with st.expander("Export Students to CSV"):
                if st.button("Generate Export File", key="export_students_btn_teacher"):
                    student_data = load_data(STUDENT_DATA_FILE)
                    all_students = []
                    for class_name, students in student_data.items():
                        for student in students:
                            all_students.append(student)
                    
                    if all_students:
                        df = pd.DataFrame(all_students)
                        expected_columns = [
                            "id", "admission_no", "name", "roll_no", "class", "dob",
                            "date_of_joining", "date_of_tc", "adhar_number", "father_name",
                            "mother_name", "parent_name", "parent_email", "parent_phone",
                            "address", "emergency_contact", "contact_number", "blood_group",
                            "financial_status", "passport_photo_path"
                        ]
                        for col in expected_columns:
                            if col not in df.columns:
                                df[col] = None

                        csv = df[expected_columns].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Students Data (CSV)",
                            csv,
                            "students_export.csv",
                            "text/csv"
                        )
                    else:
                        st.warning("No student data to export")

    # Timetable Section
    elif selected == "Timetable":
        st.header("📅 Class Timetable")
        
        tab1, tab2, tab3 = st.tabs(["View Timetable", "Edit Timetable", "Timetable Analytics"])
        
        with tab1:
            timetable_data = load_data(TIMETABLE_DATA_FILE).get(str(teacher_id), [])
            
            if not timetable_data:
                st.info("No timetable entries found")
            else:
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                periods = range(1, 8)
                
                timetable_grid = {day: {f"Period {period}": "" for period in periods} for day in days}
                
                for entry in timetable_data:
                    day = entry.get('day', 'N/A')
                    period = entry.get('period', 'N/A')
                    if day in timetable_grid and f"Period {period}" in timetable_grid[day]:
                        timetable_grid[day][f"Period {period}"] = f"{entry.get('subject', 'N/A')}\n{entry.get('class_name', 'N/A')}"
                
                df = pd.DataFrame(timetable_grid)
                st.dataframe(df.style.applymap(lambda x: 'background-color: #e6f3ff' if x else ''))
        
        with tab2:
            st.subheader("Edit Timetable")
            timetable_data = load_data(TIMETABLE_DATA_FILE).get(str(teacher_id), [])
            
            with st.form("timetable_entry"):
                col1, col2 = st.columns(2)
                with col1:
                    day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
                    period = st.number_input("Period", min_value=1, max_value=7, value=1)
                    subject = st.text_input("Subject", value=teacher_data.get('subject', ''))
                with col2:
                    class_name = st.selectbox("Class", get_full_class_list())
                    action = st.radio("Action", ["Add/Update", "Delete"])
                
                submitted = st.form_submit_button("Submit")
                if submitted:
                    entry = {
                        "day": day,
                        "period": period,
                        "subject": subject,
                        "class_name": class_name
                    }
                    if action == "Add/Update":
                        timetable_data = [e for e in timetable_data if not (e.get('day') == day and e.get('period') == period)]
                        timetable_data.append(entry)
                        st.success("Timetable entry updated!")
                    else:
                        timetable_data = [e for e in timetable_data if not (e.get('day') == day and e.get('period') == period and e.get('class_name') == class_name)]
                        st.success("Timetable entry deleted!")
                    all_data = load_data(TIMETABLE_DATA_FILE)
                    all_data[str(teacher_id)] = timetable_data
                    save_data(all_data, TIMETABLE_DATA_FILE)
                    st.rerun()
        
        with tab3:
            st.subheader("Timetable Analytics")
            timetable_data = load_data(TIMETABLE_DATA_FILE).get(str(teacher_id), [])
            if not timetable_data:
                st.info("No timetable data available")
            else:
                df = pd.DataFrame(timetable_data)
                teaching_hours = df['day'].value_counts().sort_index()
                st.bar_chart(teaching_hours, use_container_width=True)
                class_dist = df['class_name'].value_counts()
                st.write("**Classes Taught:**")
                st.dataframe(class_dist)
    
    # Assignments Section
    elif selected == "Assignments":
        st.header("📝 Assignments & Grading")
        tab1, tab2, tab3 = st.tabs(["Create Assignment", "Grade Submissions", "Assignment Analytics"])
        
        assignments_data = load_data(ASSIGNMENTS_DATA_FILE).get(str(teacher_id), [])

        with tab1:
            with st.form("create_assignment", clear_on_submit=True):
                st.subheader("Create New Assignment")
                title = st.text_input("Assignment Title*")
                description = st.text_area("Description")
                due_date = st.date_input("Due Date*", min_value=datetime.today())
                assigned_class = st.selectbox("Assign to Class*", get_full_class_list())
                max_score = st.number_input("Maximum Score*", min_value=1, value=100)
                assignment_type = st.selectbox("Type", ["Homework", "Project", "Quiz", "Test"])
                
                if st.form_submit_button("Create Assignment"):
                    if not all([title, due_date, assigned_class, max_score]):
                        st.error("Please fill all required fields (*)")
                    else:
                        new_assignment = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "description": description,
                            "due_date": str(due_date),
                            "assigned_class": assigned_class,
                            "max_score": max_score,
                            "type": assignment_type,
                            "created_date": str(datetime.today().date()),
                            "submissions": []
                        }
                        assignments_data.append(new_assignment)
                        all_data = load_data(ASSIGNMENTS_DATA_FILE)
                        all_data[str(teacher_id)] = assignments_data
                        save_data(all_data, ASSIGNMENTS_DATA_FILE)
                        st.success("Assignment created successfully!")
                        st.rerun()

        with tab2:
            st.subheader("Grade Student Submissions")
            if not assignments_data:
                st.info("No assignments created yet")
            else:
                selected_assignment = st.selectbox(
                    "Select Assignment",
                    assignments_data,
                    format_func=lambda a: f"{a.get('title', 'Untitled')} - {a.get('assigned_class', 'N/A')} (Due: {a.get('due_date', 'N/A')})"
                )
                
                if not selected_assignment.get('submissions', []):
                    st.info("No submissions for this assignment yet")
                else:
                    for sub in selected_assignment['submissions']:
                        with st.expander(f"Submission by {sub.get('student_name', 'N/A')} (ID: {sub.get('student_id', 'N/A')})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Submitted on:** {sub.get('submission_date', 'N/A')}")
                                st.write(f"**Status:** {sub.get('status', 'Submitted')}")
                            with col2:
                                st.write(f"**Current Grade:** {sub.get('grade', 'Not graded')}/{selected_assignment.get('max_score', 'N/A')}")
                                st.write(f"**Late Submission:** {sub.get('late_days', 0)} days")
                            st.write("**Submission Content:**")
                            st.write(sub.get('submission_text', 'No content provided.'))
                            if sub.get('submission_file_path') and os.path.exists(sub['submission_file_path']):
                                try:
                                    with open(sub['submission_file_path'], "rb") as f:
                                        st.download_button(
                                            label="Download Submitted File",
                                            data=f.read(),
                                            file_name=os.path.basename(sub['submission_file_path']),
                                            mime="application/octet-stream",
                                            key=f"download_submission_{sub['id']}"
                                        )
                                except Exception as e:
                                    st.warning(f"Could not download submission file: {e}")

                            with st.form(f"grade_form_{sub.get('student_id', 'N/A')}_{selected_assignment.get('id', 'N/A')}"):
                                grade = st.number_input(
                                    "Grade",
                                    min_value=0,
                                    max_value=selected_assignment.get('max_score', 100),
                                    value=sub.get('grade', 0),
                                    key=f"grade_{sub.get('student_id', 'N/A')}_{selected_assignment.get('id', 'N/A')}"
                                )
                                feedback = st.text_area(
                                    "Feedback",
                                    value=sub.get('feedback', ""),
                                    height=150
                                )
                                status = st.selectbox(
                                    "Status",
                                    ["Submitted", "Graded", "Needs Revision"],
                                    index=["Submitted", "Graded", "Needs Revision"].index(sub.get('status', 'Submitted'))
                                )
                                submitted = st.form_submit_button("Submit Grade")
                                if submitted:
                                    sub['grade'] = grade
                                    sub['feedback'] = feedback
                                    sub['status'] = status
                                    assignment_found_and_updated = False
                                    for i, assign_item in enumerate(assignments_data):
                                        if assign_item['id'] == selected_assignment['id']:
                                            assignments_data[i] = selected_assignment
                                            assignment_found_and_updated = True
                                            break
                                    if assignment_found_and_updated:
                                        all_data = load_data(ASSIGNMENTS_DATA_FILE)
                                        all_data[str(teacher_id)] = assignments_data
                                        save_data(all_data, ASSIGNMENTS_DATA_FILE)
                                        st.success("Grade submitted successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Error: Could not find or update assignment in data.")
        
        with tab3:
            st.subheader("Assignment Analytics")
            if not assignments_data:
                st.info("No assignment data available")
            else:
                assignment_stats = []
                for assignment in assignments_data:
                    if assignment.get('submissions'):
                        grades = [s.get('grade', 0) for s in assignment['submissions'] if 'grade' in s and s['grade'] is not None]
                        avg_grade = sum(grades) / len(grades) if grades else 0
                        students_in_class = get_students_by_class(assignment.get('assigned_class', ''))
                        total_students_in_class = len(students_in_class)
                        completion_rate = f"{len(assignment['submissions'])/total_students_in_class:.0%}" if total_students_in_class > 0 else "N/A"
                        assignment_stats.append({
                            "Assignment": assignment.get('title', 'N/A'),
                            "Class": assignment.get('assigned_class', 'N/A'),
                            "Due Date": assignment.get('due_date', 'N/A'),
                            "Submissions": len(assignment['submissions']),
                            "Avg Grade": f"{avg_grade:.1f}/{assignment.get('max_score', 'N/A')}",
                            "Completion": completion_rate
                        })

                if assignment_stats:
                    st.dataframe(pd.DataFrame(assignment_stats))
                
                grades_data = []
                for assignment in assignments_data:
                    for sub in assignment.get('submissions', []):
                        if 'grade' in sub and sub['grade'] is not None:
                            grades_data.append({
                                "Assignment": assignment.get('title', 'N/A'),
                                "Grade": sub.get('grade', 0),
                                "Class": assignment.get('assigned_class', 'N/A')
                            })
                
                if grades_data:
                    grades_df = pd.DataFrame(grades_data)
                    st.bar_chart(grades_df.groupby('Assignment')['Grade'].mean())
    
    # Performance Section
    elif selected == "Performance":
        st.header("📈 Student Performance Tracking")
        tab1, tab2 = st.tabs(["Enter Marks", "View Performance"])
        
        performance_data = load_data(PERFORMANCE_DATA_FILE).get(str(teacher_id), [])

        with tab1:
            with st.form("enter_marks"):
                st.subheader("Enter Marks for an Exam/Test")
                selected_class = st.selectbox("Select Class", get_full_class_list(), key="performance_class")
                exam_name = st.text_input("Exam Name (e.g., Mid-Term, Final Exam)")
                subject = st.selectbox("Subject", COMMON_SUBJECTS)
                max_marks = st.number_input("Maximum Marks", min_value=1, value=100)
                
                students = get_students_by_class(selected_class)
                marks_input = {}
                for student in students:
                    marks = st.number_input(f"Marks for {student['name']}", min_value=0, max_value=max_marks, key=f"marks_{student['id']}")
                    marks_input[student['id']] = marks
                
                if st.form_submit_button("Save Marks"):
                    new_entry = {
                        "id": str(uuid.uuid4()),
                        "teacher_id": str(teacher_id),
                        "class_name": selected_class,
                        "exam_name": exam_name,
                        "subject": subject,
                        "max_marks": max_marks,
                        "date_recorded": str(datetime.today().date()),
                        "student_marks": marks_input
                    }
                    performance_data.append(new_entry)
                    all_data = load_data(PERFORMANCE_DATA_FILE)
                    all_data[str(teacher_id)] = performance_data
                    save_data(all_data, PERFORMANCE_DATA_FILE)
                    st.success("Marks saved successfully!")
                    st.rerun()

        with tab2:
            st.subheader("View Performance Records")
            if not performance_data:
                st.info("No performance data entered yet")
            else:
                df = pd.DataFrame(performance_data)
                
                records = []
                for _, row in df.iterrows():
                    for student_id, marks in row['student_marks'].items():
                        student_info = next((s for s in get_students_by_class(row['class_name']) if s['id'] == student_id), {})
                        records.append({
                            "Exam Name": row['exam_name'],
                            "Subject": row['subject'],
                            "Class": row['class_name'],
                            "Student Name": student_info.get('name', 'N/A'),
                            "Marks": marks,
                            "Max Marks": row['max_marks'],
                            "Date Recorded": row['date_recorded']
                        })
                
                if records:
                    records_df = pd.DataFrame(records)
                    st.dataframe(records_df)
                    
                    selected_student = st.selectbox("Select Student to view trend", [""] + sorted(records_df["Student Name"].unique()))
                    if selected_student:
                        student_data_trend = records_df[records_df["Student Name"] == selected_student]
                        student_data_trend["Date Recorded"] = pd.to_datetime(student_data_trend["Date Recorded"])
                        st.line_chart(student_data_trend.set_index("Date Recorded")[["Marks"]])
    
    # Communication Section
    elif selected == "Communication":
        st.header("💬 Communication with Parents")
        tab1, tab2 = st.tabs(["Send Message", "Message History"])
        
        messages_data = load_data(MESSAGES_DATA_FILE).get(str(teacher_id), [])

        with tab1:
            with st.form("send_message", clear_on_submit=True):
                st.subheader("Send a Message to a Parent")
                students = get_students_by_class(st.selectbox("Select Class", get_full_class_list(), key="msg_class"))
                
                if not students:
                    st.warning("No students in this class to send a message to.")
                    return
                
                student_to_message = st.selectbox(
                    "Select Student",
                    students,
                    format_func=lambda s: f"{s['name']} ({s['admission_no']})"
                )
                
                message_subject = st.text_input("Subject")
                message_body = st.text_area("Message Content", height=200)
                
                if st.form_submit_button("Send Message"):
                    if not message_body:
                        st.error("Message content cannot be empty.")
                    else:
                        new_message = {
                            "id": str(uuid.uuid4()),
                            "recipient_student_id": student_to_message['id'],
                            "recipient_name": student_to_message['name'],
                            "subject": message_subject,
                            "body": message_body,
                            "timestamp": str(datetime.now()),
                            "status": "Sent"
                        }
                        messages_data.append(new_message)
                        all_data = load_data(MESSAGES_DATA_FILE)
                        all_data[str(teacher_id)] = messages_data
                        save_data(all_data, MESSAGES_DATA_FILE)
                        st.success("Message sent successfully!")
                        st.rerun()

        with tab2:
            st.subheader("Message History")
            if not messages_data:
                st.info("No messages sent yet.")
            else:
                for msg in sorted(messages_data, key=lambda x: x['timestamp'], reverse=True):
                    with st.expander(f"**{msg.get('subject', 'No Subject')}** to {msg.get('recipient_name', 'N/A')} on {msg.get('timestamp', 'N/A')}"):
                        st.write(msg.get('body', ''))
                        st.write(f"Status: {msg.get('status', 'N/A')}")
    
    # Resources Section
    elif selected == "Resources":
        st.header("📚 Academic Resources & Sharing")
        tab1, tab2 = st.tabs(["Upload Resource", "View Resources"])
        
        resources_data = load_data(RESOURCES_DATA_FILE).get(str(teacher_id), [])

        with tab1:
            with st.form("upload_resource", clear_on_submit=True):
                st.subheader("Upload a new Resource")
                title = st.text_input("Resource Title*")
                description = st.text_area("Description")
                resource_file = st.file_uploader("Upload File*", type=["pdf", "docx", "pptx", "xlsx"])
                tags = st.text_input("Tags (comma-separated, e.g., math, grade5, worksheet)")
                
                if st.form_submit_button("Upload Resource"):
                    if not all([title, resource_file]):
                        st.error("Title and a file are required.")
                    else:
                        file_save_path = os.path.join(DATA_DIR, "attachments", f"resource_{str(uuid.uuid4())}_{resource_file.name}")
                        with open(file_save_path, "wb") as f:
                            f.write(resource_file.getbuffer())

                        new_resource = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "description": description,
                            "file_path": file_save_path,
                            "file_name": resource_file.name,
                            "tags": [t.strip() for t in tags.split(',')],
                            "uploaded_by": teacher_data.get('name', ''),
                            "upload_date": str(datetime.today().date())
                        }
                        resources_data.append(new_resource)
                        all_data = load_data(RESOURCES_DATA_FILE)
                        all_data[str(teacher_id)] = resources_data
                        save_data(all_data, RESOURCES_DATA_FILE)
                        st.success("Resource uploaded successfully!")
                        st.rerun()

        with tab2:
            st.subheader("Available Resources")
            if not resources_data:
                st.info("No resources uploaded yet.")
            else:
                search_query = st.text_input("Search resources by title or tags")
                
                filtered_resources = resources_data
                if search_query:
                    filtered_resources = [
                        res for res in resources_data
                        if search_query.lower() in res['title'].lower() or
                           any(search_query.lower() in tag.lower() for tag in res.get('tags', []))
                    ]
                
                if not filtered_resources:
                    st.warning("No resources match your search criteria.")
                else:
                    for res in filtered_resources:
                        with st.expander(f"**{res['title']}** (uploaded by {res.get('uploaded_by', 'N/A')})"):
                            st.write(res.get('description', ''))
                            st.write(f"Tags: {', '.join(res.get('tags', []))}")
                            st.write(f"Uploaded: {res.get('upload_date', 'N/A')}")
                            if res.get('file_path') and os.path.exists(res['file_path']):
                                with open(res['file_path'], "rb") as f:
                                    st.download_button(
                                        label=f"Download {res.get('file_name', 'File')}",
                                        data=f.read(),
                                        file_name=res.get('file_name', 'file.pdf'),
                                        mime="application/octet-stream",
                                        key=f"download_res_{res['id']}"
                                    )
    
    # Leave Section
    elif selected == "Leave":
        st.header("⏳ Teacher Leave Management")
        tab1, tab2 = st.tabs(["Apply for Leave", "Leave History"])
        
        leave_data = load_data(LEAVE_DATA_FILE).get(str(teacher_id), [])

        with tab1:
            with st.form("apply_leave", clear_on_submit=True):
                st.subheader("Apply for a New Leave")
                leave_type = st.selectbox("Leave Type*", ["Sick Leave", "Casual Leave", "Maternity Leave", "Paternity Leave", "Sabbatical", "Other"])
                start_date = st.date_input("Start Date*", min_value=datetime.today().date())
                end_date = st.date_input("End Date*", min_value=start_date)
                reason = st.text_area("Reason for Leave*", height=150)
                supporting_doc = st.file_uploader("Upload Supporting Document (e.g., medical certificate)", type=["pdf", "jpg", "png"])
                
                if st.form_submit_button("Submit Application"):
                    if not all([start_date, end_date, reason]):
                        st.error("Please fill all required fields (*)")
                    elif end_date < start_date:
                        st.error("End date cannot be before start date.")
                    else:
                        doc_path = None
                        if supporting_doc:
                            doc_filename = f"leave_doc_{str(uuid.uuid4())}_{supporting_doc.name}"
                            doc_save_path = os.path.join(DATA_DIR, "leave_attachments", doc_filename)
                            with open(doc_save_path, "wb") as f:
                                f.write(supporting_doc.getbuffer())
                            doc_path = doc_save_path
                            
                        new_leave_request = {
                            "id": str(uuid.uuid4()),
                            "type": leave_type,
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "reason": reason,
                            "document_path": doc_path,
                            "status": "Pending",
                            "submission_date": str(datetime.today().date())
                        }
                        leave_data.append(new_leave_request)
                        all_data = load_data(LEAVE_DATA_FILE)
                        all_data[str(teacher_id)] = leave_data
                        save_data(all_data, LEAVE_DATA_FILE)
                        st.success("Leave application submitted successfully! It is now pending admin approval.")
                        st.rerun()

        with tab2:
            st.subheader("Leave Application History")
            if not leave_data:
                st.info("No leave applications found.")
            else:
                for req in sorted(leave_data, key=lambda x: x['submission_date'], reverse=True):
                    with st.expander(f"**{req['type']}** from {req['start_date']} to {req['end_date']} - Status: {req['status']}"):
                        st.write(f"**Reason:** {req['reason']}")
                        st.write(f"**Submitted on:** {req['submission_date']}")
                        if req.get('document_path') and os.path.exists(req['document_path']):
                            st.write("Supporting Document: Available")
                            with open(req['document_path'], "rb") as f:
                                st.download_button(
                                    label="Download Document",
                                    data=f.read(),
                                    file_name=os.path.basename(req['document_path']),
                                    mime="application/octet-stream"
                                )

    # Export Data Section
    elif selected == "Export Data":
        st.header("📊 Export My Data")
        
        st.write("Download your personal data from the system.")
        
        st.subheader("Profile Data")
        if st.button("Download Profile Data (JSON)"):
            profile_json = json.dumps(teacher_data, indent=2)
            st.download_button(
                label="Download JSON",
                data=profile_json,
                file_name=f"teacher_profile_{teacher_data.get('username')}.json",
                mime="application/json"
            )

        st.subheader("Attendance Data")
        if st.button("Download Attendance Data (CSV)"):
            attendance_data = load_data(ATTENDANCE_DATA_FILE).get(str(teacher_id), {})
            if attendance_data:
                records = []
                for date, classes in attendance_data.items():
                    for class_name, students in classes.items():
                        for student_id, status in students.items():
                            student_info = next((s for s in get_students_by_class(class_name) if s['id'] == student_id), {})
                            records.append({
                                "Date": date,
                                "Class": class_name,
                                "Student Name": student_info.get('name', 'N/A'),
                                "Admission No": student_info.get('admission_no', 'N/A'),
                                "Status": status
                            })
                df_attendance = pd.DataFrame(records)
                csv = df_attendance.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Attendance Data",
                    csv,
                    "attendance_export.csv",
                    "text/csv"
                )
            else:
                st.info("No attendance data to export.")

    # School Essentials Section
    elif selected == "School Essentials":
        st.header("🛒 School Essentials")
        st.write("Welcome to the School Essentials portal. Here you can order required items.")
        
        st.subheader("Place a New Order")
        
        essentials = {
            "Notebook (Pack of 10)": 150,
            "Pen Set (Pack of 5)": 50,
            "Pencil Box": 30,
            "Drawing Book": 45,
            "Geometry Box": 75,
            "Whiteboard Markers (Set of 4)": 100
        }
        
        order_details = {}
        total_price = 0
        
        for item, price in essentials.items():
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                quantity = st.number_input(f"Quantity for {item} (₹{price})", min_value=0, step=1, key=f"quantity_{item}")
            with col2:
                st.write(f"Total: ₹{quantity * price}")
            with col3:
                order_details[item] = quantity
                total_price += quantity * price
        
        st.markdown("---")
        st.subheader(f"Total Order Cost: ₹{total_price}")
        
        if st.button("Place Order"):
            if total_price > 0:
                orders_data = load_orders()
                teacher_id_str = str(st.session_state['teacher_id'])
                if teacher_id_str not in orders_data:
                    orders_data[teacher_id_str] = []
                
                new_order = {
                    "id": str(uuid.uuid4()),
                    "items": {item: qty for item, qty in order_details.items() if qty > 0},
                    "total_cost": total_price,
                    "status": "Pending",
                    "order_date": str(datetime.today().date())
                }
                
                orders_data[teacher_id_str].append(new_order)
                save_orders(orders_data)
                st.success("Order placed successfully! It is now pending approval.")
                st.balloons()
            else:
                st.error("Please add at least one item to place an order.")

def show():
    st.set_page_config(
        page_title="Teacher Module",
        page_icon="👨‍🏫",
        layout="wide"
    )
    teacher_module()

if __name__ == "__main__":
    show()

