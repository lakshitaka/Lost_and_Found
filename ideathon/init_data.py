from app import app, db, User

def init_data():
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(email='admin@kongu.edu').first()
        if not admin:
            admin = User(
                name='Admin',
                email='admin@kongu.edu',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            
        try:
            db.session.commit()
            print("Admin user initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing admin: {str(e)}")

if __name__ == '__main__':
    init_data()
