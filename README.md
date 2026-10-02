# Campus Maintenance Request System

A web application built using Django for submitting and managing campus maintenance requests.

## Features

- **User Authentication**: Student/Staff registration and login system.
- **Request Management**: Create, edit, view, and delete maintenance requests.
- **Status Tracking**: Track request status (Pending, In Progress, Resolved, Closed).
- **Staff Dashboard**: Staff view for updating maintenance statuses and assigning tasks.
- **Seed Data Utility**: Script provided for populating initial sample data.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ragendhu-R/Campus-Maintenance-Request-System.git
   cd Campus-Maintenance-Request-System
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Populate seed data (optional)**:
   ```bash
   python seed_data.py
   ```

6. **Run the server**:
   ```bash
   python manage.py runserver
   ```
