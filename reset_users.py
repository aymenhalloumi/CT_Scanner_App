from app import app, db
from flask_appbuilder.security.sqla.models import User

with app.app_context():
    # Delete all users
    users = db.session.query(User).all()
    for user in users:
        db.session.delete(user)
    
    db.session.commit()
    print("✅ All users deleted")

user = appbuilder.sm.find_user(username='admin')
appbuilder.sm.reset_password(user, 'newpassword123')
db.session.commit()
