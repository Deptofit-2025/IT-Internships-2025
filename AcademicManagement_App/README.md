**Academic Management System**
This is a comprehensive Academic Management System designed to streamline and automate various administrative, teaching, and parental tasks for a school or educational institution. The system is built using Python and the Streamlit framework, providing an intuitive, web-based interface for different user roles.

Features by Module
**Admin Dashboard**
This module provides administrators with a centralized control center for school operations.

Student Management: Admins can add, edit, and delete student records.

Teacher Management: Tools to manage teacher profiles and information.

Class & Timetable Management: Assign teachers to classes and manage student enrollment.

Fee Management: A system to record and track student fee payments.

Events & Notices: A platform to publish and manage school-wide announcements and event information.

Data Persistence: All data is stored in local JSON files within a data directory.

**Teacher Portal**
This module provides teachers with a robust set of tools to manage their daily academic and administrative tasks.

Attendance Tracking: Easily mark and save student attendance on a daily basis.

Assignments & Grading: Create new assignments, manage due dates, and grade student submissions.

Timetable Management: View and edit personal class schedules.

Performance Tracking: Enter marks for exams and tests and view student performance over time.

Communication with Parents: Send direct messages to parents of students in a teacher's class.

Resource Sharing: Upload and share academic resources with other faculty members.

Leave Management: Apply for leave and track the status of applications.

School Essentials: A simple portal to order school supplies and stationery.

**Parent Portal**
This module is a secure and intuitive interface for parents to interact with the school and monitor their child's progress.

Secure Authentication: Parents can register and log in using their child's unique admission number.

Personalized Dashboard: A high-level overview of the child's academic and attendance status.

Attendance & Performance Tracking: Detailed views of a child's attendance history and subject-wise academic scores.

School Communications: Access to school notices, events, and their child's class timetable.

Fee Management: View current fee status and payment history.

Messaging System: A direct communication channel for parents to send messages to teachers or school administration.

Assignments & Resources: View assignments with due dates and download learning resources.

Leave Application: A form to easily submit leave applications for a child.

**Technologies Used**
Python: The core programming language for the application.

Streamlit: For building the interactive, web-based user interface.

Pandas: For efficient data handling, especially for bulk operations and analytics.

Streamlit Option Menu: A custom component for a clean sidebar navigation menu.

Hashing: Used with SHA-256 for securing passwords for all user accounts.

Getting Started
Prerequisites
Python 3.7 or higher

pip (Python package installer)

**Installation**
Clone this repository or download the dashboard.py file.
**
Bash**

git clone <repository-url>
cd <repository-folder>
Install the required Python libraries. It's recommended to use a virtual environment.

Bash

pip install streamlit pandas streamlit-option-menu
How to Run
From your terminal, navigate to the directory containing dashboard.py.

Run the application using the streamlit run command.

Bash

streamlit run dashboard.py
Your default web browser will open and display the application.

**Project Structure**
.
├── data/
│   ├── attachments/
│   ├── attendance_data.json
│   ├── assignments_data.json
│   ├── leave_attachments/
│   ├── leave_data.json
│   ├── messages_data.json
│   ├── orders_data.json
│   ├── performance_data.json
│   ├── resources_data.json
│   ├── student_data.json
│   ├── submissions/
│   ├── teacher_data.json
│   ├── timetable_data.json
│   ├── class_data.json
│   ├── fee_data.json
│   ├── event_notice_data.json
│   └── ...
├── dashboard.py     # Main application file
└── README.md
The dashboard.py file contains the complete code for all modules of the application.

The data/ directory is automatically created upon the first run and stores all application data in JSON files, ensuring data persistence between sessions.
