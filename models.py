# risk_management/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# Inisialisasi ekstensi SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Model untuk pengguna."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Relasi ke model Risk
    risks = db.relationship('Risk', backref='owner', lazy=True)

    def set_password(self, password):
        """Membuat hash password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Memeriksa hash password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Risk(db.Model):
    """Model untuk data risiko."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.String(20), nullable=False) # e.g., 'Rendah', 'Sedang', 'Tinggi'
    impact = db.Column(db.String(20), nullable=False) # e.g., 'Rendah', 'Sedang', 'Tinggi'
    status = db.Column(db.String(20), default='Terbuka') # e.g., 'Terbuka', 'Dalam Proses', 'Tertutup'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Key untuk menghubungkan dengan pengguna
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Risk {self.title}>'
