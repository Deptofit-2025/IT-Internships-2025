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
# DATA MANAGEMENT (Consistent with other modules)
# ======================

def load_data(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.error(f"Error decoding JSON from {filename}. File might be corrupted or empty. Returning empty dict.")
                return {}
    return {}

def save_data(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize data files paths
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True) # Ensure data directory exists
os.makedirs(os.path.join(DATA_DIR, "attachments"), exist_ok=True) # Ensure attachments directory exists
os.makedirs(os.path.join(DATA_DIR, "submissions"), exist_ok=True) # Ensure submissions directory exists

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

# ======================
# SECURITY & AUTHENTICATION (Parent Specific)
# ======================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_parent(admission_no, password):
    """Authenticate parent credentials using student admission number and parent password"""
    student_data = load_data(STUDENT_DATA_FILE)
    for class_name, students in student_data.items():
        for student in students:
            if student.get('admission_no') == admission_no and student.get('parent_password') == hash_password(password):
                return student # Return the student object if authenticated
    return None

def register_parent_page():
    """Display parent registration page and handle registration"""
    st.title("👨‍👩‍👧‍👦 School Management System - Parent Registration")
    st.info("Register as a parent using your child's Student Admission Number and create a password.")

    with st.form("parent_register_form"):
        student_admission_no = st.text_input("Child's Student Admission Number*", help="Enter the unique admission number provided by the school.").strip()
        parent_name = st.text_input("Your Full Name (Parent/Guardian)*").strip()
        parent_email = st.text_input("Your Email (Optional)").strip()
        parent_phone = st.text_input("Your Phone (Optional)").strip()
        new_password = st.text_input("Choose Your Password*", type="password")
        confirm_password = st.text_input("Confirm Password*", type="password")

        if st.form_submit_button("Register Parent Account"):
            if not all([student_admission_no, parent_name, new_password, confirm_password]):
                st.error("Please fill all required fields (*)")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                student_data = load_data(STUDENT_DATA_FILE)
                student_found = False
                for class_name, students in student_data.items():
                    for i, student in enumerate(students):
                        if student.get('admission_no') == student_admission_no:
                            # Check if parent account already exists for this student admission number
                            if student.get('parent_password'):
                                st.error(f"A parent account already exists for Student Admission Number {student_admission_no}. Please login or contact school administration.")
                                return

                            # Update student record with parent info and hashed password
                            student_data[class_name][i]['parent_name'] = parent_name
                            student_data[class_name][i]['parent_email'] = parent_email
                            student_data[class_name][i]['parent_phone'] = parent_phone
                            student_data[class_name][i]['parent_password'] = hash_password(new_password)
                            save_data(student_data, STUDENT_DATA_FILE)
                            st.success(f"Parent account for Student Admission Number {student_admission_no} registered successfully! You can now login.")
                            st.session_state['show_parent_login'] = True # After registration, show login
                            student_found = True
                            st.rerun()
                            break
                    if student_found:
                        break
                
                if not student_found:
                    st.error(f"Student Admission Number {student_admission_no} not found. Please ensure you enter the correct number.")


def parent_login_or_register_page():
    """Display options for parent login or registration"""
    st.title("👨‍👩‍👧‍👦 School Management System - Parent Portal")

    if 'show_parent_login' not in st.session_state:
        st.session_state['show_parent_login'] = True # Default to showing login first

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login as Parent", key="parent_login_option_btn"):
            st.session_state['show_parent_login'] = True
    with col2:
        if st.button("Register Parent Account", key="parent_register_option_btn"):
            st.session_state['show_parent_login'] = False

    st.markdown("---") # Separator

    if st.session_state['show_parent_login']:
        st.subheader("Parent Login")
        with st.form("parent_login_form"):
            admission_no_input = st.text_input("Child's Admission Number", key="parent_login_admission_no").strip()
            password = st.text_input("Your Password", type="password")

            if st.form_submit_button("Login"):
                authenticated_student = authenticate_parent(admission_no_input, password)
                if authenticated_student:
                    st.session_state['parent_logged_in'] = True
                    st.session_state['logged_in_student'] = authenticated_student # Store the full student object
                    st.rerun()
                else:
                    st.error("Invalid Admission Number or password. Please ensure you have registered an account.")
    else:
        register_parent_page()

# ======================
# PARENT MODULE FUNCTIONS
# ======================

def display_parent_dashboard(student_info):
    """Display parent dashboard overview"""
    st.header(f"👋 Welcome, {student_info.get('parent_name', 'Parent')}!")
    st.subheader(f"Dashboard for {student_info['name']} ({student_info['class']})")

    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Child's Class", student_info['class'])
    with col2:
        st.metric("Child's Admission Number", student_info.get('admission_no', 'N/A')) # Display admission_no

    st.markdown("---")
    st.subheader("Quick Overview")

    # Latest Attendance
    attendance_data = load_data(ATTENDANCE_DATA_FILE)
    latest_attendance = "N/A"
    if attendance_data:
        for teacher_attn in attendance_data.values():
            for date_str, class_attn in teacher_attn.items():
                if student_info['class'] in class_attn:
                    # Use student's internal ID for attendance lookup
                    if str(student_info['id']) in class_attn[student_info['class']]:
                        latest_attendance = f"{date_str}: {class_attn[student_info['class']][str(student_info['id'])]}"
                        break # Found latest for this student
            if latest_attendance != "N/A":
                break
    st.info(f"**Latest Attendance:** {latest_attendance}")

    # Latest Academic Performance
    performance_data = load_data(PERFORMANCE_DATA_FILE)
    latest_performance = "N/A"
    if performance_data:
        for teacher_perf in performance_data.values():
            if student_info['class'] in teacher_perf:
                for student_perf_record in teacher_perf[student_info['class']]:
                    # Use student's internal ID for performance lookup
                    if student_perf_record['student_id'] == student_info['id']:
                        latest_performance = f"Overall Average: {student_perf_record['average']:.2f}%"
                        break
            if latest_performance != "N/A":
                break
    st.info(f"**Academic Performance:** {latest_performance}")

    # Upcoming Events/Notices
    event_notice_data = load_data(EVENT_NOTICE_DATA_FILE)
    upcoming_events = []
    today = datetime.today().date()
    if event_notice_data:
        for entry_id, entry in event_notice_data.items():
            if entry['type'] == "Event" and entry['event_date']:
                event_date = datetime.strptime(entry['event_date'], '%Y-%m-%d').date()
                if event_date >= today:
                    # Check target audience
                    target_audience = entry.get('target_audience', ['All'])
                    if "All" in target_audience or "Parents" in target_audience or student_info['class'] in target_audience:
                        upcoming_events.append(f"{entry['event_date']} - {entry['title']}")
        
        if upcoming_events:
            st.subheader("Upcoming Events")
            for event in sorted(upcoming_events):
                st.write(f"- {event}")
        else:
            st.info("No upcoming events.")

def view_attendance_performance(student_info):
    """View attendance and academic performance for the child"""
    st.header(f"📈 {student_info['name']}'s Progress Report")

    st.subheader("Attendance Records")
    attendance_data = load_data(ATTENDANCE_DATA_FILE)
    student_attendance_records = []
    
    if attendance_data:
        for teacher_id, teacher_attn in attendance_data.items():
            for date_str, class_attn in teacher_attn.items():
                if student_info['class'] in class_attn:
                    if str(student_info['id']) in class_attn[student_info['class']]:
                        student_attendance_records.append({
                            "Date": date_str,
                            "Status": class_attn[student_info['class']][str(student_info['id'])]
                        })
    
    if student_attendance_records:
        df_attendance = pd.DataFrame(student_attendance_records)
        df_attendance['Date'] = pd.to_datetime(df_attendance['Date'])
        df_attendance = df_attendance.sort_values(by='Date', ascending=False).reset_index(drop=True)
        st.dataframe(df_attendance, use_container_width=True)
    else:
        st.info("No attendance records found for your child.")

    st.subheader("Academic Performance")
    performance_data = load_data(PERFORMANCE_DATA_FILE)
    student_performance_record = None

    if performance_data:
        for teacher_id, classes_perf in performance_data.items():
            if student_info['class'] in classes_perf:
                for student_perf in classes_perf[student_info['class']]:
                    if student_perf['student_id'] == student_info['id']:
                        student_performance_record = student_perf
                        break
            if student_performance_record:
                break
    
    if student_performance_record:
        st.write(f"**Overall Average:** {student_performance_record['average']:.2f}%")
        if student_performance_record.get('subjects'):
            st.write("**Subject-wise Performance:**")
            df_subjects = pd.DataFrame(student_performance_record['subjects'])
            st.dataframe(df_subjects, use_container_width=True)
        else:
            st.info("No detailed subject-wise performance available.")
    else:
        st.info("No academic performance data found for your child.")


def access_notices_events_timetables(student_info):
    """Access notices, events, and timetables"""
    st.header("School Communications & Schedule")

    tab1, tab2 = st.tabs(["Notices & Events", "Class Timetable"])

    with tab1:
        st.subheader("Notices & Events")
        event_notice_data = load_data(EVENT_NOTICE_DATA_FILE)
        
        if not event_notice_data:
            st.info("No notices or events published yet.")
            return

        all_entries = list(event_notice_data.values())
        
        # Filter for relevant entries: "All", "Parents", or child's class
        relevant_entries = []
        for entry in all_entries:
            target_audience = entry.get('target_audience', ['All'])
            if "All" in target_audience or "Parents" in target_audience or student_info['class'] in target_audience:
                relevant_entries.append(entry)

        if not relevant_entries:
            st.info("No notices or events relevant to your child's class or parents.")
            return

        # Sort by date
        relevant_entries.sort(key=lambda x: datetime.strptime(x.get('event_date', x['publish_date']), '%Y-%m-%d'), reverse=True)

        for entry in relevant_entries:
            with st.expander(f"{entry['type']}: {entry['title']} (Published: {entry['publish_date']})"):
                st.write(f"**Type:** {entry['type']}")
                st.write(f"**Title:** {entry['title']}")
                st.write(f"**Content:** {entry['content']}")
                if entry['type'] == "Event":
                    st.write(f"**Event Date:** {entry['event_date']}")
                    st.write(f"**Event Time:** {entry['event_time']}")
                    st.write(f"**Location:** {entry['location']}")
                st.write(f"**Target Audience:** {', '.join(entry['target_audience'])}")
                
                if entry['attachment']:
                    attachment_path = entry['attachment']['path']
                    if os.path.exists(attachment_path):
                        with open(attachment_path, "rb") as file:
                            st.download_button(
                                label=f"Download Attachment: {entry['attachment']['name']}",
                                data=file.read(),
                                file_name=entry['attachment']['name'],
                                mime=entry['attachment']['type'],
                                key=f"parent_download_{entry['id']}"
                            )
                    else:
                        st.warning(f"Attachment file not found: {entry['attachment']['name']}")


    with tab2:
        st.subheader(f"{student_info['name']}'s Class Timetable")
        timetable_data_all_teachers = load_data(TIMETABLE_DATA_FILE)
        student_class_timetable = []

        if timetable_data_all_teachers:
            for teacher_id, entries in timetable_data_all_teachers.items():
                teacher_name = load_data(TEACHER_DATA_FILE).get(teacher_id, {}).get('name', f"Teacher {teacher_id}")
                for entry in entries:
                    if entry['class_name'] == student_info['class']:
                        student_class_timetable.append({
                            "Day": entry['day'],
                            "Period": entry['period'],
                            "Subject": entry['subject'],
                            "Teacher": teacher_name
                        })
        
        if student_class_timetable:
            df_timetable = pd.DataFrame(student_class_timetable)
            # Order by Day and Period for better display
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df_timetable['Day'] = pd.Categorical(df_timetable['Day'], categories=day_order, ordered=True)
            df_timetable = df_timetable.sort_values(by=['Day', 'Period']).reset_index(drop=True)
            st.dataframe(df_timetable, use_container_width=True)
        else:
            st.info("No timetable entries found for your child's class yet.")

def manage_fee_payment(student_info):
    """Handle fee payment and display receipts"""
    st.header("💲 Fee Payment & Receipts")

    fee_data = load_data(FEE_DATA_FILE)
    # Fee data is keyed by student's internal ID
    student_fee_record = fee_data.get(str(student_info['id']))

    if not student_fee_record:
        st.info("No fee record found for your child. Please contact school administration.")
        return

    st.subheader(f"Current Fee Status for {student_info['name']}")
    st.metric("Amount Due", f"₹{student_fee_record['amount_due']:.2f}")
    st.metric("Amount Paid", f"₹{student_fee_record['amount_paid']:.2f}")
    st.metric("Outstanding Balance", f"₹{student_fee_record['amount_due'] - student_fee_record['amount_paid']:.2f}")
    st.metric("Last Payment Date", student_fee_record['last_payment_date'])

    st.markdown("---")
    st.subheader("Record a Payment (Simulated)")
    st.warning("Note: This is a simulated payment. No actual money is transferred.")

    with st.form("parent_fee_payment_form", clear_on_submit=True):
        payment_amount = st.number_input("Amount to Pay Now", min_value=0.0, value=0.0, format="%.2f")
        payment_date = st.date_input("Payment Date", value=datetime.today().date())
        payment_method = st.selectbox("Payment Method", ["Online Transfer", "Cash (Paid at School)", "Cheque"])
        
        if st.form_submit_button("Submit Payment"):
            if payment_amount <= 0:
                st.error("Please enter a valid amount to pay.")
            elif payment_amount > (student_fee_record['amount_due'] - student_fee_record['amount_paid']):
                st.warning("Payment amount exceeds outstanding balance. Adjusting to cover remaining balance.")
                payment_amount = student_fee_record['amount_due'] - student_fee_record['amount_paid']
                
            if payment_amount > 0:
                student_fee_record['amount_paid'] += payment_amount
                student_fee_record['last_payment_date'] = str(payment_date)
                
                # Generate a simple receipt number (UUID for uniqueness)
                receipt_number = f"REC-{str(uuid.uuid4().int)[:6]}"
                
                student_fee_record['payment_history'].append({
                    "date": str(payment_date),
                    "amount": payment_amount,
                    "method": payment_method,
                    "receipt": receipt_number
                })
                fee_data[str(student_info['id'])] = student_fee_record
                save_data(fee_data, FEE_DATA_FILE)
                st.success(f"Payment of ₹{payment_amount:.2f} recorded. Receipt No: {receipt_number}")
                st.rerun()
            else:
                st.info("No payment was made.")

    st.markdown("---")
    st.subheader("Payment History / Receipts")
    if student_fee_record.get('payment_history'):
        df_history = pd.DataFrame(student_fee_record['payment_history'])
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("No payment history found for your child.")

def messaging_system(student_info):
    """Messaging system for parents to communicate with teachers/admin"""
    st.header("💬 Messaging System")

    tab1, tab2 = st.tabs(["Compose New Message", "Message History"])

    with tab1:
        st.subheader("Compose New Message")
        teachers = load_data(TEACHER_DATA_FILE)
        teacher_options = {t['name']: t['id'] for t in teachers.values() if not t.get('is_admin', False)} # Exclude admins from direct teacher list
        
        # Add an "Admin" option
        admin_users = [t for t in teachers.values() if t.get('is_admin', False)]
        admin_option_name = "School Administration"
        if admin_users:
            teacher_options[admin_option_name] = admin_users[0]['id'] # Use first admin's ID for simplicity

        recipient_type = st.radio("Send message to:", ["Teacher", "School Administration"], horizontal=True)

        selected_recipient_id = None
        if recipient_type == "Teacher":
            selected_teacher_name = st.selectbox("Select Teacher", [""] + [name for name in teacher_options.keys() if name != admin_option_name]) # Exclude "School Administration" from direct teacher list
            if selected_teacher_name:
                selected_recipient_id = teacher_options[selected_teacher_name]
        else: # School Administration
            if admin_users:
                selected_recipient_id = admin_users[0]['id'] # Target the first admin
            else:
                st.warning("No admin user found to send messages to. Please contact school.")
                return

        with st.form("parent_new_message_form", clear_on_submit=True):
            subject = st.text_input("Subject*")
            content = st.text_area("Message Content*", height=150)
            
            if st.form_submit_button("Send Message"):
                if not all([selected_recipient_id, subject, content]):
                    st.error("Please select a recipient, subject, and content.")
                else:
                    messages_data = load_data(MESSAGES_DATA_FILE)
                    
                    # Ensure the recipient's message list exists
                    if selected_recipient_id not in messages_data:
                        messages_data[selected_recipient_id] = []

                    new_message = {
                        "id": str(uuid.uuid4()), # Use full UUID for messages
                        "date": str(datetime.today().date()),
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "subject": subject,
                        "content": content,
                        "sender_id": student_info['id'], # Parent is sending on behalf of student (using internal UUID)
                        "sender_type": "parent",
                        "sender_name": student_info.get('parent_name', f"Parent of {student_info['name']}"),
                        "recipient_id": selected_recipient_id,
                        "recipient_type": "teacher" if recipient_type == "Teacher" else "admin",
                        "status": "sent",
                        "read": False,
                        "related_student_id": student_info['id'], # Store internal student ID
                        "related_student_name": student_info['name']
                    }
                    messages_data[selected_recipient_id].append(new_message)
                    save_data(messages_data, MESSAGES_DATA_FILE)
                    st.success("Message sent successfully!")
                    st.rerun()

    with tab2:
        st.subheader("Your Message History")
        messages_data = load_data(MESSAGES_DATA_FILE)
        
        parent_sent_messages = []
        for recipient_id, messages_list in messages_data.items():
            for msg in messages_list:
                # Check if the message was sent by this parent (via their student's internal ID)
                if msg.get('sender_type') == 'parent' and msg.get('sender_id') == student_info['id']:
                    recipient_name = load_data(TEACHER_DATA_FILE).get(msg['recipient_id'], {}).get('name', 'Admin/Unknown')
                    parent_sent_messages.append({
                        "Date": msg['date'],
                        "Time": msg['time'],
                        "Recipient": recipient_name,
                        "Subject": msg['subject'],
                        "Content": msg['content'],
                        "Status": msg['status']
                    })
        
        if parent_sent_messages:
            df_messages = pd.DataFrame(parent_sent_messages)
            df_messages['Date'] = pd.to_datetime(df_messages['Date'])
            df_messages = df_messages.sort_values(by=['Date', 'Time'], ascending=False).reset_index(drop=True)
            st.dataframe(df_messages, use_container_width=True)
        else:
            st.info("No messages sent by you yet.")

        st.subheader("Messages from School (Teachers/Admin)")
        # This part requires teachers/admin to explicitly send messages to parents
        # For simplicity, we'll show messages where the student ID is mentioned in the message
        # or if the message is broadly targeted at the student's class or parents.
        
        received_messages = []
        all_event_notices = load_data(EVENT_NOTICE_DATA_FILE)
        for entry_id, entry in all_event_notices.items():
            target_audience = entry.get('target_audience', ['All'])
            if "All" in target_audience or "Parents" in target_audience or student_info['class'] in target_audience:
                received_messages.append({
                    "Date": entry['publish_date'],
                    "Time": "N/A",
                    "Sender": "School/Admin",
                    "Subject": f"[{entry['type']}] {entry['title']}",
                    "Content": entry['content'],
                    "Status": "Read" # Assume notices are read
                })
        
        # Also check direct messages from teachers if they are structured to target students/parents
        # (Current messages_data.json structure is teacher-centric, so this part is more complex)
        # For now, we'll rely on notices/events as the primary "received messages"
        
        if received_messages:
            df_received = pd.DataFrame(received_messages)
            df_received['Date'] = pd.to_datetime(df_received['Date'])
            df_received = df_received.sort_values(by='Date', ascending=False).reset_index(drop=True)
            st.dataframe(df_received, use_container_width=True)
        else:
            st.info("No direct messages from school or teachers yet.")


def download_assignments_notes(student_info):
    """Download assignments and notes relevant to the child's class"""
    st.header("📚 Assignments & Learning Resources")

    tab1, tab2 = st.tabs(["Assignments", "Learning Resources"])

    with tab1:
        st.subheader("Assignments for Your Child's Class")
        assignments_data = load_data(ASSIGNMENTS_DATA_FILE)
        relevant_assignments = []

        if assignments_data:
            for teacher_id, teacher_assignments in assignments_data.items():
                teacher_name = load_data(TEACHER_DATA_FILE).get(teacher_id, {}).get('name', f"Teacher {teacher_id}")
                for assignment in teacher_assignments:
                    if assignment['assigned_class'] == student_info['class']:
                        # Check if student has already submitted this assignment
                        submitted_status = "Not Submitted"
                        submission_id = None
                        for sub in assignment.get('submissions', []):
                            if sub.get('student_id') == student_info['id']:
                                submitted_status = sub.get('status', 'Submitted')
                                submission_id = sub.get('id')
                                break

                        relevant_assignments.append({
                            "ID": assignment['id'],
                            "Title": assignment['title'],
                            "Description": assignment['description'],
                            "Due Date": assignment['due_date'],
                            "Max Score": assignment['max_score'],
                            "Type": assignment['type'],
                            "Assigned By": teacher_name,
                            "Submission Status": submitted_status,
                            "Submission ID": submission_id # Store submission ID if exists
                        })
        
        if relevant_assignments:
            df_assignments = pd.DataFrame(relevant_assignments)
            df_assignments['Due Date'] = pd.to_datetime(df_assignments['Due Date'])
            df_assignments = df_assignments.sort_values(by='Due Date').reset_index(drop=True)
            st.dataframe(df_assignments, use_container_width=True)

            st.markdown("---")
            st.subheader("Submit Assignment")
            
            # Filter for assignments that are not yet submitted or can be resubmitted
            submittable_assignments = [
                a for a in relevant_assignments 
                if a['Submission Status'] == "Not Submitted" or a['Submission Status'] == "Needs Revision"
            ]

            if not submittable_assignments:
                st.info("No assignments available for submission or revision at this time.")
                return

            selected_assignment_to_submit_id = st.selectbox(
                "Select Assignment to Submit", 
                [""] + [a['ID'] for a in submittable_assignments],
                format_func=lambda x: next((a['Title'] for a in submittable_assignments if a['ID'] == x), "")
            )

            if selected_assignment_to_submit_id:
                selected_assignment_obj = next((a for a in relevant_assignments if a['ID'] == selected_assignment_to_submit_id), None)
                
                if selected_assignment_obj:
                    st.write(f"**Submitting for:** {selected_assignment_obj['Title']}")
                    
                    # Convert 'Due Date' string to datetime object before formatting
                    due_date_dt = datetime.strptime(selected_assignment_obj['Due Date'], '%Y-%m-%d').date()
                    st.write(f"**Due Date:** {due_date_dt.strftime('%Y-%m-%d')}")

                    with st.form(f"submit_assignment_form_{selected_assignment_to_submit_id}", clear_on_submit=True):
                        submission_text = st.text_area("Your Submission (Text)", height=150)
                        submission_file = st.file_uploader("Upload Submission File (Optional)", type=["pdf", "docx", "txt", "jpg", "png"])
                        
                        submit_button = st.form_submit_button("Submit Assignment")

                        if submit_button:
                            if not submission_text and not submission_file:
                                st.error("Please provide either text content or upload a file for submission.")
                            else:
                                # Find the actual assignment object in the assignments_data
                                found_assignment = None
                                for teacher_id_key, teacher_assignments_list in assignments_data.items():
                                    for i, assign in enumerate(teacher_assignments_list):
                                        if assign['id'] == selected_assignment_to_submit_id:
                                            found_assignment = assign
                                            teacher_of_assignment_id = teacher_id_key
                                            assignment_index = i
                                            break
                                    if found_assignment:
                                        break

                                if found_assignment:
                                    submission_file_path = None
                                    if submission_file:
                                        submission_filename = f"{selected_assignment_to_submit_id}_{student_info['id']}_{submission_file.name}"
                                        submission_save_path = os.path.join(DATA_DIR, "submissions", submission_filename)
                                        try:
                                            with open(submission_save_path, "wb") as f:
                                                f.write(submission_file.getvalue())
                                            submission_file_path = submission_save_path
                                        except Exception as e:
                                            st.error(f"Error saving submission file: {e}")
                                            submission_file_path = None

                                    new_submission = {
                                        "id": str(uuid.uuid4()),
                                        "student_id": student_info['id'],
                                        "student_name": student_info['name'],
                                        "submission_date": str(datetime.today().date()),
                                        "submission_time": datetime.now().strftime("%H:%M:%S"),
                                        "submission_text": submission_text,
                                        "submission_file_path": submission_file_path,
                                        "status": "Submitted",
                                        "grade": None,
                                        "feedback": ""
                                    }

                                    # Check if a submission already exists for this student for this assignment
                                    existing_submission_index = -1
                                    for i, sub in enumerate(found_assignment.get('submissions', [])):
                                        if sub.get('student_id') == student_info['id']:
                                            existing_submission_index = i
                                            break
                                    
                                    if existing_submission_index != -1:
                                        # Update existing submission
                                        found_assignment['submissions'][existing_submission_index] = new_submission
                                        st.success("Assignment resubmitted successfully!")
                                    else:
                                        # Add new submission
                                        if 'submissions' not in found_assignment:
                                            found_assignment['submissions'] = []
                                        found_assignment['submissions'].append(new_submission)
                                        st.success("Assignment submitted successfully!")
                                    
                                    # Update the assignments_data in the main dict and save
                                    assignments_data[teacher_of_assignment_id][assignment_index] = found_assignment
                                    save_data(assignments_data, ASSIGNMENTS_DATA_FILE)
                                    st.rerun()
                                else:
                                    st.error("Selected assignment not found in data.")
            else:
                st.info("Please select an assignment to submit.")

        else:
            st.info("No assignments found for your child's class.")

    with tab2:
        st.subheader("Learning Resources for Your Child's Class")
        resources_data = load_data(RESOURCES_DATA_FILE)
        relevant_resources = []

        # Determine subjects for the student's class from timetable data
        student_subjects = set()
        timetable_data_all_teachers = load_data(TIMETABLE_DATA_FILE)
        if timetable_data_all_teachers:
            for teacher_id, entries in timetable_data_all_teachers.items():
                for entry in entries:
                    if entry['class_name'] == student_info['class']:
                        student_subjects.add(entry['subject'])
        
        # Fallback if no subjects found in timetable (e.g., for Nursery/LKG/UKG or empty timetable)
        if not student_subjects:
            st.info("Could not determine specific subjects for your child's class from timetable. Displaying all relevant resources.")
            # If no specific subjects, show all resources assigned to the class or 'All Classes'
            for teacher_id, teacher_resources in resources_data.items():
                teacher_name = load_data(TEACHER_DATA_FILE).get(teacher_id, {}).get('name', f"Teacher {teacher_id}")
                for resource in teacher_resources:
                    if resource['class_name'] == student_info['class'] or resource['class_name'] == "All Classes":
                        relevant_resources.append({
                            "ID": resource['id'],
                            "Title": resource['title'],
                            "Description": resource['description'],
                            "Type": resource['type'],
                            "Tags": ", ".join(resource.get('tags', [])), # Use .get() defensively
                            "Uploaded By": teacher_name,
                            "Upload Date": resource['upload_date'],
                            "File Name": resource['file_name'],
                            "file_path": resource.get('file_path') # Use .get() defensively
                        })
        else:
            # Filter resources based on class or subject tags
            for teacher_id, teacher_resources in resources_data.items():
                teacher_name = load_data(TEACHER_DATA_FILE).get(teacher_id, {}).get('name', f"Teacher {teacher_id}")
                for resource in teacher_resources:
                    is_relevant_by_class = (resource['class_name'] == student_info['class'] or resource['class_name'] == "All Classes")
                    is_relevant_by_subject = any(tag in student_subjects for tag in resource.get('tags', []))

                    if is_relevant_by_class or is_relevant_by_subject:
                        relevant_resources.append({
                            "ID": resource['id'],
                            "Title": resource['title'],
                            "Description": resource['description'],
                            "Type": resource['type'],
                            "Tags": ", ".join(resource.get('tags', [])), # Use .get() defensively
                            "Uploaded By": teacher_name,
                            "Upload Date": resource['upload_date'],
                            "File Name": resource['file_name'],
                            "file_path": resource.get('file_path') # Use .get() defensively
                        })

    if relevant_resources:
        df_resources = pd.DataFrame(relevant_resources)
        df_resources['Upload Date'] = pd.to_datetime(df_resources['Upload Date'])
        df_resources = df_resources.sort_values(by='Upload Date', ascending=False).reset_index(drop=True)
        st.dataframe(df_resources[['Title', 'Description', 'Type', 'Tags', 'Uploaded By', 'Upload Date', 'File Name']], use_container_width=True)

        st.markdown("---")
        st.subheader("Download Resource Files")
        selected_resource_id = st.selectbox("Select Resource to Download", [""] + [r['ID'] for r in relevant_resources],
                                            format_func=lambda x: next((r['Title'] for r in relevant_resources if r['ID'] == x), ""))

        if selected_resource_id:
            resource_to_download = next((r for r in relevant_resources if r['ID'] == selected_resource_id), None)
            
            if resource_to_download and resource_to_download.get('file_path'):
                file_path = resource_to_download['file_path']
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"Download {resource_to_download['file_name']}",
                            data=file.read(),
                            file_name=resource_to_download['file_name'],
                            mime=resource_to_download['file_type']
                        )
                else:
                    st.error("File not found. It might have been moved or deleted.")
            else:
                st.warning("Please select a resource to enable download.")
    else:
        st.info("No learning resources found for your child's class or subjects.")


