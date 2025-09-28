from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "usuarios"   # nombre real de tu tabla
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # en tu tabla es "password"
    rol = db.Column(db.String(50), default="user")        # en tu tabla es "rol"

class Product(db.Model):
    __tablename__ = "productos"  # nombre real de tu tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2))
    imagen_url = db.Column(db.Text)
    ficha_tecnica = db.Column(db.Text)   # 🆕 nuevo campo
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
