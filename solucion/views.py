import os
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from pdf2image import convert_from_path
import pytesseract
from docx import Document
from django.http import JsonResponse
from django.core.cache import cache

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\snavarro\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def pdf_to_word(file):
    # Save the uploaded file temporarily to disk
    temp_file_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(temp_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


    # Convert the PDF to images and extract the text
    images = convert_from_path(temp_file_path, poppler_path=r'C:\Program Files (x86)\poppler-23.11.0\Library\bin')
    doc = Document()
    for i in range(len(images)):
        text = pytesseract.image_to_string(images[i], lang='spa')
        doc.add_paragraph(text)

        # Actualizar el valor de progreso
        progress = (i+1) / len(images) * 100
        cache.set('progress', progress)
        
    docx_file = f"{os.path.splitext(temp_file_path)[0]}.docx"
    doc.save(docx_file)

    # Remove the temporary file
    os.remove(temp_file_path)
    # Increment the file counter and delete files if necessary
    
    return docx_file

@never_cache
def index(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        file = request.FILES['pdf_file']
        converted_file = pdf_to_word(file)
        try:
            f = open(converted_file, 'rb')
        except IOError:
            # Manejar el error aquí
            pass
        else:
            response = FileResponse(f, as_attachment=True)
            delete_docx_files() 
            return response
    else:
        return render(request, 'solucion/index.html', {'converted_file': None})

def delete_docx_files():
    for filename in os.listdir(settings.MEDIA_ROOT):
        if filename.endswith('.docx'):
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, filename))
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")
                

def delete_docx_files():
    for filename in os.listdir(settings.MEDIA_ROOT):
        if filename.endswith('.docx'):
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            try:
                os.remove(file_path)
            except PermissionError:
                print(f"No se tienen los permisos necesarios para eliminar el archivo {filename}")
            except FileNotFoundError:
                print(f"El archivo {filename} no existe")
            except OSError as e:
                print(f"Error ({e.errno}) al eliminar el archivo {filename}: {e.strerror}")
            except Exception as e:
                print(f"Error inesperado al eliminar el archivo {filename}: {e}")


def get_progress(request):
    progress = cache.get('progress', 0)
    return JsonResponse({'progress': progress})





