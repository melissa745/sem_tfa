from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage  # Importación agregada
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import fitz  # Importa PyMuPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer 
import pathlib
import textwrap
import google.generativeai as genai
import nltk
from IPython.display import display
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import fitz 
from IPython.display import Markdown
# Vista adicional que requiere autenticación
@login_required
def index(request):    
    # Pasar el contenido generado (o el mensaje de error) a la plantilla
    return render(request, 'app/home.html')

'''def subir_pdf(request):
    context = {}  # Inicializa el contexto para la plantilla
    #pdf_text = ""
    if request.method == 'POST':
        try:
            myfile = request.FILES.get('myfile')  # Usar .get para evitar MultiValueDictKeyError
            if myfile:
                # Especificar la ruta de almacenamiento
                fs = FileSystemStorage(location='static/files')
                filename = fs.save(myfile.name, myfile)
                upload_file_url = fs.url(filename)
                
                context = {
                    "path": "static/files" + upload_file_url,
                    "filename":filename
                }
                print("File Uploaded Successfully")
                print(leer_pdf("static/files"+upload_file_url))
            else:
                # Manejar el caso en que no se subió ningún archivo
                context['error'] = 'No file was uploaded.'
        except Exception as e:
            # Captura cualquier otra excepción que pueda ocurrir
            print(f"An error occurred: {e}")
            context['error'] = f"An error occurred during file upload: {e}"

    # Usa el mismo template tanto para GET como para POST, pero el contexto cambiará
    return render(request, 'app/subir_pdf.html', context)
'''
def generate_summary(text, sentences_count=2):
    # Crea un parser de texto a partir del texto proporcionado
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    
    # Inicializa el sumarizador de TextRank
    summarizer = TextRankSummarizer()
    
    # Genera el resumen con el número de oraciones especificado
    summary = summarizer(parser.document, sentences_count)
    
    # Concatena las oraciones del resumen en una sola cadena
    summary_text = " ".join(str(sentence) for sentence in summary)
    
    return summary_text 
def subir_pdf(request):
    context = {}

    if request.method == 'POST':
        try:
            myfile = request.FILES.get('myfile')
            if myfile:
                fs = FileSystemStorage(location='static/files')
                filename = fs.save(myfile.name, myfile)
                upload_file_url = fs.url(filename)
                
                # Obtener el texto del PDF
                pdf_text = leer_pdf("static/files" + upload_file_url)
                summary = generate_summary (pdf_text)
                # Obtener las preguntas ingresadas por el usuario
                questions = request.POST.getlist('questions')  # Asumiendo que las preguntas se envían como una lista en el formulario
                #extraer pregunta
                answers = extract_answers(pdf_text, questions)
                context = {
                    "path": "static/files" + upload_file_url,
                    "filename": filename,
                    "pdf_text": pdf_text,
                    "summary":summary,
                    "answers": answers
                }
                print("File Uploaded Successfully")
                print(pdf_text)
                print("resumen",summary) 
                print("answers",answers) 
            
            else:
                context['error'] = 'No file was uploaded.'
        except Exception as e:
            print(f"An error occurred: {e}")
            context['error'] = f"An error occurred during file upload: {e}"

    return render(request, 'app/subir_pdf.html', context)
def extract_answers(pdf_text, questions):
    # Tokeniza el texto del PDF en oraciones
    sentences = nltk.sent_tokenize(pdf_text)
    
    # Inicializa una lista para almacenar las respuestas
    answers = []
    
    # Itera sobre cada oración del texto del PDF
    for sentence in sentences:
        # Itera sobre cada pregunta proporcionada
        for question in questions:
            # Verifica si la oración contiene la pregunta
            if question in sentence:
                # Si encuentra la pregunta, agrega la oración como respuesta
                answers.append(sentence)
                # Termina la iteración sobre las preguntas para evitar agregar la misma oración varias veces
                break
    
    return answers 

def leer_pdf(ruta_pdf):
    texto_del_pdf = ""
    try:
        # Abre el archivo PDF
        with fitz.open(ruta_pdf) as doc:
            # Itera sobre cada página del PDF
            for pagina in doc:
                # Extrae el texto de la página actual
                texto_del_pdf += pagina.get_text()
    except Exception as e:
        print(f"Error al leer el archivo PDF: {e}")
        texto_del_pdf = None

    return texto_del_pdf

 # PyMuPDF para leer PDF

# Asumiendo que ya tienes configurado genai.GenerativeModel o cualquier modelo de IA que estés utilizando

def subir_leer_y_preguntar_pdf(request):
    context = {}  # Inicializa el contexto para la plantilla

    if request.method == 'POST':
        # Verificar si se está subiendo un archivo
        myfile = request.FILES.get('myfile', None)
        pregunta = request.POST.get('input_text', None)

        if myfile:
            fs = FileSystemStorage(location='static/files')
            filename = fs.save(myfile.name, myfile)
            ruta_pdf = fs.path(filename)

            # Leer el contenido del PDF
            texto_del_pdf = leer_pdf(ruta_pdf)
            context['texto_pdf'] = texto_del_pdf[:500]  # Muestra una parte del texto para verificación, ajusta según necesidad

        if pregunta and 'texto_pdf' in request.session:
            # Procesar la pregunta utilizando el texto del PDF almacenado en la sesión
            texto_del_pdf = request.session['texto_pdf']
            respuesta_ia = procesar_pregunta(texto_del_pdf, pregunta)
            context['respuesta_ia'] = respuesta_ia
        elif pregunta:
            # Esto maneja el caso en que se hace una pregunta sin volver a subir el archivo,
            # asumiendo que el texto del PDF ya está disponible de una carga anterior
            texto_del_pdf = request.session.get('texto_pdf', '')
            if texto_del_pdf:
                respuesta_ia = procesar_pregunta(texto_del_pdf, pregunta)
                context['respuesta_ia'] = respuesta_ia
            else:
                context['error'] = "Por favor, sube un archivo PDF antes de hacer una pregunta."

    return render(request, 'app/subir_y_preguntar_pdf.html', context)

def leer_pdf(ruta_pdf):
    texto_del_pdf = ""
    try:
        with fitz.open(ruta_pdf) as doc:
            for pagina in doc:
                texto_del_pdf += pagina.get_text()
    except Exception as e:
        print(f"Error al leer el archivo PDF: {e}")
    return texto_del_pdf

def procesar_pregunta(texto_pdf, pregunta):
    # Implementa la lógica para enviar la pregunta y el texto al modelo de IA y obtener una respuesta
    respuesta_ia = "Respuesta simulada para la pregunta: " + pregunta
    print("las conclusiones son",respuesta_ia)
    return respuesta_ia
    

#def questions(request):
    try:
        # Crear una instancia del modelo generativo y generar contenido
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("en base al texto extraido, responde")
        
        # Aquí, deberías extraer la información relevante de `response`
        # Por ejemplo, si `response` tiene un atributo `text` con el contenido generado:
        generated_text = response.text  # Ajusta esto según la estructura real de la respuesta

        print(generated_text)

        return render(request, 'app/subir_pdf.html', genai)
        
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir durante la generación de contenido
        generated_text = f"Error al generar contenido: {e}"