def apply_for_student_leave(student_info):
    """Allow parents to apply for leave on behalf of their child"""
    st.header(f"📝 Apply for Leave for {student_info['name']}")

    st.subheader("Submit New Leave Application")
    with st.form("student_leave_application_form", clear_on_submit=True):
        leave_type = st.selectbox("Leave Type*", ["Sick Leave", "Family Event", "Vacation", "Other"])
        start_date = st.date_input("Start Date*", min_value=datetime.today().date())
        end_date = st.date_input("End Date*", min_value=start_date)
        reason = st.text_area("Reason for Leave*", height=100)
        supporting_docs = st.file_uploader("Upload Supporting Documents (Optional)", type=["pdf", "jpg", "png", "docx"], accept_multiple_files=True)

        if st.form_submit_button("Submit Leave Application"):
            if not all([leave_type, start_date, end_date, reason]):
                st.error("Please fill all required fields (*)")
            elif start_date > end_date:
                st.error("End Date cannot be before Start Date.")
            else:
                leave_data = load_data(LEAVE_DATA_FILE)
                new_leave_id = str(uuid.uuid4()) # Use full UUID for leave ID
                
                # Calculate leave days (inclusive)
                leave_days = (end_date - start_date).days + 1

                # Handle supporting documents
                doc_paths = []
                if supporting_docs:
                    leave_docs_dir = os.path.join(DATA_DIR, "leave_attachments")
                    os.makedirs(leave_docs_dir, exist_ok=True)
                    for doc_file in supporting_docs:
                        doc_filename = f"{new_leave_id}_{doc_file.name}"
                        doc_path = os.path.join(leave_docs_dir, doc_filename)
                        try:
                            with open(doc_path, "wb") as f:
                                f.write(doc_file.getvalue())
                            doc_paths.append(doc_path)
                        except Exception as e:
                            st.warning(f"Could not save supporting document {doc.name}: {e}")

                # Store leave under a special key for student leaves, or a consolidated structure
                # Let's use a consolidated structure where 'target_type' differentiates
                
                new_leave_record = {
                    "id": new_leave_id,
                    "target_id": student_info['id'], # Use internal student ID (UUID)
                    "target_type": "student", # Important: differentiate from teacher leave
                    "target_name": student_info['name'],
                    "class_name": student_info['class'],
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "leave_days": leave_days,
                    "type": leave_type,
                    "reason": reason,
                    "status": "Pending", # Default status
                    "application_date": str(datetime.today().date()),
                    "applied_by": student_info.get('parent_name', f"Parent of {student_info['name']}"),
                    "supporting_docs": doc_paths,
                    "comments": "" # For admin comments
                }

                # Ensure 'student_leaves' key exists in leave_data
                if 'student_leaves' not in leave_data:
                    leave_data['student_leaves'] = []
                leave_data['student_leaves'].append(new_leave_record)
                
                save_data(leave_data, LEAVE_DATA_FILE)
                st.success("Leave application submitted successfully! Status: Pending review.")
                st.rerun()

    st.markdown("---")
    st.subheader("Your Child's Leave History")
    leave_data = load_data(LEAVE_DATA_FILE)
    student_leave_history = []

    if 'student_leaves' in leave_data:
        for leave in leave_data['student_leaves']:
            if leave.get('target_id') == student_info['id'] and leave.get('target_type') == 'student':
                student_leave_history.append({
                    "Leave ID": leave['id'],
                    "Type": leave['type'],
                    "Start Date": leave['start_date'],
                    "End Date": leave['end_date'],
                    "Days": leave.get('leave_days', 'N/A'),
                    "Reason": leave['reason'],
                    "Status": leave['status'],
                    "Applied On": leave['application_date']
                })
    
    if student_leave_history:
        df_leave_history = pd.DataFrame(student_leave_history)
        df_leave_history['Applied On'] = pd.to_datetime(df_leave_history['Applied On'])
        df_leave_history = df_leave_history.sort_values(by='Applied On', ascending=False).reset_index(drop=True)
        st.dataframe(df_leave_history, use_container_width=True)

        st.subheader("Cancel Pending Leave Application")
        pending_leaves = [l for l in student_leave_history if l['Status'] == 'Pending']
        if pending_leaves:
            leave_ids_to_cancel = [l['Leave ID'] for l in pending_leaves]
            selected_leave_to_cancel = st.selectbox("Select Leave ID to Cancel", [""] + leave_ids_to_cancel)

            if selected_leave_to_cancel:
                if st.button(f"Confirm Cancel Leave ID: {selected_leave_to_cancel}"):
                    found_and_canceled = False
                    if 'student_leaves' in leave_data:
                        for i, leave_obj in enumerate(leave_data['student_leaves']):
                            if leave_obj['id'] == selected_leave_to_cancel and leave_obj['status'] == 'Pending':
                                leave_data['student_leaves'][i]['status'] = 'Canceled'
                                save_data(leave_data, LEAVE_DATA_FILE)
                                st.success(f"Leave application {selected_leave_to_cancel} has been canceled.")
                                found_and_canceled = True
                                st.rerun()
                                break
                    if not found_and_canceled:
                        st.error("Could not cancel leave. It might not be pending or already processed.")
        else:
            st.info("No pending leave applications to cancel.")

    else:
        st.info("No leave applications submitted for your child yet.")


