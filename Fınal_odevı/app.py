from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gelistirme_anahtari'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///araba.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ✅ Kullanıcı tablosu
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' veya 'user'

# ✅ Araç tablosu
class Arac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    fiyat = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/arac-kiralama', methods=['GET', 'POST'])
def arac_kiralama():
    if request.method == 'POST':
        return redirect(url_for('araclar'))  
    return render_template('arac_kiralama.html')

@app.route('/arac-iade', methods=['GET', 'POST'])
def arac_iade():
    if request.method == 'POST':
        return redirect(url_for('index'))  
    return render_template('arac_iade.html')

@app.route('/araclar')
def araclar():
    araclar = Arac.query.all()  # Veritabanındaki tüm araçları al
    return render_template('araclar.html', araclar=araclar)  # Araçları şablona gönder


@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html')

@app.route('/fiyatlar')
def fiyatlar():
    return render_template('fiyatlar.html')

@app.route('/kampanyalar')
def kampanyalar():
    return render_template('kampanyalar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))  # Rol kontrolü dashboard içinde
        flash('E-posta veya şifre hatalı!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': 
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'user')  # HTML formunda varsa role al, yoksa 'user'

        if User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kayıtlı!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Current user role: {current_user.role}")  # Debug amaçlı
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html')  # Admin sayfası
    else:
        return render_template('dashboard.html')  # Normal kullanıcı sayfası


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/arac-ekle', methods=['GET', 'POST'])
@login_required
def arac_ekle():
    if current_user.role != 'admin':
        flash('Bu sayfaya erişim izniniz yok.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        marka = request.form['marka']
        model = request.form['model']
        yil = request.form['yil']
        fiyat = request.form['fiyat']

        # Yeni araç nesnesi oluştur
        yeni_arac = Arac(marka=marka, model=model, yil=int(yil), fiyat=float(fiyat))
        
        # Veritabanına ekle
        db.session.add(yeni_arac)
        db.session.commit()

        flash('Araç başarıyla eklendi.', 'success')
        return redirect(url_for('araclar'))  # Araçlar sayfasına yönlendir

    # Mevcut yıl değerini dinamik olarak ayarlamak için
    current_year = 2023  # veya datetime.datetime.now().year ile dinamik olarak alabilirsiniz
    return render_template('arac_ekle.html', max_year=current_year)

with app.app_context():
    # Admin yapmak istediğiniz kullanıcının e-posta adresini buraya girin
    user_email_to_update = "yusufalkan2900@gmail.com" # Burayı admin yapmak istediğiniz kullanıcının e-posta adresiyle değiştirin

    # E-posta adresine göre kullanıcıyı bulun
    user = User.query.filter_by(email=user_email_to_update).first()

    if user:
        if user.role == 'admin':
            print(f"'{user_email_to_update}' e-postalı kullanıcı zaten admin rolünde.")
        else:
            # Kullanıcının rolünü admin olarak güncelle
            user.role = 'admin'
            db.session.commit()
            print(f"'{user_email_to_update}' e-postalı kullanıcının rolü başarıyla 'admin' olarak güncellendi.")
    else:
        print(f"'{user_email_to_update}' e-posta adresine sahip bir kullanıcı bulunamadı.")

print("İşlem tamamlandı.")




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


    
    
