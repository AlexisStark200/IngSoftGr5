from django.db import models

class Grupo(models.Model):
    id_grupo = models.AutoField(primary_key=True, db_column='ID_GRUPO')
    nombre_grupo = models.CharField(max_length=60, db_column='NOMBRE_GRUPO')
    area_interes = models.CharField(max_length=40, db_column='AREA_INTERES', default='Cultura')
    fecha_creacion = models.DateField(db_column='FECHA_CREACION', auto_now_add=True)
    tipo_grupo = models.CharField(max_length=40, db_column='TIPO_GRUPO', default='Club')
    logo = models.BinaryField(db_column='LOGO', null=True, blank=True)
    correo_grupo = models.CharField(max_length=128, db_column='CORREO_GRUPO')
    descripcion = models.TextField(db_column='DESCRIPCION')
    link_whatsapp = models.CharField(max_length=128, db_column='LINK_WHATSAPP', blank=True, null=True)

    class Meta:
        db_table = 'GRUPO'
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'

    def __str__(self):
        return self.nombre_grupo
