# database/db.py
import sqlite3
import os
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime, date
import pandas as pd

def init_db():
    def __init__(self, db_path='school.db'):
        self.db_path=db_path
        self.init_db()
    
    
        try:
            os.makedirs("data", exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Teachers table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    subject TEXT,
                    join_date DATE,
                    profile_pic TEXT
                )""")
                
                # Classes table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL UNIQUE,
                    academic_year TEXT
                )""")
                
                # Teacher-Class association
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER,
                    class_id INTEGER,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    UNIQUE(teacher_id, class_id)
                )""")
                
                # Students table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    class_id INTEGER,
                    parent_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id)
                )""")
                
                # Parents table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS parents (
                    parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT
                )""")
                
                # Attendance table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    class_id INTEGER,
                    date DATE NOT NULL,
                    status TEXT CHECK(status IN ('Present', 'Absent', 'Late')),
                    teacher_id INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                    UNIQUE(student_id, date)
                )""")
                
                # Assignments table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date DATE,
                    class_id INTEGER,
                    teacher_id INTEGER,
                    max_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                )""")
                
                # Submissions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER,
                    student_id INTEGER,
                    submission_text TEXT,
                    submission_date DATE,
                    grade INTEGER,
                    feedback TEXT,
                    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )""")
                
                # Timetable table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS timetable (
                    timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day TEXT NOT NULL,
                    period INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    class_id INTEGER,
                    teacher_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                    UNIQUE(day, period, class_id)
                )""")
                
                # Messages table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER,
                    student_id INTEGER,
                    parent_id INTEGER,
                    message_type TEXT,
                    subject TEXT,
                    message TEXT,
                    urgency TEXT,
                    sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pending',
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
                )""")
                
                # Resources table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    resource_type TEXT,
                    class_id INTEGER,
                    teacher_id INTEGER,
                    filename TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                )""")
                
                # Leave applications table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS leave_applications (
                    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER,
                    leave_type TEXT,
                    start_date DATE,
                    end_date DATE,
                    reason TEXT,
                    status TEXT DEFAULT 'Pending',
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
                )""")
                
                # Performance table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    subject TEXT,
                    average REAL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )""")
                cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        grade TEXT NOT NULL,
                        attendance REAL DEFAULT 0,
                        parent_id INTEGER)''')
            
            # Attendance table
                cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY,
                        student_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        status TEXT NOT NULL,
                        FOREIGN KEY(student_id) REFERENCES students(id))''')
            
            conn.commit()

    

                
        except Exception as e:
            raise Exception(f"Database initialization failed: {str(e)}")
    def _insert_sample_data(self):
        """Insert sample data for testing"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Check if sample data already exists
            c.execute("SELECT COUNT(*) FROM students")
            if c.fetchone()[0] == 0:
                # Insert sample student
                c.execute("INSERT INTO students (name, grade, attendance, parent_id) VALUES (?, ?, ?, ?)",
                          ('John Doe', '5', 95.5, 1))
                
                # Insert sample attendance
                from datetime import date, timedelta
                for i in range(30):
                    day = date.today() - timedelta(days=i)
                    status = 'Present' if i % 5 != 0 else 'Absent'  # Absent every 5th day
                    c.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                              (1, day, status))
                
                conn.commit()

    def get_students(self, parent_id: int = None) -> List[Tuple]:
        """Get all students or students for a specific parent"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # For column access by name
            c = conn.cursor()
            if parent_id:
                c.execute("SELECT id, name, grade, attendance FROM students WHERE parent_id=?", (parent_id,))
            else:
                c.execute("SELECT id, name, grade, attendance FROM students")
            return c.fetchall()

    def get_attendance_history(self, student_id: int) -> List[Tuple]:
        """Get attendance history for a student"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT date, status FROM attendance WHERE student_id=? ORDER BY date DESC", (student_id,))
            return c.fetchall()
    # ========== TEACHER METHODS ==========
    def get_teacher_by_id(self, teacher_id: int) -> Optional[Dict]:
        """Get teacher details by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE teacher_id=?", (teacher_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_teacher_profile(self, teacher_id: int, email: str, phone: str) -> bool:
        """Update teacher profile information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE teachers SET email=?, phone=? WHERE teacher_id=?",
                (email, phone, teacher_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_classes_by_teacher(self, teacher_id: int) -> List[Dict]:
        """Get all classes taught by a teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, c.class_name 
                FROM classes c
                JOIN teacher_classes tc ON c.class_id = tc.class_id
                WHERE tc.teacher_id=?
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== ATTENDANCE METHODS ==========
    def save_attendance(self, attendance_data: List[Dict]) -> bool:
        """Save attendance records for multiple students"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First delete any existing attendance for these students on this date
            for record in attendance_data:
                cursor.execute("""
                    DELETE FROM attendance 
                    WHERE student_id=? AND date=?
                """, (record['student_id'], record['date']))
            
            # Insert new attendance records
            cursor.executemany("""
                INSERT INTO attendance (student_id, class_id, date, status, teacher_id)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (r['student_id'], r['class_id'], r['date'], r['status'], r['teacher_id']) 
                for r in attendance_data
            ])
            
            conn.commit()
            return True

    def get_attendance_by_date_class(self, date: date, class_id: int) -> List[Dict]:
        """Get attendance records for a specific date and class"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE date=? AND class_id=?
            """, (date, class_id))
            return [dict(row) for row in cursor.fetchall()]

    # ========== STUDENT METHODS ==========
    def get_students_by_class(self, class_id: int) -> List[Dict]:
        """Get all students in a specific class"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, s.class_id, c.class_name 
                FROM students s
                JOIN classes c ON s.class_id = c.class_id
                WHERE s.class_id=?
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_parent_by_student(self, student_id: int) -> Optional[Dict]:
        """Get parent details for a specific student"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.* FROM parents p
                JOIN students s ON p.parent_id = s.parent_id
                WHERE s.student_id=?
            """, (student_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ========== ASSIGNMENT METHODS ==========
    def create_assignment(self, title: str, description: str, due_date: date, 
                        class_id: int, teacher_id: int, max_score: int) -> int:
        """Create a new assignment"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assignments (title, description, due_date, class_id, teacher_id, max_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, due_date, class_id, teacher_id, max_score))
            conn.commit()
            return cursor.lastrowid

    def get_assignments_by_teacher(self, teacher_id: int) -> List[Dict]:
        """Get all assignments created by a teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, c.class_name 
                FROM assignments a
                JOIN classes c ON a.class_id = c.class_id
                WHERE a.teacher_id=?
                ORDER BY a.due_date
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_submissions_by_assignment(self, assignment_id: int) -> List[Dict]:
        """Get all submissions for a specific assignment"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, st.name as student_name, a.max_score
                FROM submissions s
                JOIN students st ON s.student_id = st.student_id
                JOIN assignments a ON s.assignment_id = a.assignment_id
                WHERE s.assignment_id=?
            """, (assignment_id,))
            return [dict(row) for row in cursor.fetchall()]

    def grade_submission(self, submission_id: int, grade: int, feedback: str) -> bool:
        """Grade a student submission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE submissions 
                SET grade=?, feedback=?
                WHERE submission_id=?
            """, (grade, feedback, submission_id))
            conn.commit()
            return cursor.rowcount > 0

    # ========== TIMETABLE METHODS ==========
    def get_teacher_timetable(self, teacher_id: int) -> List[Dict]:
        """Get timetable for a specific teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, c.class_name 
                FROM timetable t
                JOIN classes c ON t.class_id = c.class_id
                WHERE t.teacher_id=?
                ORDER BY 
                    CASE t.day
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        WHEN 'Sunday' THEN 7
                    END,
                    t.period
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== PERFORMANCE METHODS ==========
    def get_class_performance(self, class_id: int) -> List[Dict]:
        """Get performance data for all students in a class"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, p.subject, p.average
                FROM students s
                JOIN performance p ON s.student_id = p.student_id
                WHERE s.class_id=?
            """, (class_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_student_performance(self, student_id: int) -> List[Dict]:
        """Get performance data for a specific student"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM performance
                WHERE student_id=?
            """, (student_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== COMMUNICATION METHODS ==========
    def send_message(self, teacher_id: int, student_id: int, parent_id: int,
                    message_type: str, subject: str, message: str, urgency: str) -> int:
        """Send a message to a parent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (teacher_id, student_id, parent_id, message_type, subject, message, urgency)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (teacher_id, student_id, parent_id, message_type, subject, message, urgency))
            conn.commit()
            return cursor.lastrowid

    def get_teacher_messages(self, teacher_id: int) -> List[Dict]:
        """Get all messages sent by a teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.*, s.name as student_name 
                FROM messages m
                JOIN students s ON m.student_id = s.student_id
                WHERE m.teacher_id=?
                ORDER BY m.sent_date DESC
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    def cancel_message(self, message_id: int) -> bool:
        """Cancel a pending message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM messages 
                WHERE message_id=? AND status='Pending'
            """, (message_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ========== RESOURCE METHODS ==========
    def add_resource(self, title: str, description: str, resource_type: str,
                    class_id: Optional[int], teacher_id: int, filename: str) -> int:
        """Add a new teaching resource"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resources (title, description, resource_type, class_id, teacher_id, filename)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, resource_type, class_id, teacher_id, filename))
            conn.commit()
            return cursor.lastrowid

    def get_teacher_resources(self, teacher_id: int) -> List[Dict]:
        """Get all resources uploaded by a teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, c.class_name 
                FROM resources r
                LEFT JOIN classes c ON r.class_id = c.class_id
                WHERE r.teacher_id=?
                ORDER BY r.upload_date DESC
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    # ========== LEAVE METHODS ==========
    def apply_leave(self, teacher_id: int, leave_type: str, start_date: date,
                   end_date: date, reason: str, status: str = "Pending") -> int:
        """Apply for leave"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leave_applications (teacher_id, leave_type, start_date, end_date, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (teacher_id, leave_type, start_date, end_date, reason, status))
            conn.commit()
            return cursor.lastrowid

    def get_teacher_leaves(self, teacher_id: int) -> List[Dict]:
        """Get all leave applications for a teacher"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM leave_applications
                WHERE teacher_id=?
                ORDER BY application_date DESC
            """, (teacher_id,))
            return [dict(row) for row in cursor.fetchall()]

    def cancel_leave(self, leave_id: int) -> bool:
        """Cancel a pending leave application"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM leave_applications 
                WHERE leave_id=? AND status='Pending'
            """, (leave_id,))
            conn.commit()
            return cursor.rowcount > 0

