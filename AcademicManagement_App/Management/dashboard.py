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
# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
# Ensure attachments directory exists within data directory
os.makedirs(os.path.join(DATA_DIR, "attachments"), exist_ok=True)

TEACHER_DATA_FILE = os.path.join(DATA_DIR, "teacher_data.json")
STUDENT_DATA_FILE = os.path.join(DATA_DIR, "student_data.json")
CLASS_DATA_FILE = os.path.join(DATA_DIR, "class_data.json")
FEE_DATA_FILE = os.path.join(DATA_DIR, "fee_data.json")
EVENT_NOTICE_DATA_FILE = os.path.join(DATA_DIR, "event_notice_data.json")
ATTENDANCE_DATA_FILE = os.path.join(DATA_DIR, "attendance_data.json")
ASSIGNMENTS_DATA_FILE = os.path.join(DATA_DIR, "assignments_data.json")
PERFORMANCE_DATA_FILE = os.path.join(DATA_DIR, "performance_data.json")
TIMETABLE_DATA_FILE = os.path.join(DATA_DIR, "timetable_data.json")
MESSAGES_DATA_FILE = os.path.join(DATA_DIR, "messages_data.json")
RESOURCES_DATA_FILE = os.path.join(DATA_DIR, "resources_data.json")
LEAVE_DATA_FILE = os.path.join(DATA_DIR, "leave_data.json")


