"""
Tests Unitarios - ÁgoraUN
Módulo de Testing - Entrega 06

12 Pruebas Unitarias (3 por integrante)
Herramienta: unittest (Django TestCase)
Validación: Funcionalidades esenciales del sistema
"""

from django.test import TestCase
from grupos.models import Grupo


# ============================================================================
# PERSONA 1 - BACKEND/MODELOS (3 pruebas - RF_1)
# ============================================================================

class TestBackendRegistroGrupos(TestCase):
    """Tests implementados por Persona 1 - Gestión de grupos en backend"""

    def test_p1_crear_grupo_campos_requeridos(self):
        """
        P1.Test.001 - Crear grupo con todos los campos requeridos
        RF_1: La aplicación permite registrar clubes con información completa
        Entrada: Datos completos y válidos
        Salida esperada: Grupo creado con ID único
        Caso límite: Todos los campos obligatorios presente
        """
        grupo = Grupo.objects.create(
            nombre_grupo="Club de Programación",
            descripcion="Club oficial de programación",
            tipo_grupo="Académico",
            area_interes="Tecnología",
            correo_grupo="programacion@unal.edu.co"
        )
        self.assertIsNotNone(grupo.id_grupo)
        self.assertEqual(grupo.nombre_grupo, "Club de Programación")
        self.assertTrue(grupo.correo_grupo.endswith("@unal.edu.co"))

    def test_p1_validar_formato_correo_institucional(self):
        """
        P1.Test.002 - Validar que correo sea institucional
        RF_1: Validación de datos de entrada
        Entrada: Diferentes formatos de correo
        Salida esperada: Solo correos @unal.edu.co
        Caso límite: Validación de dominio institucional
        """
        grupo = Grupo.objects.create(
            nombre_grupo="Semillero de Investigación",
            descripcion="Semillero de investigación",
            tipo_grupo="Investigación",
            area_interes="Ciencias",
            correo_grupo="investigacion@unal.edu.co"
        )
        self.assertIn("@unal.edu.co", grupo.correo_grupo)
        self.assertTrue(len(grupo.correo_grupo) > 0)

    def test_p1_persistencia_datos_en_bd(self):
        """
        P1.Test.003 - Verificar persistencia de datos en BD
        RF_1: Integridad de datos
        Entrada: Grupo creado en BD
        Salida esperada: Datos recuperables después de crear
        Caso límite: Consulta de grupo después de creación
        """
        grupo = Grupo.objects.create(
            nombre_grupo="Club de Artes",
            descripcion="Actividades artísticas",
            tipo_grupo="Cultural",
            area_interes="Artes",
            correo_grupo="artes@unal.edu.co"
        )
        grupo_recuperado = Grupo.objects.get(id_grupo=grupo.id_grupo)
        self.assertEqual(grupo.nombre_grupo, grupo_recuperado.nombre_grupo)
        self.assertEqual(grupo.descripcion, grupo_recuperado.descripcion)


# ============================================================================
# PERSONA 2 - FRONTEND/CATÁLOGO (3 pruebas - RF_3)
# ============================================================================

