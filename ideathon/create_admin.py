from app import app, db, User

with app.app_context():
    admin = User(
        name='Admin',
        email='admin@kongu.edu',
        password='admin123',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
