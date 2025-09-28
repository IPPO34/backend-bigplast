from flask import Flask, request, jsonify, send_from_directory
from config import Config
from models import db, User, Product
from auth import verify_password, create_token, admin_required
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash  # ✅ Import necesario

# Configuración de subida de imágenes
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    db.init_app(app)
    CORS(app)

    # Crear carpeta de uploads si no existe
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ---------- AUTH ----------
    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "username and password required"}), 400

        # Buscar usuario en BD
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            token = create_token(user_id=user.id, rol=user.rol)  # ✅ rol real
            return jsonify({"token": token, "rol": user.rol})
        
        return jsonify({"error": "invalid credentials"}), 401

    # ---------- Upload imágenes ----------
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return jsonify({"error": "No se envió archivo"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Archivo vacío"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            return jsonify({"url": f"/uploads/{filename}"})
        return jsonify({"error": "Formato no permitido"}), 400

    # Servir archivos subidos
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # ---------- PUBLIC: productos ----------
    @app.route("/api/productos", methods=["GET"])
    def list_productos():
        products = Product.query.order_by(Product.creado_en.desc()).all()
        result = []
        for p in products:
            result.append({
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio": float(p.precio) if p.precio is not None else None,
                "imagen_url": p.imagen_url,
                "creado_en": p.creado_en.isoformat() if p.creado_en else None,
                "ficha_tecnica": getattr(p, "ficha_tecnica", None)  # ✅ si existe en modelo
            })
        return jsonify(result)

    @app.route("/api/productos/<int:pid>", methods=["GET"])
    def get_producto(pid):
        p = Product.query.get_or_404(pid)
        return jsonify({
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": float(p.precio) if p.precio is not None else None,
            "imagen_url": p.imagen_url,
            "creado_en": p.creado_en.isoformat() if p.creado_en else None,
            "ficha_tecnica": getattr(p, "ficha_tecnica", None)
        })

    # ---------- ADMIN: CRUD ----------
    @app.route("/api/productos", methods=["POST"])
    @admin_required
    def create_producto():
        data = request.get_json() or {}
        p = Product(
            nombre=data.get("nombre"),
            descripcion=data.get("descripcion"),
            precio=data.get("precio"),
            imagen_url=data.get("imagen_url"),
            ficha_tecnica=data.get("ficha_tecnica")  # ✅ si existe en modelo
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({"msg": "producto creado", "id": p.id}), 201

    @app.route("/api/productos/<int:pid>", methods=["PUT"])
    @admin_required
    def update_producto(pid):
        data = request.get_json() or {}
        p = Product.query.get_or_404(pid)
        p.nombre = data.get("nombre", p.nombre)
        p.descripcion = data.get("descripcion", p.descripcion)
        p.precio = data.get("precio", p.precio)
        p.imagen_url = data.get("imagen_url", p.imagen_url)
        p.ficha_tecnica = data.get("ficha_tecnica", getattr(p, "ficha_tecnica", None))
        db.session.commit()
        return jsonify({"msg": "producto actualizado"})

    @app.route("/api/productos/<int:pid>", methods=["DELETE"])
    @admin_required
    def delete_producto(pid):
        p = Product.query.get_or_404(pid)
        db.session.delete(p)
        db.session.commit()
        return jsonify({"msg": "producto eliminado"})

    # ---------- Info empresa ----------
    @app.route("/api/empresa", methods=["GET"])
    def empresa_info():
        return jsonify({
            "nombre": "Sillas Plásticas Vásquez",
            "descripcion": "Fabricantes y distribuidores de sillas plásticas resistentes para hogar y eventos. Producción local, entrega rápida.",
            "direccion": "Av. Ejemplo 123, Ciudad",
            "telefono": "+51 9XX XXX XXX",
            "email": "contacto@vasquez-sillas.pe"
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
