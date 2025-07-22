# risk_management/app.py

from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Risk
from forms import LoginForm, RiskForm
import os
import json

# --- Konfigurasi Aplikasi ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ganti-dengan-kunci-rahasia-yang-kuat')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Inisialisasi Ekstensi ---
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Halaman yang dituju jika pengguna belum login
login_manager.login_message = "Silakan masuk untuk mengakses halaman ini."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    """Memuat pengguna dari database berdasarkan ID."""
    return User.query.get(int(user_id))

# --- Rute Aplikasi ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login pengguna."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Proses logout pengguna."""
    logout_user()
    flash('Anda telah berhasil keluar.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Halaman dasbor utama."""
    risks = Risk.query.filter_by(owner_id=current_user.id).all()
    
    # Data untuk ringkasan
    total_risks = len(risks)
    open_risks = len([r for r in risks if r.status == 'Terbuka'])
    closed_risks = len([r for r in risks if r.status == 'Tertutup'])
    
    # Data untuk chart
    status_counts = {
        'Terbuka': open_risks,
        'Dalam Proses': len([r for r in risks if r.status == 'Dalam Proses']),
        'Tertutup': closed_risks
    }
    
    impact_counts = {
        'Rendah': len([r for r in risks if r.impact == 'Rendah']),
        'Sedang': len([r for r in risks if r.impact == 'Sedang']),
        'Tinggi': len([r for r in risks if r.impact == 'Tinggi']),
    }

    # Mengubah data ke format JSON untuk JavaScript
    chart_data = {
        'status': {
            'labels': list(status_counts.keys()),
            'data': list(status_counts.values())
        },
        'impact': {
            'labels': list(impact_counts.keys()),
            'data': list(impact_counts.values())
        }
    }

    return render_template('dashboard.html', 
                           total_risks=total_risks,
                           open_risks=open_risks,
                           closed_risks=closed_risks,
                           chart_data_json=json.dumps(chart_data))

@app.route('/risks')
@login_required
def risks_list():
    """Halaman untuk menampilkan semua risiko dalam tabel."""
    all_risks = Risk.query.filter_by(owner_id=current_user.id).order_by(Risk.created_at.desc()).all()
    return render_template('risks.html', risks=all_risks)

@app.route('/risk/add', methods=['GET', 'POST'])
@login_required
def add_risk():
    """Halaman untuk menambah risiko baru."""
    form = RiskForm()
    if form.validate_on_submit():
        new_risk = Risk(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            probability=form.probability.data,
            impact=form.impact.data,
            status=form.status.data,
            owner_id=current_user.id
        )
        db.session.add(new_risk)
        db.session.commit()
        flash('Risiko baru berhasil ditambahkan!', 'success')
        return redirect(url_for('risks_list'))
    return render_template('add_risk.html', form=form, legend='Tambah Risiko Baru')

@app.route('/risk/<int:risk_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_risk(risk_id):
    """Halaman untuk mengedit risiko yang ada."""
    risk = Risk.query.get_or_404(risk_id)
    if risk.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk mengedit risiko ini.', 'danger')
        return redirect(url_for('risks_list'))
        
    form = RiskForm(obj=risk) # Mengisi form dengan data yang ada
    if form.validate_on_submit():
        risk.title = form.title.data
        risk.description = form.description.data
        risk.category = form.category.data
        risk.probability = form.probability.data
        risk.impact = form.impact.data
        risk.status = form.status.data
        db.session.commit()
        flash('Risiko berhasil diperbarui!', 'success')
        return redirect(url_for('risks_list'))
    return render_template('add_risk.html', form=form, legend=f'Edit Risiko: {risk.title}')

@app.route('/risk/<int:risk_id>/delete', methods=['POST'])
@login_required
def delete_risk(risk_id):
    """Proses untuk menghapus risiko."""
    risk = Risk.query.get_or_404(risk_id)
    if risk.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus risiko ini.', 'danger')
        return redirect(url_for('risks_list'))
        
    db.session.delete(risk)
    db.session.commit()
    flash('Risiko berhasil dihapus.', 'success')
    return redirect(url_for('risks_list'))


# --- Inisialisasi Database ---
@app.cli.command("init-db")
def init_db_command():
    """Membuat tabel database dan pengguna default."""
    db.create_all()
    # Cek jika pengguna 'admin' sudah ada
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Database diinisialisasi dan pengguna 'admin' (password: 'admin123') dibuat.")
    else:
        print("Database sudah ada.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            print("Membuat pengguna default: admin / admin123")
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
