from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from perform_ela import perform_ela

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/analisis')
def analisis():
    return render_template('Analisis.html')

@app.route('/user')
def user():
    return render_template('User.html')

@app.route('/donaciones')
def donaciones():
    return render_template('donaciones.html')

@app.route('/actualizaciones')
def actualizaciones():
    return render_template('Actualizaciones.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/analyze', methods=['POST'])
def analyze():

    if 'image' not in request.files:
        return 'No file part'

    file = request.files['image']

    if file.filename == '':
        return 'No selected file'

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Run the ELA analysis
        result_path = perform_ela(filepath)

        if result_path:
            return send_file(result_path, as_attachment=True)
        else:
            return 'Error performing ELA.'

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
