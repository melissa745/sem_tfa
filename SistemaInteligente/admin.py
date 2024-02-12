from django.contrib import admin
from .models import *
# Register your models here.
class UsuarioAdmin(admin.ModelAdmin):
        list_display = ('nombre','apellido','cedula','numero_telefono')   

class ArchivoAdmin(admin.ModelAdmin):
        list_display = ('usuario','documento','fecha')
        usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

admin.site.register(Archivo,ArchivoAdmin)
admin.site.register(Usuario,UsuarioAdmin)