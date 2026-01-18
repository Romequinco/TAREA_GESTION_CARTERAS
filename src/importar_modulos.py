"""
Script auxiliar para importar módulos que empiezan con números.
En Python, los nombres de módulo que empiezan con números no se pueden
importar directamente, por lo que usamos importlib.
"""

import importlib
import sys

# Función auxiliar para importar módulos con nombres que empiezan con números
def importar_modulo(nombre_modulo):
    """
    Importa un módulo cuyo nombre empieza con número.
    
    Parámetros:
    -----------
    nombre_modulo : str
        Nombre del módulo (ej: '1datos', '2markowitz')
        
    Retorna:
    --------
    module
        Módulo importado
    """
    return importlib.import_module(nombre_modulo)

# Importar todos los módulos
datos = importar_modulo('1datos')
equiponderada = importar_modulo('2equiponderada_diversificacion')
markowitz = importar_modulo('3markowitz')
validacion = importar_modulo('4validacion')

# Hacer disponibles en el namespace
sys.modules['datos'] = datos
sys.modules['equiponderada'] = equiponderada
sys.modules['markowitz'] = markowitz
sys.modules['validacion'] = validacion
