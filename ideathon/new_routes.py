from flask import render_template, redirect, url_for

def setup_new_routes(app):
    @app.route('/landing')
    def landing():
        return render_template('landing.html')

    @app.route('/new/login')
    def new_login():
        return render_template('new_login.html')

    @app.route('/new/admin/login')
    def new_admin_login():
        return render_template('new_admin_login.html')

    @app.route('/new/claim/status')
    def new_claim_status():
        return render_template('new_claim_status.html')
