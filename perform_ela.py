from flask import Flask, render_template, render_template_string, request, redirect, url_for, send_file
from PIL import Image, ImageChops, ImageEnhance, ImageOps
import os
import exifread

app = Flask(__name__)

def perform_ela(image_path, quality=90, scale=10):
    try:
        # Recompresión de la imagen y análisis de diferencias
        original = Image.open(image_path).convert('RGB')
        temp_image_path = os.path.join('/tmp', 'temp_image.jpg')  # Guardar temporalmente en /tmp
        original.save(temp_image_path, 'JPEG', quality=quality)
        recompressed = Image.open(temp_image_path)
        ela_image = ImageChops.difference(original, recompressed)

        # Mejora visual de la imagen ELA
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale_factor = 255.0 / max_diff if max_diff != 0 else 1
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale_factor * scale)
        ela_image = ImageOps.autocontrast(ela_image)

        # Guardar la imagen ELA en /tmp
        ela_filename = 'ela_result.png'
        ela_path = os.path.join('/tmp', ela_filename)
        ela_image.save(ela_path)

        # Limpiar la imagen temporal
        os.remove(temp_image_path)

        return ela_filename  # Devolver solo el nombre del archivo
    except Exception as e:
        print(f"Failed to perform ELA: {e}")
        return None


# Función para extraer metadatos y geotags
def extract_metadata(image_path):
    with open(image_path, 'rb') as img_file:
        tags = exifread.process_file(img_file)
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        
        image = request.files['image']
        if image.filename == '':
            return redirect(request.url)
        
        if image:
            # Guardar la imagen en el directorio temporal de Vercel
            image_path = os.path.join('/tmp', image.filename)  # Usar /tmp en lugar de static/uploads
            image.save(image_path)  # Guardar la imagen original
            
            # Ejecutar ELA
            ela_result_path = perform_ela(image_path)

            if ela_result_path:
                # Extraer metadatos y geotags
                metadata, geo_tags = extract_metadata(image_path)

                # Renderizar el resultado
                return render_template('result.html', ela_result_path=ela_result_path, metadata=metadata, geo_tags=geo_tags)
            else:
                return "Error al realizar el análisis ELA.", 500

    return render_template('index.html')

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