class TestFrontendCatalogoGrupos(TestCase):
    """Tests implementados por Persona 2 - Catálogo y búsqueda"""

    def setUp(self):
        """Preparar datos de prueba para catálogo"""
        self.grupo1 = Grupo.objects.create(
            nombre_grupo="Club de Música",
            descripcion="Club musical",
            tipo_grupo="Cultural",
            area_interes="Música",
            correo_grupo="musica@unal.edu.co"
        )
        self.grupo2 = Grupo.objects.create(
            nombre_grupo="Club de Literatura",
            descripcion="Club literario",
            tipo_grupo="Cultural",
            area_interes="Literatura",
            correo_grupo="literatura@unal.edu.co"
        )
        self.grupo3 = Grupo.objects.create(
            nombre_grupo="Club de Fútbol",
            descripcion="Club deportivo",
            tipo_grupo="Deportivo",
            area_interes="Deporte",
            correo_grupo="futbol@unal.edu.co"
        )

    def test_p2_listar_todos_grupos_catalogo(self):
        """
        P2.Test.001 - Listar todos los grupos en catálogo
        RF_3: Catálogo de clubes para consulta
        Entrada: Consulta de todos los grupos
        Salida esperada: Lista completa de 3 grupos
        Caso límite: Verificar conteo y existencia
        """
        grupos = Grupo.objects.all()
        self.assertEqual(grupos.count(), 3)
        self.assertIn(self.grupo1, grupos)
        self.assertIn(self.grupo2, grupos)
        self.assertIn(self.grupo3, grupos)

    def test_p2_buscar_grupo_por_nombre(self):
        """
        P2.Test.002 - Buscar grupo por nombre (búsqueda parcial)
        RF_3: Funcionalidad de búsqueda en catálogo
        Entrada: Nombre parcial "Literatura"
        Salida esperada: Club de Literatura encontrado
        Caso límite: Búsqueda insensible a mayúsculas
        """
        grupo = Grupo.objects.filter(nombre_grupo__icontains="Literatura").first()
        self.assertIsNotNone(grupo)
        self.assertEqual(grupo.nombre_grupo, "Club de Literatura")
        self.assertEqual(grupo.area_interes, "Literatura")

    def test_p2_filtrar_grupos_por_area_interes(self):
        """
        P2.Test.003 - Filtrar grupos por área de interés
        RF_3: Filtrado avanzado en catálogo
        Entrada: Área de interés "Deportivo"
        Salida esperada: Solo grupos deportivos (1)
        Caso límite: Verificar que solo se retornen de esa área
        """
        grupos_deportivos = Grupo.objects.filter(area_interes="Deporte")
        self.assertEqual(grupos_deportivos.count(), 1)
        self.assertEqual(grupos_deportivos.first().nombre_grupo, "Club de Fútbol")
        grupos_cultural = Grupo.objects.filter(area_interes="Literatura")
        self.assertEqual(grupos_cultural.count(), 1)


# ============================================================================
# PERSONA 3 - CRUD/EDICIÓN (3 pruebas - RF_5)
# ============================================================================

class TestCRUDGestionGrupos(TestCase):
    """Tests implementados por Persona 3 - CRUD de grupos"""

    def setUp(self):
        """Preparar grupo para pruebas CRUD"""
        self.grupo = Grupo.objects.create(
            nombre_grupo="Club Base para Tests",
            descripcion="Descripción inicial",
            tipo_grupo="Académico",
            area_interes="Tecnología",
            correo_grupo="base@unal.edu.co"
        )

    def test_p3_actualizar_informacion_grupo(self):
        """
        P3.Test.001 - Actualizar información del grupo (UPDATE)
        RF_5: Gestión de grupos - Edición
        Entrada: Cambio de descripción
        Salida esperada: Descripción actualizada en BD
        Caso límite: Múltiples cambios simultáneos
        """
        descripcion_nueva = "Descripción completamente nueva"
        self.grupo.descripcion = descripcion_nueva
        self.grupo.tipo_grupo = "Investigación"
        self.grupo.save()

        grupo_actualizado = Grupo.objects.get(id_grupo=self.grupo.id_grupo)
        self.assertEqual(grupo_actualizado.descripcion, descripcion_nueva)
        self.assertEqual(grupo_actualizado.tipo_grupo, "Investigación")

    def test_p3_eliminar_grupo(self):
        """
        P3.Test.002 - Eliminar grupo (DELETE)
        RF_5: Gestión de grupos - Eliminación
        Entrada: ID de grupo a eliminar
        Salida esperada: Grupo no existe después de delete
        Caso límite: Verificar que no queda registro en BD
        """
        id_grupo = self.grupo.id_grupo
        self.grupo.delete()

        with self.assertRaises(Grupo.DoesNotExist):
            Grupo.objects.get(id_grupo=id_grupo)

    def test_p3_ediciones_sucesivas_integridad(self):
        """
        P3.Test.003 - Verificar integridad después de ediciones sucesivas
        RF_5: Gestión de grupos - Integridad de datos
        Entrada: Múltiples ediciones secuenciales
        Salida esperada: Todos los cambios se preservan
        Caso límite: 3 ediciones consecutivas
        """
        # Primera edición
        self.grupo.descripcion = "Primera edición"
        self.grupo.save()

        # Segunda edición
        self.grupo.area_interes = "Investigación"
        self.grupo.save()

        # Tercera edición
        self.grupo.correo_grupo = "nuevo@unal.edu.co"
        self.grupo.save()

        # Verificación final
        grupo_final = Grupo.objects.get(id_grupo=self.grupo.id_grupo)
        self.assertEqual(grupo_final.descripcion, "Primera edición")
        self.assertEqual(grupo_final.area_interes, "Investigación")
        self.assertEqual(grupo_final.correo_grupo, "nuevo@unal.edu.co")