def load_data(filename, default_value={}):
    """Load data from JSON file, returning a default value if file is empty or corrupted."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                # Attempt to load, if file is empty, json.load will raise an error
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

# Grade levels and sections
GRADE_LEVELS = ["Nursery", "LKG", "UKG"] + [f"Grade {i}" for i in range(1, 11)]
CLASS_SECTIONS = ["A", "B", "C", "D"]

def get_full_class_list():
    """Generate complete list of classes with sections"""
    classes = []
    for grade in GRADE_LEVELS:
        if grade in ["Nursery", "LKG", "UKG"]:
            classes.append(grade)
        else:
            for section in CLASS_SECTIONS:
                classes.append(f"{grade}{section}")
    return classes

# ==============================================================================
# SESSION STATE INITIALIZATION (Moved to top-level for immediate availability)
# ==============================================================================

# Initialize teachers data
if 'teachers' not in st.session_state:
    st.session_state.teachers = load_data(TEACHER_DATA_FILE, default_value={})
    print(f"DEBUG: Initial teachers loaded: {st.session_state.teachers}") # DEBUG PRINT

# Initialize students data (structured as {class_name: [student_list]})
if 'students' not in st.session_state:
    st.session_state.students = load_data(STUDENT_DATA_FILE, default_value={})
    if not st.session_state.students:
        # Add some sample student data if the file is empty
        sample_students = {}
        for class_name in get_full_class_list():
            sample_students[class_name] = []
            num_students = 2 if class_name in ["Nursery", "LKG", "UKG"] else 3
            for i in range(1, num_students + 1):
                # Ensures unique admission numbers across sample data
                admission_no = f"ADM{class_name.replace(' ', '').replace('Grade', '')}{i:03d}"
                sample_students[class_name].append({
                    "id": str(uuid.uuid4()), # Unique internal ID
                    "admission_no": admission_no,
                    "name": f"Student {i} {class_name}",
                    "roll_no": f"{i}",
                    "class": class_name,
                    "dob": "2010-01-01", # Example fixed date
                    "date_of_joining": "2023-09-01", # Example fixed date
                    "date_of_tc": None,
                    "adhar_number": f"1234567890{i:02d}",
                    "father_name": f"Father {i} {class_name}",
                    "mother_name": f"Mother {i} {class_name}",
                    "parent_email": f"parent{i}_{class_name.replace(' ', '_')}@example.com",
                    "parent_phone": f"98765432{i:02d}",
                    "address": f"{i} School Road, {class_name} City",
                    "emergency_contact": f"Emergency Contact {i} - 99988877{i:02d}",
                    "contact_number": f"91234567{i:02d}",
                    "blood_group": "O+",
                    "financial_status": "Paid",
                    "passport_photo_path": None
                })
        st.session_state.students = sample_students
        save_data(st.session_state.students, STUDENT_DATA_FILE)

# Initialize other data files with empty structures if they don't exist
# Use load_data with appropriate default values (dict for general, list for messages/resources/leave/assignments)
data_files_to_initialize = {
    'attendance_data': (ATTENDANCE_DATA_FILE, {}), # {teacher_id: {date: {class: {student_id: status}}}}
    'assignments_data': (ASSIGNMENTS_DATA_FILE, {}), # {teacher_id: [assignment_objects]}
    'timetable_data': (TIMETABLE_DATA_FILE, {}), # {class_name: {day: {period: {subject, teacher}}}}
    'performance_data': (PERFORMANCE_DATA_FILE, {}), # {class_name: {student_id: {subject: score, ...}}}
    'messages_data': (MESSAGES_DATA_FILE, {}), # {teacher_id: [message_objects]}
    'resources_data': (RESOURCES_DATA_FILE, {}), # {teacher_id: [resource_objects]}
    'leave_data': (LEAVE_DATA_FILE, {}), # {teacher_id: [leave_application_objects]}
    'class_data': (CLASS_DATA_FILE, {}), # Can be used for class-specific settings/info
    'fee_data': (FEE_DATA_FILE, {}), # {student_id: fee_record_object}
    'event_notice_data': (EVENT_NOTICE_DATA_FILE, {}) # {event_id: event_object}
}

for session_key, (file_path, default_type) in data_files_to_initialize.items():
    if session_key not in st.session_state:
        st.session_state[session_key] = load_data(file_path, default_value=default_type)
        if not st.session_state[session_key]: # If file was empty/corrupted, re-initialize with the default structure
             st.session_state[session_key] = default_type
        save_data(st.session_state[session_key], file_path)


# ======================
# MANAGEMENT MODULE FUNCTIONS
# ======================

def display_overview_dashboard():
    """Display overview of institution performance"""
    st.header("📊 Institution Performance Overview")

    teachers = st.session_state.teachers
    students_by_class = st.session_state.students # This is a dict of lists, not a flat list
    attendance_data = st.session_state.attendance_data
    assignments_data = st.session_state.assignments_data
    fee_data = st.session_state.fee_data

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Teachers", len(teachers))
    with col2:
        total_students = sum(len(students) for students in students_by_class.values()) if students_by_class else 0
        st.metric("Total Students", total_students)
    with col3:
        total_classes = len(get_full_class_list())
        st.metric("Total Classes", total_classes)

    st.subheader("Key Performance Indicators")

    # Attendance Rate
    total_present_attendance = 0
    total_recorded_attendance = 0
    if attendance_data:
        for teacher_attn in attendance_data.values():
            for date_attn in teacher_attn.values():
                for class_attn in date_attn.values():
                    total_present_attendance += sum(1 for status in class_attn.values() if status == "Present")
                    total_recorded_attendance += len(class_attn)

        overall_attendance_rate = (total_present_attendance / total_recorded_attendance * 100) if total_recorded_attendance > 0 else 0
        st.metric("Overall Attendance Rate", f"{overall_attendance_rate:.1f}%")
    else:
        st.info("No attendance data available for analytics.")

    # Assignment Completion Rate
    total_assignments_for_kpi = 0
    total_submissions_for_kpi = 0
    if assignments_data:
        for teacher_assignments in assignments_data.values():
            for assignment in teacher_assignments:
                total_assignments_for_kpi += 1
                total_submissions_for_kpi += len(assignment.get('submissions', []))

        completion_rate = (total_submissions_for_kpi / total_assignments_for_kpi * 100) if total_assignments_for_kpi > 0 else 0
        st.metric("Overall Assignment Completion Rate", f"{completion_rate:.1f}%")
    else:
        st.info("No assignment data available for analytics.")

    # Fee Collection Status
    if fee_data:
        total_expected_fees = sum(fee.get('amount_due', 0.0) for fee in fee_data.values())
        total_collected_fees = sum(fee.get('amount_paid', 0.0) for fee in fee_data.values())
        collection_percentage = (total_collected_fees / total_expected_fees * 100) if total_expected_fees > 0 else 0
        st.metric("Fee Collection Percentage", f"{collection_percentage:.1f}%")
    else:
        st.info("No fee data available for analytics.")

    st.subheader("Student Distribution by Class")
    student_counts = {cls: len(students) for cls, students in students_by_class.items()}
    if student_counts:
        df_students = pd.DataFrame(student_counts.items(), columns=['Class', 'Number of Students'])
        st.bar_chart(df_students.set_index('Class'))
    else:
        st.info("No student data available to display distribution.")

def manage_students_admin():
    """Admin view for managing student records (add/edit/delete)"""
    st.header("🧑‍🎓 Student Management")

    student_data = st.session_state.students

    tab1, tab2 = st.tabs(["Add Student", "Manage Existing Students"])

    with tab1:
        st.subheader("Add New Student")
        with st.form("add_student_admin", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_admission_no = st.text_input("Student Admission Number*", help="Unique admission number for the student.").strip()
                name = st.text_input("Full Name*", help="Full legal name of the student.").strip()
                roll_no = st.text_input("Roll No.", help="Student's roll number in class (optional).").strip()
                class_name = st.selectbox("Class*", get_full_class_list())
                dob = st.date_input("Date of Birth*", max_value=datetime.today().date())
                date_of_joining = st.date_input("Date of Joining*", max_value=datetime.today().date())
                date_of_tc = st.date_input("Date of TC (Optional)", value=None, help="Date of Transfer Certificate issuance, if applicable.")
                adhar_number = st.text_input("Aadhar Number (Optional)").strip()
                contact_number = st.text_input("Student's Contact Number (Optional)").strip()
            with col2:
                parent_name = st.text_input("Parent/Guardian Name*").strip()
                father_name = st.text_input("Father's Name*").strip()
                mother_name = st.text_input("Mother's Name*").strip()
                parent_email = st.text_input("Parent Email*").strip()
                parent_phone = st.text_input("Parent Phone*").strip()
                address = st.text_area("Address").strip()
                emergency_contact = st.text_input("Emergency Contact (Name & Number)*").strip()
                blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
                financial_status = st.text_input("Financial Status (e.g., Paid, Scholarship, Partial)").strip()
                passport_photo = st.file_uploader("Upload Passport Photo (Optional)", type=["jpg", "jpeg", "png"])

            if st.form_submit_button("Add Student"):
                required_fields = [student_admission_no, name, class_name, dob, date_of_joining, parent_name, father_name, mother_name, parent_email, parent_phone, emergency_contact]
                if not all(required_fields) or not all(field for field in required_fields if isinstance(field, str)):
                    st.error("Please fill all required fields (*)")
                elif not (dob and date_of_joining): # Ensure date inputs are not None
                    st.error("Please select valid dates for Date of Birth and Date of Joining.")
                else:
                    # Check if admission number already exists globally
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
                                st.success(f"Passport photo saved to {photo_save_path}")
                            except Exception as e:
                                st.error(f"Error saving photo: {e}")
                                photo_path = None # Ensure photo_path is None on error

                        new_student_record = {
                            "id": str(uuid.uuid4()), # Unique internal ID
                            "admission_no": student_admission_no,
                            "name": name,
                            "roll_no": roll_no,
                            "class": class_name,
                            "dob": str(dob),
                            "date_of_joining": str(date_of_joining),
                            "date_of_tc": str(date_of_tc) if date_of_tc else None,
                            "adhar_number": adhar_number,
                            "parent_name": parent_name,
                            "father_name": father_name,
                            "mother_name": mother_name,
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
        all_students_list = []
        for class_name_key, students_in_class in student_data.items():
            for student in students_in_class:
                all_students_list.append({**student, "class_name_display": class_name_key})

        if not all_students_list:
            st.info("No student records available.")
            return

        df_students = pd.DataFrame(all_students_list)
        # Select columns to display in the main table
        display_columns = [
            "admission_no", "name", "roll_no", "class_name_display", "dob", "date_of_joining",
            "father_name", "mother_name", "parent_email", "parent_phone", "contact_number",
            "emergency_contact", "blood_group", "financial_status"
        ]
        st.dataframe(df_students[display_columns], use_container_width=True)

        st.subheader("Edit or Delete Student")

        # Use admission number for selection
        student_admission_numbers = [s['admission_no'] for s in all_students_list if 'admission_no' in s]
        student_to_manage_admission_no = st.selectbox(
            "Select Student by Admission Number to Edit/Delete",
            [""] + sorted(student_admission_numbers), # Sort for better UX
            key="edit_delete_student_admission_no"
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

            action = st.radio("Choose Action", ["Edit", "Delete"], key="student_action_radio")

            if action == "Edit":
                st.subheader(f"Edit Details for {selected_student_obj['name']}")
                with st.form(f"edit_student_form_{selected_student_obj['id']}"):
                    col1_edit, col2_edit = st.columns(2)
                    with col1_edit:
                        new_name = st.text_input("Full Name", value=selected_student_obj.get('name', ''))
                        new_roll_no = st.text_input("Roll No.", value=selected_student_obj.get('roll_no', ''))
                        # Safely convert date strings to datetime.date objects for st.date_input
                        try:
                            default_dob = datetime.strptime(selected_student_obj['dob'], '%Y-%m-%d').date() if selected_student_obj.get('dob') else None
                        except (ValueError, TypeError):
                            default_dob = None
                        try:
                            default_joining_date = datetime.strptime(selected_student_obj['date_of_joining'], '%Y-%m-%d').date() if selected_student_obj.get('date_of_joining') else None
                        except (ValueError, TypeError):
                            default_joining_date = None
                        try:
                            default_tc_date = datetime.strptime(selected_student_obj['date_of_tc'], '%Y-%m-%d').date() if selected_student_obj.get('date_of_tc') else None
                        except (ValueError, TypeError):
                            default_tc_date = None

                        new_dob = st.date_input("Date of Birth", value=default_dob or datetime.today().date(), max_value=datetime.today().date())
                        new_date_of_joining = st.date_input("Date of Joining", value=default_joining_date or datetime.today().date(), max_value=datetime.today().date())
                        new_date_of_tc = st.date_input("Date of TC (Optional)", value=default_tc_date)
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
                        blood_group_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
                        new_blood_group = st.selectbox("Blood Group", blood_group_options, index=blood_group_options.index(selected_student_obj.get('blood_group', 'Unknown')))
                        new_financial_status = st.text_input("Financial Status", value=selected_student_obj.get('financial_status', ''))
                        # For photo, allow new upload or display current
                        current_photo_path = selected_student_obj.get('passport_photo_path')
                        if current_photo_path and os.path.exists(current_photo_path):
                            st.image(current_photo_path, caption="Current Passport Photo", width=150)
                            st.info("Upload a new photo to replace the current one.")
                        new_passport_photo = st.file_uploader("Upload New Passport Photo (Optional)", type=["jpg", "jpeg", "png"], key=f"edit_photo_{selected_student_obj['id']}")

                    if st.form_submit_button("Save Changes"):
                        # Find the student to update by ID and class
                        found_and_updated = False
                        for idx, s in enumerate(student_data.get(selected_student_obj['class'], [])):
                            if s['id'] == selected_student_obj['id']:
                                student_data[selected_student_obj['class']][idx].update({
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
                                        student_data[selected_student_obj['class']][idx]["passport_photo_path"] = photo_save_path
                                        st.success(f"New passport photo saved to {photo_save_path}")
                                    except Exception as e:
                                        st.error(f"Error saving new photo: {e}")
                                found_and_updated = True
                                break
                        if found_and_updated:
                            save_data(student_data, STUDENT_DATA_FILE)
                            st.success("Student details updated successfully!")
                            st.rerun()
                        else:
                            st.error("Error: Student not found in data for update.")

            elif action == "Delete":
                st.warning(f"Are you sure you want to delete {selected_student_obj['name']} (Admission No: {selected_student_obj['admission_no']})?")
                if st.button("Confirm Delete", key=f"confirm_delete_{selected_student_obj['id']}"):
                    original_class = selected_student_obj['class']
                    st.session_state.students[original_class] = [
                        s for s in st.session_state.students[original_class]
                        if s['id'] != selected_student_obj['id']
                    ]
                    # If the class list becomes empty, remove the class entry
                    if not st.session_state.students[original_class]:
                        del st.session_state.students[original_class]

                    save_data(st.session_state.students, STUDENT_DATA_FILE)
                    st.success("Student deleted successfully!")
                    st.rerun()
        else:
            st.info("Please select a student by Admission Number to manage.")


def manage_teachers_admin():
    """Admin view for managing teacher records (add/edit/delete)"""
    st.header("👨‍🏫 Teacher Management")

    teachers = st.session_state.teachers

    tab1, tab2 = st.tabs(["Add Teacher", "Manage Existing Teachers"])

    with tab1:
        st.subheader("Add New Teacher")
        with st.form("add_teacher_admin", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Choose Username*", help="This will be the teacher's login username.").strip()
                password = st.text_input("Choose Password*", type="password")
                teacher_name = st.text_input("Full Name*").strip()
                teacher_subject = st.selectbox("Subject*", ["Mathematics", "Science", "English", "History", "Geography", "Computer Science", "Arts", "Physical Education", "Other", "Administration"])
                teacher_email = st.text_input("Email (Optional)").strip()
                teacher_phone = st.text_input("Phone (Optional)").strip()
            with col2:
                designation = st.text_input("Designation*", help="e.g., Head of Department, Senior Teacher").strip()
                joining_date = st.date_input("Joining Date*", value=datetime.today().date())
                resignation_date = st.date_input("Resignation Date (Optional)", value=None, help="Set if the teacher has resigned.")
                epf_number = st.text_input("EPF Number (Optional)").strip()
                esi_number = st.text_input("ESI Number (Optional)").strip()
                payroll = st.number_input("Monthly Payroll (₹)", min_value=0.0, step=100.0, format="%.2f")
                is_admin_checkbox = st.checkbox("Grant Admin Privileges", help="Only grant to trusted personnel.")

            if st.form_submit_button("Add Teacher"):
                required_fields = [username, password, teacher_name, teacher_subject, designation, joining_date]
                if not all(required_fields) or not all(field for field in required_fields if isinstance(field, str)):
                    st.error("Please fill all required fields (*)")
                elif not joining_date: # Ensure date input is not None
                    st.error("Please select a valid Joining Date.")
                else:
                    if any(t.get('username') == username for t in teachers.values()):
                        st.error("Username already exists. Please choose a different one.")
                    else:
                        new_id = str(uuid.uuid4())
                        st.session_state.teachers[new_id] = {
                            "id": new_id,
                            "username": username,
                            "password": hashlib.sha256(password.encode()).hexdigest(),
                            "name": teacher_name,
                            "subject": teacher_subject,
                            "email": teacher_email,
                            "phone": teacher_phone,
                            "join_date": str(joining_date),
                            "designation": designation,
                            "resignation_date": str(resignation_date) if resignation_date else None,
                            "epf_number": epf_number,
                            "esi_number": esi_number,
                            "payroll": payroll,
                            "is_admin": is_admin_checkbox
                        }
                        save_data(st.session_state.teachers, TEACHER_DATA_FILE)
                        st.success(f"Teacher '{teacher_name}' added successfully!")
                        st.rerun()

    with tab2:
        st.subheader("Manage Existing Teachers")
        teachers_list = list(teachers.values())

        if not teachers_list:
            st.info("No teacher records available.")
            return

        df_teachers = pd.DataFrame(teachers_list)
        # Don't display password hash and internal ID
        df_teachers_display = df_teachers.drop(columns=['password', 'id'], errors='ignore')
        st.dataframe(df_teachers_display, use_container_width=True)

        st.subheader("Edit or Delete Teacher")
        # Use username for selection as it's more human-readable and unique
        teacher_usernames = sorted([t['username'] for t in teachers_list if 'username' in t])
        selected_teacher_username = st.selectbox("Select Teacher by Username", [""] + teacher_usernames, key="edit_delete_teacher_username")

        selected_teacher_obj = None
        if selected_teacher_username:
            selected_teacher_obj = next((t for t in teachers_list if t.get('username') == selected_teacher_username), None)


        if selected_teacher_obj:
            st.write(f"**Selected Teacher:** {selected_teacher_obj['name']} ({selected_teacher_obj['username']})")

            action = st.radio("Choose Action", ["Edit", "Delete"], key="teacher_action_radio")

            if action == "Edit":
                st.subheader(f"Edit Details for {selected_teacher_obj['name']}")
                with st.form(f"edit_teacher_form_{selected_teacher_obj['id']}"):
                    col1_edit, col2_edit = st.columns(2)
                    with col1_edit:
                        new_name = st.text_input("Full Name", value=selected_teacher_obj.get('name', ''))
                        subject_options = ["Mathematics", "Science", "English", "History", "Geography", "Computer Science", "Arts", "Physical Education", "Other", "Administration"]
                        new_subject = st.selectbox("Subject", subject_options, index=subject_options.index(selected_teacher_obj.get('subject', 'Other')))
                        new_email = st.text_input("Email", value=selected_teacher_obj.get('email', ''))
                        new_phone = st.text_input("Phone", value=selected_teacher_obj.get('phone', ''))
                        new_password_edit = st.text_input("New Password (leave blank to keep current)", type="password", key=f"new_pwd_edit_{selected_teacher_obj['id']}")
                    with col2_edit:
                        new_designation = st.text_input("Designation", value=selected_teacher_obj.get('designation', ''))
                        try:
                            default_join_date = datetime.strptime(selected_teacher_obj['join_date'], '%Y-%m-%d').date() if selected_teacher_obj.get('join_date') else None
                        except (ValueError, TypeError):
                            default_join_date = None
                        try:
                            default_resignation_date = datetime.strptime(selected_teacher_obj['resignation_date'], '%Y-%m-%d').date() if selected_teacher_obj.get('resignation_date') else None
                        except (ValueError, TypeError):
                            default_resignation_date = None
                        new_joining_date = st.date_input("Joining Date", value=default_join_date or datetime.today().date())
                        new_resignation_date = st.date_input("Resignation Date (Optional)", value=default_resignation_date)
                        new_epf_number = st.text_input("EPF Number", value=selected_teacher_obj.get('epf_number', ''))
                        new_esi_number = st.text_input("ESI Number", value=selected_teacher_obj.get('esi_number', ''))
                        new_payroll = st.number_input("Monthly Payroll (₹)", min_value=0.0, step=100.0, format="%.2f", value=float(selected_teacher_obj.get('payroll', 0.0)))
                        new_is_admin = st.checkbox("Admin Privileges", value=selected_teacher_obj.get('is_admin', False))
                    if st.form_submit_button("Save Changes"):
                        # Update the teacher data in session state
                        teacher_to_update = st.session_state.teachers.get(selected_teacher_obj['id'])
                        if teacher_to_update:
                            teacher_to_update['name'] = new_name
                            teacher_to_update['subject'] = new_subject
                            teacher_to_update['email'] = new_email
                            teacher_to_update['phone'] = new_phone
                            teacher_to_update['designation'] = new_designation
                            teacher_to_update['join_date'] = str(new_joining_date)
                            teacher_to_update['resignation_date'] = str(new_resignation_date) if new_resignation_date else None
                            teacher_to_update['epf_number'] = new_epf_number
                            teacher_to_update['esi_number'] = new_esi_number
                            teacher_to_update['payroll'] = new_payroll
                            teacher_to_update['is_admin'] = new_is_admin
                            if new_password_edit:
                                teacher_to_update['password'] = hashlib.sha256(new_password_edit.encode()).hexdigest()
                            save_data(st.session_state.teachers, TEACHER_DATA_FILE)
                            st.success("Teacher details updated successfully!")
                            st.rerun()
                        else:
                            st.error("Error: Teacher not found for update.")
            elif action == "Delete":
                st.warning(f"Are you sure you want to delete {selected_teacher_obj['name']} ({selected_teacher_obj['username']})?")
                if st.button("Confirm Delete", key=f"confirm_delete_{selected_teacher_obj['id']}"):
                    del st.session_state.teachers[selected_teacher_obj['id']]
                    save_data(st.session_state.teachers, TEACHER_DATA_FILE)
                    st.success("Teacher deleted successfully!")
                    st.rerun()
        else:
            st.info("Please select a teacher by Username to manage.")

def manage_classes_admin():
    """Admin view for managing classes (e.g., assigning teachers, viewing class lists)"""
    st.header("🏫 Class Management")
    class_data = st.session_state.class_data
    teachers = st.session_state.teachers
    students_by_class = st.session_state.students
    all_teachers_list = list(teachers.values())
    teacher_options = {f"{t['name']} ({t['username']})": t['id'] for t in all_teachers_list}
    teacher_display_names = [""] + sorted(list(teacher_options.keys()))
    tab1, tab2 = st.tabs(["View/Edit Class Details", "Assign Class Teachers"])
    with tab1:
        st.subheader("View & Edit Class Details")
        full_class_list = get_full_class_list()
        selected_class = st.selectbox("Select Class", [""] + sorted(full_class_list), key="view_class_details_select")
        if selected_class:
            # Initialize class data if not present
            if selected_class not in class_data:
                class_data[selected_class] = {
                    "head_teacher_id": None,
                    "student_ids": [], # This will be derived from student_data dynamically
                    "class_capacity": 0,
                    "description": ""
                }
                save_data(class_data, CLASS_DATA_FILE)
            current_class_info = class_data[selected_class]
            st.write(f"**Class: {selected_class}**")
            # Get students currently in this class
            students_in_this_class = students_by_class.get(selected_class, [])
            st.metric("Current Students", len(students_in_this_class))
            current_head_teacher_id = current_class_info.get("head_teacher_id")
            current_head_teacher_name = teachers.get(current_head_teacher_id, {}).get("name", "Not assigned")
            st.write(f"**Head Teacher:** {current_head_teacher_name}")
            with st.form(f"edit_class_details_{selected_class}"):
                # Update general class info
                new_class_capacity = st.number_input("Class Capacity", min_value=0, value=current_class_info.get("class_capacity", 0))
                new_description = st.text_area("Description", value=current_class_info.get("description", ""))
                if st.form_submit_button("Save Class Details"):
                    class_data[selected_class]["class_capacity"] = new_class_capacity
                    class_data[selected_class]["description"] = new_description
                    save_data(class_data, CLASS_DATA_FILE)
                    st.success(f"Details for {selected_class} updated.")
                    st.rerun()
            st.subheader("Students in this Class")
            if students_in_this_class:
                df_class_students = pd.DataFrame(students_in_this_class)
                st.dataframe(df_class_students[['admission_no', 'name', 'roll_no', 'dob']], use_container_width=True)
            else:
                st.info(f"No students currently assigned to {selected_class}.")
        else:
            st.info("Select a class to view or edit its details.")
    with tab2:
        st.subheader("Assign Head Teachers to Classes")
        class_to_assign = st.selectbox("Select Class to Assign Teacher", [""] + sorted(get_full_class_list()), key="assign_class_teacher_select")
        if class_to_assign:
            # Initialize class data if not present
            if class_to_assign not in class_data:
                class_data[class_to_assign] = {
                    "head_teacher_id": None,
                    "student_ids": [],
                    "class_capacity": 0,
                    "description": ""
                }
                save_data(class_data, CLASS_DATA_FILE)
            current_head_teacher_id = class_data[class_to_assign].get("head_teacher_id")
            current_head_teacher_name = teachers.get(current_head_teacher_id, {}).get("name", "Not assigned")
            st.info(f"Current Head Teacher for {class_to_assign}: **{current_head_teacher_name}**")
            selected_teacher_display_name = st.selectbox("Select New Head Teacher", teacher_display_names, key="select_head_teacher")
            selected_teacher_id = teacher_options.get(selected_teacher_display_name)
            if st.button(f"Assign {selected_teacher_display_name} as Head Teacher for {class_to_assign}"):
                if selected_teacher_id:
                    class_data[class_to_assign]["head_teacher_id"] = selected_teacher_id
                    save_data(class_data, CLASS_DATA_FILE)
                    st.success(f"Teacher '{teachers[selected_teacher_id]['name']}' assigned as head teacher for {class_to_assign}.")
                    st.rerun()
                else:
                    st.error("Please select a teacher to assign.")
        else:
            st.info("Select a class to assign a head teacher.")

def manage_fee_admin():
    """Admin view for managing student fees"""
    st.header("💰 Fee Management")

    fee_data = st.session_state.fee_data
    students = st.session_state.students

    # Flatten the students dictionary for easier searching
    all_students_list = [s for students_in_class in students.values() for s in students_in_class]
    student_options = {f"{s['name']} ({s['admission_no']})": s['id'] for s in all_students_list}
    student_display_names = [""] + sorted(list(student_options.keys()))

    tab1, tab2 = st.tabs(["Record Fee Payment", "View/Edit Fee Records"])

    with tab1:
        st.subheader("Record New Payment")
        with st.form("record_fee_payment_form", clear_on_submit=True):
            selected_student_display_name = st.selectbox("Select Student", student_display_names, key="record_fee_student_select")
            if selected_student_display_name:
                selected_student_id = student_options[selected_student_display_name]
                selected_student_info = next((s for s in all_students_list if s['id'] == selected_student_id), None)
                if selected_student_info:
                    st.info(f"You are recording a payment for {selected_student_info['name']} in {selected_student_info['class']}.")

            payment_amount = st.number_input("Payment Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
            fee_type = st.selectbox("Fee Type", ["Tuition Fee", "Bus Fee", "Exam Fee", "Other"])
            payment_method = st.selectbox("Payment Method", ["Cash", "Online Transfer", "Cheque", "Card"])
            payment_date = st.date_input("Payment Date", value=datetime.today().date())
            description = st.text_area("Description / Notes (Optional)")

            if st.form_submit_button("Record Payment"):
                if not selected_student_display_name:
                    st.error("Please select a student.")
                elif payment_amount <= 0:
                    st.error("Payment amount must be greater than zero.")
                else:
                    fee_record = fee_data.get(selected_student_id, {"records": [], "amount_due": 0.0, "amount_paid": 0.0})
                    fee_record["records"].append({
                        "id": str(uuid.uuid4()),
                        "type": fee_type,
                        "amount": payment_amount,
                        "method": payment_method,
                        "date": str(payment_date),
                        "description": description
                    })
                    fee_record["amount_paid"] += payment_amount
                    # For simplicity, assume amount due is a fixed value or needs to be set elsewhere.
                    # This example just adds to amount_paid.
                    fee_data[selected_student_id] = fee_record
                    save_data(fee_data, FEE_DATA_FILE)
                    st.success(f"Payment of ₹{payment_amount:.2f} recorded for {selected_student_display_name} successfully.")
                    st.rerun()

    with tab2:
        st.subheader("View/Edit Fee Records")
        selected_student_display_name_view = st.selectbox("Select Student", student_display_names, key="view_fee_student_select")
        if selected_student_display_name_view:
            selected_student_id = student_options[selected_student_display_name_view]
            fee_record = fee_data.get(selected_student_id, {"records": [], "amount_due": 0.0, "amount_paid": 0.0})

            st.metric("Total Amount Paid", f"₹{fee_record['amount_paid']:.2f}")

            if fee_record["records"]:
                st.subheader("Payment History")
                df_records = pd.DataFrame(fee_record["records"])
                df_records_display = df_records.drop(columns=['id'], errors='ignore')
                st.dataframe(df_records_display, use_container_width=True)

                st.subheader("Delete a Record")
                record_ids = [r['id'] for r in fee_record['records']]
                record_to_delete_id = st.selectbox("Select Record to Delete", [""] + record_ids)

                if st.button("Delete Selected Record", key="delete_fee_record_btn"):
                    if record_to_delete_id:
                        record_to_delete = next((r for r in fee_record['records'] if r['id'] == record_to_delete_id), None)
                        if record_to_delete:
                            fee_record['records'] = [r for r in fee_record['records'] if r['id'] != record_to_delete_id]
                            fee_record['amount_paid'] -= record_to_delete['amount']
                            fee_data[selected_student_id] = fee_record
                            save_data(fee_data, FEE_DATA_FILE)
                            st.success("Fee record deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Selected record not found.")
                    else:
                        st.warning("Please select a record to delete.")
            else:
                st.info("No payment records for this student.")
        else:
            st.info("Select a student to view their fee records.")

def manage_events_notices_admin():
    """Admin view for managing events and notices"""
    st.header("📢 Events & Notices")

    event_notice_data = st.session_state.event_notice_data

    tab1, tab2 = st.tabs(["Add Event/Notice", "Manage Existing Events/Notices"])

    with tab1:
        st.subheader("Add New Event or Notice")
        with st.form("add_event_form", clear_on_submit=True):
            event_type = st.radio("Select Type", ["Event", "Notice"])
            title = st.text_input("Title*").strip()
            description = st.text_area("Description*").strip()
            if event_type == "Event":
                event_date = st.date_input("Event Date*", min_value=datetime.today().date())
                event_time = st.time_input("Event Time*", value=datetime.now().time())
                venue = st.text_input("Venue (Optional)").strip()
            else:
                event_date = None
                event_time = None
                venue = None

            if st.form_submit_button("Add Event/Notice"):
                if not title or not description:
                    st.error("Please fill all required fields.")
                else:
                    new_id = str(uuid.uuid4())
                    event_notice_data[new_id] = {
                        "id": new_id,
                        "type": event_type,
                        "title": title,
                        "description": description,
                        "date_posted": str(datetime.today().date()),
                        "event_date": str(event_date) if event_date else None,
                        "event_time": str(event_time) if event_time else None,
                        "venue": venue
                    }
                    save_data(event_notice_data, EVENT_NOTICE_DATA_FILE)
                    st.success(f"{event_type} '{title}' added successfully!")
                    st.rerun()

    with tab2:
        st.subheader("Manage Existing Events/Notices")
        events_notices_list = list(event_notice_data.values())
        if not events_notices_list:
            st.info("No events or notices available.")
            return

        df_events_notices = pd.DataFrame(events_notices_list)
        df_events_notices_display = df_events_notices.drop(columns=['id'], errors='ignore')
        st.dataframe(df_events_notices_display, use_container_width=True)

        st.subheader("Delete Event/Notice")
        event_notice_titles = [f"{e['title']} ({e['date_posted']})" for e in events_notices_list]
        selected_title = st.selectbox("Select Event/Notice to Delete", [""] + sorted(event_notice_titles), key="delete_event_notice_select")

        if selected_title:
            selected_event_notice_obj = next((e for e in events_notices_list if f"{e['title']} ({e['date_posted']})" == selected_title), None)
            if selected_event_notice_obj:
                st.warning(f"Are you sure you want to delete '{selected_event_notice_obj['title']}'?")
                if st.button("Confirm Delete", key=f"confirm_delete_event_{selected_event_notice_obj['id']}"):
                    del event_notice_data[selected_event_notice_obj['id']]
                    save_data(event_notice_data, EVENT_NOTICE_DATA_FILE)
                    st.success("Event/Notice deleted successfully.")
                    st.rerun()

def view_dashboard_teacher_student():
    """This function simulates the teacher/student dashboard view.
    It shows notices, timetable, assignments, etc.
    It is not an admin view."""
    st.title("🏛️ School Management System")
    st.header("Dashboard Overview")

    # Display Notices/Events
    event_notice_data = st.session_state.event_notice_data
    if event_notice_data:
        st.subheader("📢 Latest School Notices & Events")
        sorted_notices = sorted(
            event_notice_data.values(),
            key=lambda x: datetime.strptime(x.get('date_posted', '1900-01-01'), '%Y-%m-%d'),
            reverse=True
        )
        for notice in sorted_notices:
            with st.expander(f"**{notice['title']}** - ({notice['type']})"):
                st.write(f"**Date Posted:** {notice.get('date_posted')}")
                if notice.get('event_date'):
                    st.write(f"**Event Date:** {notice['event_date']}")
                if notice.get('event_time'):
                    st.write(f"**Event Time:** {notice['event_time']}")
                if notice.get('venue'):
                    st.write(f"**Venue:** {notice['venue']}")
                st.write("---")
                st.write(notice['description'])
    else:
        st.info("No current notices or events to display.")


def show():
    """Main application logic and layout."""
    st.set_page_config(
        page_title="School Management System",
        page_icon="🏛️",
        layout="wide"
    )

    st.sidebar.title("Navigation")
    
    # This code assumes direct entry to the admin dashboard, as requested by the user.
    # No login/register options will be displayed.
    
    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Overview", "Students", "Teachers", "Classes", "Fees", "Events & Notices"],
            icons=['house', 'mortarboard', 'person-video', 'building', 'currency-dollar', 'bell'],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Overview":
        display_overview_dashboard()
    elif selected == "Students":
        manage_students_admin()
    elif selected == "Teachers":
        manage_teachers_admin()
    elif selected == "Classes":
        manage_classes_admin()
    elif selected == "Fees":
        manage_fee_admin()
    elif selected == "Events & Notices":
        manage_events_notices_admin()

if __name__ == "__main__":
    show()

