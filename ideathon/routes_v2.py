from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

def setup_new_routes(app):
    @app.route('/new/home')
    def new_home():
        return render_template('new_home.html')

    @app.route('/new/options')
    def new_options():
        return render_template('new_options.html')

    @app.route('/new/student/login', methods=['GET', 'POST'])
    def new_student_login():
        if request.method == 'POST':
            # Add login logic here
            return redirect(url_for('new_home'))
        return render_template('new_student_login.html')

    @app.route('/new/student/register', methods=['GET', 'POST'])
    def new_student_register():
        if request.method == 'POST':
            # Add registration logic here
            return redirect(url_for('new_student_login'))
        return render_template('new_student_register.html')

    @app.route('/new/admin/login', methods=['GET', 'POST'])
    def new_admin_login():
        if request.method == 'POST':
            # Add admin login logic here
            return redirect(url_for('new_admin_dashboard'))
        return render_template('new_admin_portal.html')

    @app.route('/new/claim/status', methods=['GET', 'POST'])
    def new_claim_status():
        if request.method == 'POST':
            # Add claim status check logic here
            return render_template('new_claim_check.html', status="Processing")
        return render_template('new_claim_check.html')
