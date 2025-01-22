# Checkpoint 3: Lost and Found Management System Overview

## Project Structure
- **Backend (app.py)**
  - Flask web application with SQLAlchemy ORM
  - User authentication and role-based access control
  - PostgreSQL/SQLite database support

## Database Models
1. **User Model**
   - Fields: id, name, email, password, role
   - Supports student and admin roles
   - Email restricted to @kongu.edu domain

2. **Item Model**
   - Fields: id, name, description, location, found_date, status
   - Includes verification questions for claims
   - Tracks item status (unclaimed/claimed)

3. **Claim Model**
   - Fields: id, user_id, item_id, status, claim_date, answers
   - Manages item claims and their approval status

## Key Features
1. **Authentication System**
   - Separate login flows for students and admins
   - College email-based registration (@kongu.edu)
   - Session management with Flask-Login

2. **Admin Dashboard**
   - Item management (add/delete items)
   - Claim approval system
   - Statistics overview
   - Verification question setup

3. **Student Features**
   - View lost/found items
   - Submit claims with verification answers
   - Track claim status

## Frontend Structure
- **Templates**: Organized HTML templates for different pages
- **Static Files**: CSS and image assets for styling

## Dependencies
- Flask==2.2.5
- Flask-SQLAlchemy==3.0.2
- Flask-Login==0.6.2
- Flask-WTF==1.1.1
- PostgreSQL support (psycopg2-binary pending)

## Current Status
- Core functionality implemented
- Database migrations set up
- Basic styling in place
- Authentication system working
- Admin and user roles established
