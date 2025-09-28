import jwt
from functools import wraps
from flask import request, jsonify, current_app
from passlib.hash import bcrypt
from datetime import datetime, timedelta

# -------------------------------
# Utilidades de contraseñas
# -------------------------------
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, password_hash):
    return bcrypt.verify(password, password_hash)

# -------------------------------
# JWT helpers
# -------------------------------
def create_token(user_id, rol):
    payload = {
        "sub": user_id,
        "rol": rol,   # usamos rol en lugar de is_admin
        "exp": datetime.utcnow() + timedelta(days=current_app.config["JWT_EXP_DAYS"])
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return token

def decode_token(token):
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])

# -------------------------------
# Decorador: solo admins
# -------------------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth:
            return jsonify({"error": "Authorization header missing"}), 401

        parts = auth.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"error": "Invalid Authorization header"}), 401

        token = parts[1]
        try:
            payload = decode_token(token)
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "msg": str(e)}), 401

        if payload.get("rol") != "admin":   # validamos por rol
            return jsonify({"error": "Admin privileges required"}), 403

        request.user_id = payload.get("sub")
        return f(*args, **kwargs)
    return decorated
