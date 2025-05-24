from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///araba.db'
db = SQLAlchemy(app)

# Modeller
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Arac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    kiralama_durumu = db.Column(db.String(50), default="Müsait", nullable=False)
    resim_url = db.Column(db.String(255), nullable=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('kiralanan_araclar', lazy=True))

# JSON'a aktarım fonksiyonu
def export_araclar_to_json():
    with app.app_context():
        # Veritabanını güncelle
        db.create_all()
        
        araclar = Arac.query.all()
        data = []
        for arac in araclar:
            data.append({
                'id': arac.id,
                'marka': arac.marka,
                'model': arac.model,
                'fiyat': arac.fiyat,
                'kiralama_durumu': arac.kiralama_durumu,
                'resim_url': arac.resim_url,
                'kullanici_id': arac.kullanici_id,
                'kullanici_adi': arac.user.name if arac.user else None
            })

        with open('araclar.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Araçlar başarıyla araclar.json dosyasına kaydedildi!")

# Ana fonksiyon
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tabloları oluştur
    export_araclar_to_json()
