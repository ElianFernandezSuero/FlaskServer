from flask import Flask, render_template, request, redirect, url_for
from PIL import Image, ImageChops, ImageEnhance, ImageOps
import os
import exifread

app = Flask(__name__)

# Función para realizar ELA
def perform_ela(image_path, quality=90, scale=10):
    try:
        # Recompresión de imagen y análisis de diferencias
        original = Image.open(image_path).convert('RGB')
        temp_image_path = os.path.join(os.path.dirname(image_path), 'temp_image.jpg')
        original.save(temp_image_path, 'JPEG', quality=quality)
        recompressed = Image.open(temp_image_path)
        ela_image = ImageChops.difference(original, recompressed)

        # Mejora visual de la imagen ELA
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale_factor = 255.0 / max_diff if max_diff != 0 else 1
        ela_image = ImageEnhance.Brightness(ela_image).enhance(scale_factor * scale)
        ela_image = ImageOps.autocontrast(ela_image)

        # Guardar la imagen ELA en la carpeta correcta (static/uploads/)
        ela_path = os.path.join('static/uploads', 'ela_result.png')  # Asegura que se guarde en static/uploads
        ela_image.save(ela_path)

        # Limpiar imagen temporal
        os.remove(temp_image_path)

        return ela_path
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
            # Guardar la imagen en el servidor
            image_path = os.path.join('static/uploads', image.filename)
            image.save(image_path)
            
            # Ejecutar ELA
            ela_result_path = perform_ela(image_path)

            # Extraer metadatos y geotags
            metadata, geo_tags = extract_metadata(image_path)

            return render_template('result.html', ela_result_path=ela_result_path, metadata=metadata, geo_tags=geo_tags)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
