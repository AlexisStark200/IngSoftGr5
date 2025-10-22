from django.contrib import admin
from .models import Grupo

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('id_grupo', 'nombre_grupo', 'correo_grupo')
