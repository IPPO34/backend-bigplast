from app import create_app   # importa la función, no app
from models import db, User
from werkzeug.security import generate_password_hash

# crear app usando la factory
app = create_app()

with app.app_context():
    username = "Administrador"
    password = "Admin456*"
    hashed_pw = generate_password_hash(password)

    new_user = User(username=username, password=hashed_pw, rol="admin")
    db.session.add(new_user)
    db.session.commit()

    print(f"✅ Usuario creado: {username}")
