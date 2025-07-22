# risk_management/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """Form untuk login pengguna."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')

class RiskForm(FlaskForm):
    """Form untuk menambah atau mengedit risiko."""
    title = StringField('Judul Risiko', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Deskripsi', validators=[DataRequired()])
    category = StringField('Kategori', validators=[DataRequired(), Length(max=50)], 
                           render_kw={"placeholder": "Contoh: Finansial, Operasional, Keamanan"})
    
    probability = SelectField('Probabilitas', 
                              choices=[('Rendah', 'Rendah'), ('Sedang', 'Sedang'), ('Tinggi', 'Tinggi')],
                              validators=[DataRequired()])
    
    impact = SelectField('Dampak', 
                         choices=[('Rendah', 'Rendah'), ('Sedang', 'Sedang'), ('Tinggi', 'Tinggi')],
                         validators=[DataRequired()])
    
    status = SelectField('Status', 
                         choices=[('Terbuka', 'Terbuka'), ('Dalam Proses', 'Dalam Proses'), ('Tertutup', 'Tertutup')],
                         validators=[DataRequired()])
                         
    submit = SubmitField('Simpan Risiko')
