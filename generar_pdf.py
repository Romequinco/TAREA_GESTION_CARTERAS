"""
Script para convertir el reporte HTML a PDF usando playwright
"""
import os
import sys
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def generar_pdf_playwright():
    """Convierte el HTML a PDF usando playwright"""
    try:
        from playwright.sync_api import sync_playwright
        print("playwright importado correctamente")
    except ImportError:
        print("ERROR: playwright no esta instalado.")
        print("Instalalo con: pip install playwright")
        print("Luego ejecuta: playwright install chromium")
        return False
    
    # Rutas de archivos
    ruta_html = Path('REPORTE_TECNICO_OPTIMIZACION_CARTERAS.html').absolute()
    ruta_pdf = Path('REPORTE_TECNICO_OPTIMIZACION_CARTERAS.pdf')
    
    # Verificar que el HTML existe
    if not ruta_html.exists():
        print(f"ERROR: No se encuentra el archivo {ruta_html}")
        return False
    
    print(f"Convirtiendo {ruta_html.name} a PDF usando Playwright...")
    
    try:
        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Cargar el HTML
            page.goto(f"file:///{ruta_html.as_posix()}")
            
            # Esperar a que las imágenes se carguen
            page.wait_for_timeout(3000)
            
            # Generar PDF con configuración para impresión
            page.pdf(
                path=str(ruta_pdf),
                format='A4',
                margin={
                    'top': '2cm',
                    'right': '2cm',
                    'bottom': '2cm',
                    'left': '2cm'
                },
                print_background=True,
                prefer_css_page_size=False
            )
            
            browser.close()
        
        size_kb = ruta_pdf.stat().st_size / 1024
        print(f"PDF generado exitosamente: {ruta_pdf}")
        print(f"  Tamano del archivo: {size_kb:.2f} KB")
        return True
        
    except Exception as e:
        print(f"ERROR al generar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def generar_pdf_xhtml2pdf():
    """Convierte el HTML a PDF usando xhtml2pdf (alternativa mas simple)"""
    try:
        from xhtml2pdf import pisa
        print("xhtml2pdf importado correctamente")
    except ImportError:
        print("ERROR: xhtml2pdf no esta instalado.")
        print("Instalalo con: pip install xhtml2pdf")
        return False
    
    # Rutas de archivos
    ruta_html = Path('REPORTE_TECNICO_OPTIMIZACION_CARTERAS.html')
    ruta_pdf = Path('REPORTE_TECNICO_OPTIMIZACION_CARTERAS.pdf')
    
    # Verificar que el HTML existe
    if not ruta_html.exists():
        print(f"ERROR: No se encuentra el archivo {ruta_html}")
        return False
    
    print(f"Convirtiendo {ruta_html.name} a PDF usando xhtml2pdf...")
    
    try:
        # Leer el HTML con encoding UTF-8
        with open(ruta_html, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        
        # Convertir a PDF
        with open(ruta_pdf, 'wb') as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file,
                encoding='utf-8'
            )
        
        if pisa_status.err:
            print(f"ERROR: {pisa_status.err}")
            return False
        
        size_kb = ruta_pdf.stat().st_size / 1024
        print(f"PDF generado exitosamente: {ruta_pdf}")
        print(f"  Tamano del archivo: {size_kb:.2f} KB")
        return True
        
    except Exception as e:
        print(f"ERROR al generar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Intentar primero con playwright (mejor calidad)
    if generar_pdf_playwright():
        exit(0)
    
    # Si falla, intentar con xhtml2pdf
    print("\nIntentando con xhtml2pdf como alternativa...")
    if generar_pdf_xhtml2pdf():
        exit(0)
    
    print("\n" + "="*60)
    print("No se pudo generar el PDF automaticamente.")
    print("\nAlternativas:")
    print("1. Abre REPORTE_TECNICO_OPTIMIZACION_CARTERAS.html en tu navegador")
    print("2. Presiona Ctrl+P (o Cmd+P en Mac)")
    print("3. Selecciona 'Guardar como PDF'")
    print("="*60)
