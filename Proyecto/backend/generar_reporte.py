


import subprocess
import datetime
import os


def ejecutar_pylint_en_carpetas():
    """
    Ejecuta pylint en las carpetas especificadas y genera reportes.
    
    Returns:
        list: Lista con los nombres de los archivos de reporte generados
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    carpetas = ["grupos", "project"]
    archivos_generados = []
    
    print("=== GENERANDO REPORTES PYLINT ===")
    
    for carpeta in carpetas:
        if os.path.exists(carpeta):
            print(f"\n--- Analizando: {carpeta} ---")
            
            # Ejecutar pylint para la carpeta actual
            resultado = subprocess.run(
                [
                    'pylint', 
                    '--load-plugins', 'pylint_django',
                    '--rcfile=.pylintrc',
                    '--reports=yes',
                    carpeta
                ], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            # Guardar reporte individual
            nombre_individual = f"pylint_{carpeta}_{timestamp}.txt"
            with open(nombre_individual, 'w', encoding='utf-8') as archivo:
                archivo.write(resultado.stdout)
                if resultado.stderr:
                    archivo.write("\n--- ERRORES ---\n")
                    archivo.write(resultado.stderr)
            
            archivos_generados.append(nombre_individual)
            print(f"Reporte individual: {nombre_individual}")
        else:
            print(f"¡Advertencia: La carpeta '{carpeta}' no existe!")
    
    # Reporte combinado
    print("\n--- Reporte Combinado ---")
    resultado_combinado = subprocess.run(
        [
            'pylint', 
            '--load-plugins', 'pylint_django',
            '--rcfile=.pylintrc',
            '--reports=yes',
            'grupos/', 'project/'
        ], 
        capture_output=True, 
        text=True,
        check=False
    )
    
    nombre_combinado = f"pylint_completo_{timestamp}.txt"
    with open(nombre_combinado, 'w', encoding='utf-8') as archivo:
        archivo.write(resultado_combinado.stdout)
        if resultado_combinado.stderr:
            archivo.write("\n--- ERRORES ---\n")
            archivo.write(resultado_combinado.stderr)
    
    archivos_generados.append(nombre_combinado)
    print(f"Reporte combinado: {nombre_combinado}")
    print("\n=== ANÁLISIS COMPLETADO ===")
    
    return archivos_generados


if __name__ == "__main__":
    ejecutar_pylint_en_carpetas()
