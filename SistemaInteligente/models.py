from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#class MyFileModel(models.Model):
#    file = models.FileField(upload_to='uploads/')
    
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.postgres.search import SearchVectorField
from datetime import datetime
#import google.generativeai as genai

class Administrador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10)
    numero_telefono = models.CharField(max_length=10)


#Antiguos metodos    
class Archivo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    documento = models.FileField(upload_to='archivos/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    fecha = models.DateTimeField(auto_now_add=True)  # Cambio aquí para capturar automáticamente la fecha de creación

    # Resto de la definición...
    