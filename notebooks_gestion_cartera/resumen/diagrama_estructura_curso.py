"""
Script para generar el diagrama de flujo de la estructura del curso
de Gestión de Carteras.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Configuración (ACTUALIZADO con TEMA 4)
fig, ax = plt.subplots(figsize=(22, 18))
ax.set_xlim(0, 10)
ax.set_ylim(0, 14)
ax.axis('off')

# Definir las cajas principales
cajas = [
    # Nivel superior - Título principal
    (5, 12, 'MÓDULO 2: GESTIÓN DE CARTERAS\nObjetivo: Teoría Moderna de Carteras + CAPM', '#1a237e', 3.2, 0.8),
    
    # Tema 1 - Rama izquierda
    (2, 10, 'TEMA 1\nIntroducción Carteras', '#1565c0', 1.8, 0.8),
    (2, 8.6, '1.1\nCarteras\n2 Activos', '#42a5f5', 1.4, 0.6),
    (2, 7.6, '1.2\nCarteras\n4 Activos', '#42a5f5', 1.4, 0.6),
    (2, 6.6, '1.3\nDiversificación', '#42a5f5', 1.4, 0.6),
    (2, 5.6, 'Apéndice\nFórmulas', '#90caf9', 1.4, 0.6),
    
    # Tema 2 - Rama central
    (5, 10, 'TEMA 2\nMarkowitz y Tobin', '#c62828', 1.8, 0.8),
    (5, 8.6, '2.1\nOptimización\nMedia-Varianza', '#ef5350', 1.4, 0.6),
    (5, 7.6, '2.2\nConceptos\nOptimización', '#ef5350', 1.4, 0.6),
    (5, 6.6, '2.3\nCVXPY', '#ef5350', 1.4, 0.6),
    (5, 5.6, '2.4\nMarkowitz', '#ef5350', 1.4, 0.6),
    (5, 4.6, '2.5\nPosiciones Cortas', '#ef5350', 1.4, 0.6),
    (5, 3.6, '2.6\nTeoría de Tobin', '#ef5350', 1.4, 0.6),
    
    # Tema 3 - Rama derecha
    (8, 10, 'TEMA 3\nCAPM y Modelo\nMercado', '#f57c00', 1.8, 0.8),
    (8, 8.6, '3.2\nCAPM', '#ff9800', 1.4, 0.6),
    (8, 7.6, '3.3\nModelo de\nMercado', '#ff9800', 1.4, 0.6),
    (8, 6.6, '3.4\nEjercicio\nSP500', '#ffb74d', 1.4, 0.6),
    
    # Tema 4 - Rama inferior derecha (ACTUALIZADO con 4.2 y 4.3)
    (8, 5.2, 'TEMA 4\nSmart Betas\nMultifactorial', '#6a1b9a', 1.8, 0.8),
    (8, 4.0, '4.1\nAPT/Fama-\nFrench', '#9c27b0', 1.4, 0.6),
    (8, 2.8, '4.2\nAnálisis\nFondos', '#9c27b0', 1.4, 0.6),
    (8, 1.6, '4.3\nCarteras\nFactores', '#9c27b0', 1.4, 0.6),
    
    # Conceptos clave - Parte inferior
    (1, 1.5, 'CORRELACIÓN\nρ', '#81c784', 1, 0.4),
    (3, 1.5, 'DIVERSIFICACIÓN\nRiesgo', '#81c784', 1, 0.4),
    (5, 1.5, 'FRONTERA\nEFICIENTE\nCML', '#81c784', 1, 0.4),
    (7, 1.5, 'CAPM\nBeta\nSML', '#81c784', 1, 0.4),
    (9, 1.5, 'ALPHA\nRiesgo', '#81c784', 1, 0.4),
    (8, 1.5, 'FACTORES\nSMB/HML\nMOM', '#81c784', 1, 0.4),
]

# Dibujar cajas
for x, y, text, color, width, height in cajas:
    box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                        boxstyle="round,pad=0.05",
                        facecolor=color, edgecolor='black', linewidth=2, alpha=0.9)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center',
           fontsize=7, fontweight='bold', color='white')

# Flechas principales (ACTUALIZADO con TEMA 3)
flechas_principales = [
    # De título a temas
    ((5, 11.6), (2.5, 10.4)),
    ((5, 11.6), (5, 10.4)),
    ((5, 11.6), (7.5, 10.4)),
    
    # Tema 1 - Flujo vertical
    ((2, 9.6), (2, 9.1)),
    ((2, 8.3), (2, 7.9)),
    ((2, 7.3), (2, 6.9)),
    ((2, 6.3), (2, 5.9)),
    
    # Tema 2 - Flujo vertical
    ((5, 9.6), (5, 9.1)),
    ((5, 8.3), (5, 7.9)),
    ((5, 7.3), (5, 6.9)),
    ((5, 6.3), (5, 5.9)),
    ((5, 5.3), (5, 4.9)),
    ((5, 4.3), (5, 3.9)),
    
    # Tema 3 - Flujo vertical
    ((8, 9.6), (8, 9.1)),
    ((8, 8.3), (8, 7.9)),
    ((8, 7.3), (8, 6.9)),
    
    # Tema 4 - Flujo vertical (ACTUALIZADO con 4.2 y 4.3)
    ((8, 9.6), (8, 5.6)),
    ((8, 4.8), (8, 4.3)),
    ((8, 3.7), (8, 3.1)),
    ((8, 2.5), (8, 1.9)),
    
    # Conexiones entre temas
    ((3.5, 5.5), (4.5, 5.5), 'Conceptos\nFundamentales'),
    ((5.5, 3.5), (7.5, 8.5), 'Extensión\nCAPM'),
    ((8, 6.3), (8, 5.6), 'Extensión\nMultifactorial'),
    
    # A conceptos clave
    ((2, 5.3), (1, 1.9), 'ρ'),
    ((2, 6.3), (3, 1.9), 'Diversificación'),
    ((5, 3.3), (5, 1.9), 'CML'),
    ((8, 7.3), (7, 1.9), 'Beta'),
    ((8, 6.3), (9, 1.9), 'Alpha'),
    ((8, 1.3), (8, 1.9), 'Factores'),
]

# Dibujar flechas
for i, flecha in enumerate(flechas_principales):
    if len(flecha) == 2:
        start, end = flecha
        arrow = FancyArrowPatch(start, end,
                              arrowstyle='->', lw=2,
                              color='black', mutation_scale=20, alpha=0.8)
        ax.add_patch(arrow)
    else:
        start, end, label = flecha
        arrow = FancyArrowPatch(start, end,
                              arrowstyle='->', lw=2.5,
                              color='#ff6f00', mutation_scale=25, alpha=0.9)
        ax.add_patch(arrow)
        # Añadir etiqueta en el medio de la flecha
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.1, label, ha='center', va='bottom',
               fontsize=8, fontweight='bold', color='#ff6f00',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

# Añadir título principal
plt.title('DIAGRAMA DE FLUJO: ESTRUCTURA DEL CURSO DE GESTIÓN DE CARTERAS',
         fontsize=18, fontweight='bold', pad=30)

# Añadir leyenda de colores (ACTUALIZADA)
legend_elements = [
    mpatches.Patch(facecolor='#1565c0', label='Tema 1: Introducción Carteras'),
    mpatches.Patch(facecolor='#c62828', label='Tema 2: Markowitz y Tobin'),
    mpatches.Patch(facecolor='#f57c00', label='Tema 3: CAPM y Modelo de Mercado'),
    mpatches.Patch(facecolor='#6a1b9a', label='Tema 4: Smart Betas'),
    mpatches.Patch(facecolor='#81c784', label='Conceptos Clave'),
    mpatches.Patch(facecolor='#ff6f00', label='Conexión Conceptual')
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1),
         fontsize=10, framealpha=0.9)

plt.tight_layout()
plt.savefig('diagrama_estructura_curso.png', dpi=300, bbox_inches='tight')
print("Diagrama guardado como 'diagrama_estructura_curso.png'")
plt.show()
