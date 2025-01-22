from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '2d9c6d8940c84d3fb82e974f9a03b487a6e4ca3d7b594432'  # Secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    claims = db.relationship('Claim', back_populates='user', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    found_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='unclaimed')  # unclaimed, claimed
    verification_questions = db.Column(db.Text, nullable=True)
    claims = db.relationship('Claim', back_populates='item', lazy=True)
    approved_claim_id = db.Column(db.Integer, nullable=True)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    claim_date = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.Text, nullable=True)  # Store answers as JSON
    
    user = db.relationship('User', back_populates='claims')
    item = db.relationship('Item', back_populates='claims')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add JSON filter for templates
@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

# Routes
@app.route('/')
def home():
    items = Item.query.all()
    return render_template('home.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()  # Logout current user before attempting new login
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.role != 'admin':  # Ensure user is not an admin
            if user.password == password:  # Replace this with proper password hashing later
                login_user(user)
                flash('Logged in successfully!')
                return redirect(url_for('home'))
            else:
                flash('Invalid password')
        else:
            flash('Invalid email or account type')

    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        logout_user()  # Logout current user before attempting new login
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role='admin').first()
        
        if user and user.password == password:
            login_user(user)
            flash('Admin logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials')
            
    return render_template('admin_login.html')

@app.route('/admin')
@login_required
def admin_check():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('home'))
        
    items = Item.query.all()
    claims = Claim.query.all()
    stats = {
        'total_items': Item.query.count(),
        'unclaimed_items': Item.query.filter_by(status='unclaimed').count(),
        'pending_claims': Claim.query.filter_by(status='pending').count(),
        'approved_claims': Claim.query.filter_by(status='approved').count()
    }
    return render_template('admin_dashboard.html', items=items, claims=claims, stats=stats)

@app.route('/logout')
def logout():  # Removed @login_required to allow logout even if not logged in
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate name
        if not name or len(name.strip()) < 3:
            flash('Name must be at least 3 characters long')
            return redirect(url_for('register'))
            
        if not name.replace(' ', '').isalpha():
            flash('Name can only contain letters and spaces')
            return redirect(url_for('register'))
        
        if not email.endswith('@kongu.edu'):
            flash('Please use your college email (@kongu.edu)')
            return redirect(url_for('register'))
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return redirect(url_for('register'))
            
        new_user = User(name=name.strip(), email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/admin/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        questions = request.form.getlist('questions[]')
        
        # Filter out empty questions
        questions = [q.strip() for q in questions if q.strip()]
        
        item = Item(
            name=name,
            description=description,
            location=location,
            verification_questions=json.dumps(questions) if questions else None
        )
        
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item added successfully!')
        except:
            db.session.rollback()
            flash('Error adding item')
            
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_item.html')

@app.route('/claim/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim_item(item_id):
    if current_user.role == 'admin':
        flash('Administrators cannot claim items.')
        return redirect(url_for('home'))
    
    item = Item.query.get_or_404(item_id)
    
    if item.status == 'claimed':
        flash('This item has already been claimed.')
        return redirect(url_for('home'))
        
    # Check if user already has a pending claim for this item
    existing_claim = Claim.query.filter_by(
        user_id=current_user.id,
        item_id=item.id,
        status='pending'
    ).first()
    
    if existing_claim:
        flash('You already have a pending claim for this item.')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        try:
            # Get answers to verification questions
            questions = json.loads(item.verification_questions) if item.verification_questions else []
            answers = []
            
            # Collect answers in order
            for i in range(len(questions)):
                answer = request.form.get(f'answer_{i}')
                if not answer:
                    flash('Please answer all verification questions.')
                    return redirect(url_for('home'))
                answers.append(answer)
                
            # Create new claim
            claim = Claim(
                user_id=current_user.id,
                item_id=item.id,
                answers=json.dumps(answers)
            )
            
            db.session.add(claim)
            db.session.commit()
            flash('Your claim has been submitted and is pending review.')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your claim. Please try again.')
            print(f"Error submitting claim: {str(e)}")
            
        return redirect(url_for('home'))
    
    return redirect(url_for('home'))

@app.route('/admin/handle_claim/<int:claim_id>/<action>')
@login_required
def handle_claim(claim_id, action):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('home'))
        
    claim = Claim.query.get_or_404(claim_id)
    item = Item.query.get(claim.item_id)
    
    if action == 'approve':
        # Reject all other claims for this item
        other_claims = Claim.query.filter(
            Claim.item_id == item.id,
            Claim.id != claim.id,
            Claim.status == 'pending'
        ).all()
        
        for other_claim in other_claims:
            other_claim.status = 'rejected'
        
        # Approve this claim
        claim.status = 'approved'
        item.status = 'claimed'
        item.approved_claim_id = claim.id
        flash(f'Claim approved for {claim.user.name}')
        
    elif action == 'reject':
        claim.status = 'rejected'
        flash('Claim rejected')
        
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('An error occurred while processing the claim.')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_item/<int:item_id>')
@login_required
def delete_item(item_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    
    item = Item.query.get_or_404(item_id)
    
    # Delete associated claims first
    claims = Claim.query.filter_by(item_id=item_id).all()
    for claim in claims:
        db.session.delete(claim)
    
    # Delete the item
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/claim/cancel/<int:claim_id>')
@login_required
def cancel_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    
    # Check if the claim belongs to the current user
    if claim.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('home'))
    
    # Update the item status back to unclaimed
    item = Item.query.get(claim.item_id)
    if item:
        item.status = 'unclaimed'
    
    # Delete the claim
    db.session.delete(claim)
    db.session.commit()
    flash('Claim cancelled successfully')
    return redirect(url_for('claim_status'))

@app.route('/claims/status')
@login_required
def claim_status():
    claims = Claim.query.filter_by(user_id=current_user.id).order_by(Claim.claim_date.desc()).all()
    return render_template('claim_status.html', claims=claims)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_email = "admin@kongu.edu"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="Admin",
                email=admin_email,
                password="admin123",  # You should change this password
                role="admin"
            )
            db.session.add(admin)
            try:
                db.session.commit()
                print("Admin user created successfully!")
                print("Email: admin@kongu.edu")
                print("Password: admin123")
            except Exception as e:
                db.session.rollback()
                print("Error creating admin user:", e)
    
    app.run(host='0.0.0.0', port=5000)
