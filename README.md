# Hostel Issue Tracking System

A web-based application developed using Django to simplify hostel complaint registration, management, and tracking. The system allows students to report hostel-related issues, wardens to manage complaints, and administrators to monitor the overall complaint management process.

## Project Overview

The Hostel Issue Tracking System provides a centralized platform for managing hostel maintenance and other student complaints.

Students can submit complaints with descriptions and photo evidence. Wardens can review the complaints, update their status, and monitor the progress. Students can track the status of their complaints through their dashboard.

The system aims to improve communication between students and wardens, reduce manual complaint handling, and provide a transparent complaint resolution process.

## Features

- **Student Dashboard** – Students can submit and track their complaints.
- **Warden Dashboard** – Wardens can view and manage student complaints.
- **Django Administration Portal** – Administrators can manage users and complaint records.
- **Complaint Registration** – Students can report hostel-related issues.
- **Photo Evidence** – Students can upload images to support their complaints.
- **Complaint Status Tracking** – Students can monitor complaint progress.
- **Email Confirmation** – Students receive confirmation emails after submitting complaints.
- **Resolved Complaint Notification** – When the warden marks a complaint as resolved, an email notification is automatically sent to the particular student who raised the complaint.
- **Complaint Management** – Wardens can update complaint status and monitor pending and completed issues.

## Tech Stack

| Technology | Purpose |
|---|---|
| HTML | Structure of web pages |
| CSS | Styling and layout |
| JavaScript | Client-side interactivity |
| Bootstrap | Responsive UI design |
| Python Django | Backend development |
| SQLite3 | Database management |

## Database

**SQLite3** is used as the database for storing student details, complaint information, and complaint status.

SQLite3 is Django's default database configuration, making it suitable for this project without requiring a separate database server.

## User Roles

### Student
- Register and log in to the system.
- Submit hostel complaints.
- Upload photo evidence.
- View complaint details.
- Track complaint status.
- Receive email notifications when complaints are resolved.

### Warden
- View student complaints.
- Analyze complaint descriptions and uploaded images.
- Update complaint status.
- Monitor pending and resolved complaints.

### Administrator
- Manage student and warden accounts.
- Manage complaint records.
- Monitor the system through the Django administration portal.

## Complaint Workflow

1. Student logs in to the website.
2. Student submits a complaint with a description and photo evidence.
3. Complaint details are stored in the SQLite3 database.
4. Warden reviews the complaint.
5. Warden updates the complaint status.
6. Student tracks the updated status through the dashboard.
7. When the complaint is marked as **Resolved**, an email notification is sent to the student's registered email address.

## Email Configuration

The project uses Django email configuration to send complaint notifications to students.

Before running the project, update the email configuration in `settings.py` with your own email address and email app password.

The following placeholders are used in the project:

- `XXXXX` – Replace with the appropriate email host value.
- `YYYYYY` – Replace with your own email app password.

Make sure to configure the email host, email address, and app password correctly in `settings.py` before running the application.

**Important:** Do not upload your personal email password or app password to GitHub. Use environment variables or a local configuration file to keep your credentials private.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hostel-issue-tracking-system.git
```

### 2. Navigate to the Project Directory

```bash
cd hostel-issue-tracking-system
```

### 3. Install Django

```bash
pip install django
```

### 4. Configure Email Settings

Open `settings.py` and replace the email configuration placeholders:

- Replace `XXXXX` with the required email host.
- Replace `YYYYYY` with your own email app password.
- Configure your email address.

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

Django administration portal:

```text
http://127.0.0.1:8000/admin/
```

## Future Enhancements

- Mobile application integration.
- Real-time complaint notifications.
- Technician assignment and maintenance scheduling.
- Complaint analytics and reporting.
- Automated complaint prioritization.

## Project Objective

To develop a centralized hostel issue tracking platform that enables students to report problems, helps wardens manage complaints efficiently, and improves transparency through complaint status tracking and email notifications.

---

**Developed using HTML, CSS, JavaScript, Bootstrap, Django, and SQLite3.**
