from flask import Flask, render_template, render_template_string, request, redirect, url_for, send_file
import os
from perform_ela import perform_ela
from exifread import process_file  # Asegúrate de tener exifread instalado

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'  # Cambiado a /tmp para usar el almacenamiento temporal

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
        filepath = os.path.join('/tmp', file.filename)  # Usar /tmp para guardar temporalmente
        file.save(filepath)

        # Ejecutar el análisis ELA
        ela_result_path = perform_ela(filepath)

        if ela_result_path:
            # Si `perform_ela` devuelve la ruta completa, asegúrate de que sea solo el nombre del archivo.
            ela_result_path = 'ela_result.png'

            # Extraer metadatos y geotags
            metadata, geo_tags = extract_metadata(filepath)

            # Renderizar la plantilla de resultados
            return render_template('result.html', ela_result_path=ela_result_path, metadata=metadata, geo_tags=geo_tags)
        else:
            return 'Error al realizar el análisis ELA.'

    return redirect(url_for('index'))
@app.route('/display_image/<path:image_path>')
def display_image(image_path):
    # Asegúrate de buscar en /tmp
    full_image_path = os.path.join('/tmp', image_path)
    print(f"Intentando acceder a: {full_image_path}")  # Depurar la ruta
    if os.path.exists(full_image_path):
        print(f"Sirviendo el archivo: {full_image_path}")
        return send_file(full_image_path, mimetype='image/png')
    else:
        print(f"Archivo no encontrado: {full_image_path}")
        return "Archivo no encontrado", 404

@app.route('/list_tmp')
def list_tmp():
    # Obtener la lista de archivos en el directorio /tmp
    files = os.listdir('/tmp')
    # Renderizar los archivos en una plantilla simple
    return render_template_string('''
        <h1>Archivos en /tmp</h1>
        <ul>
        {% for file in files %}
            <li>{{ file }}</li>
        {% endfor %}
        </ul>
    ''', files=files)

if __name__ == '__main__':
    app.run(debug=True)
