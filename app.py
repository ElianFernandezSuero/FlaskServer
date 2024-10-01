from flask import Flask, render_template, request, redirect, url_for
import os
from perform_ela import perform_ela
from exifread import process_file  # Asegúrate de tener exifread instalado

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Función para extraer metadatos y geotags
def extract_metadata(image_path):
    with open(image_path, 'rb') as img_file:
        tags = process_file(img_file)
        metadata = {}
        geo_tags = {}

        for tag in tags.keys():
            # Filtrar información útil
            if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote']:
                metadata[tag] = str(tags[tag])
            
            # Extraer geotags si existen
            if tag in ['GPS GPSLatitude', 'GPS GPSLongitude']:
                geo_tags[tag] = str(tags[tag])
        
        return metadata, geo_tags

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/login')
def login():
    return render_template('Login.html')

# Ruta para el análisis de la imagen (ELA y metadatos)
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return 'No se encontró ninguna imagen.'

    file = request.files['image']

    if file.filename == '':
        return 'No se seleccionó ningún archivo.'

    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Ejecutar el análisis ELA
        ela_result_path = perform_ela(filepath)

        if ela_result_path:
            # Extraer metadatos y geotags
            metadata, geo_tags = extract_metadata(filepath)

            # Renderizar la plantilla de resultados con las variables
            return render_template('result.html', ela_result_path=ela_result_path, metadata=metadata, geo_tags=geo_tags)
        else:
            return 'Error al realizar el análisis ELA.'

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