# ======================
# MAIN PARENT DASHBOARD
# ======================

def show():
    """Main function for the parent dashboard"""
    if 'parent_logged_in' not in st.session_state or not st.session_state['parent_logged_in']:
        parent_login_or_register_page()
        return

    student_info = st.session_state['logged_in_student']

    st.title(f"👨‍👩‍👧‍👦 Parent Portal - {student_info['name']}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

    st.sidebar.markdown(f"**Logged in as:** {student_info.get('parent_name', 'Parent')}")
    st.sidebar.markdown(f"**Child:** {student_info['name']} (Admission No: {student_info.get('admission_no', 'N/A')})") # Display admission_no
    st.sidebar.markdown(f"**Class:** {student_info['class']}")


    selected = option_menu(
        None,
        ["Dashboard", "Attendance & Performance", "Notices, Events & Timetable",
         "Fee Payment", "Messaging", "Assignments & Resources", "Apply for Leave"],
        icons=['house-door', 'graph-up', 'calendar3', 'currency-dollar',
               'chat-dots', 'book', 'file-earmark-text'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
            "nav-link-selected": {"background-color": "#007bff"}, # Parent theme blue
        }
    )

    if selected == "Dashboard":
        display_parent_dashboard(student_info)
    elif selected == "Attendance & Performance":
        view_attendance_performance(student_info)
    elif selected == "Notices, Events & Timetable":
        access_notices_events_timetables(student_info)
    elif selected == "Fee Payment":
        manage_fee_payment(student_info)
    elif selected == "Messaging":
        messaging_system(student_info)
    elif selected == "Assignments & Resources":
        download_assignments_notes(student_info)
    elif selected == "Apply for Leave":
        apply_for_student_leave(student_info)

# ======================
# INITIALIZATION (Updated to include parent_password in sample student data)
# ======================
# ... (previous code) ...

def initialize_all_data_files():
    """Initialize all data files with empty structures or sample data if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)

    # ... (other file initializations) ...

    # Special initialization for RESOURCES_DATA_FILE with sample data
    # Define sample_resources outside the if block to ensure it's always accessible
    sample_resources = {
        "1001": [ # Using teacher ID "1001" (John Doe)
            {
                "id": str(uuid.uuid4()),
                "title": "Introduction to Algebra",
                "description": "Lecture notes covering basic algebraic expressions and equations.",
                "type": "Lecture Notes",
                "class_name": "Grade 6A",
                "tags": ["Math", "Algebra"],
                "upload_date": "2023-01-10",
                "upload_time": "09:30",
                "file_name": "intro_algebra.pdf",
                "file_type": "application/pdf",
                "file_size": "500 KB",
                "uploaded_by": "John Doe",
                "download_count": 0,
                "file_path": os.path.join(DATA_DIR, "attachments", "intro_algebra.pdf") # Placeholder path
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Photosynthesis Process",
                "description": "Presentation slides on how plants make food.",
                "type": "Presentation",
                "class_name": "Grade 5B",
                "tags": ["Science", "Biology"],
                "upload_date": "2023-02-15",
                "upload_time": "11:00",
                "file_name": "photosynthesis.pptx",
                "file_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "file_size": "1.2 MB",
                "uploaded_by": "Jane Smith",
                "download_count": 0,
                "file_path": os.path.join(DATA_DIR, "attachments", "photosynthesis.pptx") # Placeholder path
            },
            {
                "id": str(uuid.uuid4()),
                "title": "World War II Overview",
                "description": "Summary notes for key events and figures of WWII.",
                "type": "Reference",
                "class_name": "All Classes", # Example for 'All Classes'
                "tags": ["History", "World Affairs"],
                "upload_date": "2023-03-20",
                "upload_time": "14:00",
                "file_name": "wwii_overview.pdf",
                "file_type": "application/pdf",
                "file_size": "800 KB",
                "uploaded_by": "John Doe",
                "download_count": 0,
                "file_path": os.path.join(DATA_DIR, "attachments", "wwii_overview.pdf") # Placeholder path
            }
        ]
    }

    if not os.path.exists(RESOURCES_DATA_FILE):
        save_data(sample_resources, RESOURCES_DATA_FILE)

    # Create attachments directories if they don't exist
    os.makedirs(os.path.join(DATA_DIR, "attachments"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "leave_attachments"), exist_ok=True)

    # Create dummy files for sample resources to make them downloadable
    # This loop is now safe because sample_resources is always defined
    for teacher_id, resources_list in sample_resources.items():
        for resource in resources_list:
            file_path = resource.get('file_path')
            if file_path and not os.path.exists(file_path):
                try:
                    # Create a dummy file with some content
                    with open(file_path, "w") as f:
                        f.write(f"This is a dummy file for {resource['title']}.\n")
                        f.write(f"Type: {resource['type']}\n")
                        f.write(f"Class: {resource['class_name']}\n")
                        f.write(f"Uploaded by: {resource['uploaded_by']}\n")
                    st.info(f"Created dummy file: {os.path.basename(file_path)}") # This will only show on initialization
                except Exception as e:
                    st.error(f"Could not create dummy file {os.path.basename(file_path)}: {e}")


# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    initialize_all_data_files() # Ensure all data files are initialized

    st.set_page_config(
        page_title="Parent Portal",
        page_icon="👨‍👩‍👧‍👦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
            .stButton button {
                width: 100%;
            }
            .stSelectbox, .stTextInput, .stTextArea, .stDateInput, .stFileUploader, .stNumberInput {
                margin-bottom: 1rem;
            }
            .stExpander {
                margin-bottom: 1rem;
                border: 1px solid #e1e4e8;
                border-radius: 0.5rem;
            }
            .stExpander .stMarkdown {
                padding: 1rem;
            }
            /* Parent specific primary color for selected menu item */
            div.st-emotion-cache-1jmveo1 > div {
                background-color: #007bff; /* Blue for parent selected */
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #F0F2F6;
                border-radius: 4px 4px 0px 0px;
                gap: 10px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #007bff; /* Active tab blue */
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    show()


