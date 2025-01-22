from app import app, db, User

with app.app_context():
    # Check if admin already exists
    existing_admin = User.query.filter_by(email='admin@kongu.edu').first()
    if existing_admin is None:
        admin = User(
            name='Admin',
            email='admin@kongu.edu',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
