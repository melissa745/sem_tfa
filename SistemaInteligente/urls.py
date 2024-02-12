from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('subir_pdf/',views.subir_pdf,name='subir_pdf'),
]