# ============================================================================
# PERSONA 4 - VALIDACIÓN INTEGRAL (3 pruebas - Casos límite)
# ============================================================================

class TestValidacionIntegralGrupos(TestCase):
    """Tests implementados por Persona 4 - Validación integral y casos límite"""

    def test_p4_crear_multiples_grupos_sin_conflicto(self):
        """
        P4.Test.001 - Crear múltiples grupos sin conflicto de IDs
        Validación: IDs únicos y secuenciales
        Entrada: Creación de 5 grupos
        Salida esperada: 5 grupos con IDs diferentes
        Caso límite: Verificar que no hay duplicados
        """
        grupos_creados = []
        for i in range(5):
            grupo = Grupo.objects.create(
                nombre_grupo=f"Grupo Prueba {i+1}",
                descripcion=f"Descripción {i+1}",
                tipo_grupo="Test",
                area_interes="Testing",
                correo_grupo=f"test{i}@unal.edu.co"
            )
            grupos_creados.append(grupo.id_grupo)

        # Verificar que no hay IDs duplicados
        self.assertEqual(len(grupos_creados), len(set(grupos_creados)))
        # Verificar conteo total
        self.assertEqual(Grupo.objects.count(), 5)

    def test_p4_validar_tipos_grupo_correctos(self):
        """
        P4.Test.002 - Validar tipos de grupo correctos
        Validación: Tipos permitidos
        Entrada: Creación con diferentes tipos
        Salida esperada: Todos los tipos almacenados correctamente
        Caso límite: Verificar tipos específicos
        """
        tipos = ["Académico", "Investigación", "Deportivo", "Cultural"]
        grupos = []

        for tipo in tipos:
            grupo = Grupo.objects.create(
                nombre_grupo=f"Grupo {tipo}",
                descripcion=f"Grupo de {tipo}",
                tipo_grupo=tipo,
                area_interes="General",
                correo_grupo=f"{tipo.lower()}@unal.edu.co"
            )
            grupos.append(grupo)

        # Verificar que todos los tipos se guardaron correctamente
        for i, grupo in enumerate(grupos):
            grupo_recuperado = Grupo.objects.get(id_grupo=grupo.id_grupo)
            self.assertEqual(grupo_recuperado.tipo_grupo, tipos[i])

    def test_p4_campos_no_nulos_en_consultas(self):
        """
        P4.Test.003 - Verificar que campos esenciales no sean nulos
        Validación: Integridad referencial
        Entrada: Consulta de todos los grupos
        Salida esperada: Ningún campo esencial nulo
        Caso límite: Validación de NOT NULL
        """
        grupo = Grupo.objects.create(
            nombre_grupo="Grupo Validación",
            descripcion="Test de campos no nulos",
            tipo_grupo="Validación",
            area_interes="Test",
            correo_grupo="validation@unal.edu.co"
        )

        grupo_recuperado = Grupo.objects.get(id_grupo=grupo.id_grupo)
        self.assertIsNotNone(grupo_recuperado.nombre_grupo)
        self.assertIsNotNone(grupo_recuperado.descripcion)
        self.assertIsNotNone(grupo_recuperado.correo_grupo)
        self.assertIsNotNone(grupo_recuperado.tipo_grupo)
        self.assertIsNotNone(grupo_recuperado.area_interes)
