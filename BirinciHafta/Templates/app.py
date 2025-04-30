from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/araclar')
def araclar():
    return render_template('araclar.html')

@app.route('/iletisim')
def iletisim():
    return render_template('iletisim.html')

@app.route('/fiyatlar')
def fiyatlar():
    return render_template('fiyatlar.html')

@app.route('/kampanyalar')
def kampanyalar():
    return render_template('kampanyalar.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)