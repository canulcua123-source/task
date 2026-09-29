#!/usr/bin/env python3
"""Genera el ensayo sobre el Capítulo 1 de The Mythical Man-Month como Word con portada UTM."""

from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "entregas" / "formulacion de proyecto"
OUTPUT_DOCX = OUTPUT_DIR / "formulacion_1_Ensayo_Mythical_Man_Month.docx"


def crear_portada_imagen():
    """Genera portada estilo UTM como imagen."""
    W, H = 2480, 3508  # A4 a 300 DPI
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Barras laterales
    colors = [(0, 51, 102), (0, 76, 140), (51, 122, 183), (100, 160, 210), (173, 200, 230)]
    x = 80
    for c in colors:
        draw.rectangle([x, 0, x + 50, H], fill=c)
        x += 65

    cc = W // 2 + 100  # centro del contenido

    try:
        font_b_xl = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 120)
        font_b_lg = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 72)
        font_b_md = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 52)
        font_r_md = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 48)
        font_r_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 42)
    except Exception:
        font_b_xl = ImageFont.load_default()
        font_b_lg = font_b_md = font_r_md = font_r_sm = font_b_xl

    y = 300
    draw.text((cc, y), "UTM", fill=(0, 128, 0), font=font_b_xl, anchor="mt")
    y += 180
    draw.text((cc, y), "UNIVERSIDAD TECNOLÓGICA", fill=(0, 0, 0), font=font_b_lg, anchor="mt")
    y += 90
    draw.text((cc, y), "METROPOLITANA", fill=(0, 0, 0), font=font_b_lg, anchor="mt")
    y += 140
    draw.text((cc, y), "TECNOLOGÍAS DE LA INFORMACIÓN", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 70
    draw.text((cc, y), "INNOVACIÓN DIGITAL", fill=(0, 51, 102), font=font_b_md, anchor="mt")

    y += 150
    draw.text((cc, y), "Actividad:", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 70
    draw.text((cc, y), "Ensayo sobre el Capítulo 1 de", fill=(0, 0, 0), font=font_r_md, anchor="mt")
    y += 60
    draw.text((cc, y), "The Mythical Man-Month", fill=(0, 0, 0), font=font_r_md, anchor="mt")

    y += 120
    draw.text((cc, y), "Materia:", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 70
    draw.text((cc, y), "Formulación de Proyectos de TI", fill=(0, 0, 0), font=font_r_md, anchor="mt")

    y += 120
    draw.text((cc, y), "Maestro:", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 70
    draw.text((cc, y), "Por confirmar", fill=(0, 0, 0), font=font_r_md, anchor="mt")

    y += 120
    draw.text((cc, y), "Integrantes:", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 70
    draw.text((cc, y), "Jesús Guadalupe Canul", fill=(0, 0, 0), font=font_r_sm, anchor="mt")

    y += 120
    draw.text((cc, y), "Grado: 7° Cuatrimestre", fill=(0, 51, 102), font=font_b_md, anchor="mt")
    y += 65
    draw.text((cc, y), "Grupo: A", fill=(0, 51, 102), font=font_b_md, anchor="mt")

    portada_path = BASE_DIR / "assets" / "portada_ensayo_temp.png"
    img.save(str(portada_path), "PNG", quality=95)
    return str(portada_path)


def main():
    doc = Document()

    # --- PORTADA ---
    section = doc.sections[0]
    section.top_margin = Cm(0)
    section.bottom_margin = Cm(0)
    section.left_margin = Cm(0)
    section.right_margin = Cm(0)

    portada_path = crear_portada_imagen()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    page_w = section.page_width
    page_h = section.page_height
    run.add_picture(portada_path, width=page_w, height=page_h)

    # --- Salto de página y márgenes normales ---
    new_section = doc.add_section()
    new_section.top_margin = Cm(2.5)
    new_section.bottom_margin = Cm(2.5)
    new_section.left_margin = Cm(2.5)
    new_section.right_margin = Cm(2.5)

    # --- CONTENIDO DEL ENSAYO ---

    # Título
    h = doc.add_heading("Ensayo: El pozo de alquitrán", level=1)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)

    sub = doc.add_paragraph()
    run = sub.add_run("Capítulo 1 de \"The Mythical Man-Month\" — Frederick P. Brooks Jr.")
    run.font.size = Pt(11)
    run.italic = True
    run.font.color.rgb = RGBColor(100, 100, 100)
    sub.paragraph_format.space_after = Pt(18)

    # Helper para agregar párrafos con formato
    def parrafo(texto, bold_first=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.5
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_first:
            r = p.add_run(bold_first)
            r.bold = True
            r.font.size = Pt(12)
            r = p.add_run(texto)
            r.font.size = Pt(12)
        else:
            r = p.add_run(texto)
            r.font.size = Pt(12)
        return p

    def subtitulo(texto):
        h = doc.add_heading(texto, level=2)
        for run in h.runs:
            run.font.color.rgb = RGBColor(0, 51, 102)
        return h

    # --- INTRODUCCIÓN ---
    subtitulo("Introducción")

    parrafo(
        "Cuando uno empieza a programar, todo parece sencillo: abres un editor, escribes unas "
        "líneas de código, lo corres y funciona. Esa sensación de crear algo de la nada es lo que "
        "engancha a la mayoría de los que estudiamos desarrollo de software. Pero conforme los "
        "proyectos crecen, esa simplicidad se convierte en algo muy diferente. Frederick Brooks, "
        "en el primer capítulo de su libro \"The Mythical Man-Month\", lo compara con un pozo de "
        "alquitrán: un lugar donde entre más luchas por avanzar, más te hundes. Este capítulo me "
        "hizo reflexionar sobre lo que realmente implica desarrollar software a gran escala y por "
        "qué tantos proyectos terminan fallando a pesar de tener programadores talentosos."
    )

    # --- DESARROLLO ---
    subtitulo("El programa vs. el producto: no es lo mismo")

    parrafo(
        "Una de las ideas que más me llamó la atención del capítulo es la distinción que hace "
        "Brooks entre un programa y un producto de programación. Un programa es algo que tú haces "
        "para ti mismo: funciona en tu máquina, tú sabes cómo usarlo y si se rompe, tú lo arreglas. "
        "Pero un producto de programación es otra cosa completamente diferente. Necesita documentación, "
        "pruebas, manejo de errores, interfaces claras, y tiene que funcionar en ambientes que tú no "
        "controlas. Brooks dice que pasar de un programa a un producto cuesta al menos tres veces más "
        "esfuerzo. Y si además tiene que funcionar como parte de un sistema más grande, el costo se "
        "multiplica por nueve."
    )

    parrafo(
        "Esto lo he vivido en mis propios proyectos de la carrera. A veces hago un script en Python "
        "que me funciona perfecto en mi laptop, pero cuando lo tengo que entregar como un proyecto "
        "formal, con base de datos, con interfaz, con validaciones, el trabajo se multiplica "
        "enormemente. Y ni hablar cuando hay que trabajar en equipo: el código que escribo tiene que "
        "ser entendible para los demás, tiene que integrarse con lo que ellos hicieron, y todo tiene "
        "que probarse en conjunto. Es exactamente lo que Brooks describe: el pozo de alquitrán donde "
        "cada paso cuesta más de lo que esperabas."
    )

    subtitulo("Las alegrías de programar")

    parrafo(
        "Algo que me gustó mucho del capítulo es que Brooks no solo habla de lo difícil que es "
        "el desarrollo de software, sino que también reconoce por qué nos gusta. Identifica cinco "
        "alegrías de programar que yo comparto completamente:"
    )

    # Lista
    joys = [
        "La alegría de crear cosas. Hay algo profundamente satisfactorio en construir algo que "
        "antes no existía. Es como ser un artesano digital: diseñas, construyes y al final tienes "
        "algo funcional que puedes ver y usar.",

        "El placer de hacer cosas útiles para otros. Cuando alguien usa tu software y le resuelve "
        "un problema real, esa sensación no tiene precio. No es solo código, es una herramienta "
        "que le facilita la vida a alguien.",

        "La fascinación de armar rompecabezas complejos. Programar es resolver problemas constantemente. "
        "Cada bug es un misterio, cada algoritmo es un acertijo. Para los que nos gusta pensar, eso "
        "es adictivo.",

        "El aprendizaje continuo. En esta carrera nunca dejas de aprender. Cada proyecto te obliga "
        "a investigar algo nuevo, a usar una tecnología diferente, a pensar de otra manera.",

        "Trabajar con un medio maleable. A diferencia de un ingeniero civil que trabaja con concreto, "
        "nosotros trabajamos con algo que podemos cambiar fácilmente. Si algo no funciona, lo reescribes. "
        "El software es flexible, y eso nos da mucha libertad creativa.",
    ]

    for joy in joys:
        p = doc.add_paragraph(joy, style="List Bullet")
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.5
        for run in p.runs:
            run.font.size = Pt(12)

    subtitulo("Los sufrimientos del oficio")

    parrafo(
        "Pero así como hay alegrías, Brooks también describe los sufrimientos que vienen con el "
        "trabajo. Y creo que cualquier persona que ha programado en equipo o en un proyecto grande "
        "puede identificarse con esto:"
    )

    parrafo(
        "Primero, la exigencia de perfección. La computadora no perdona: si falta un punto y coma, "
        "una variable mal nombrada o un caso borde que no contemplaste, todo se cae. Ninguna otra "
        "disciplina exige tanta precisión en cada detalle. En un ensayo puedes tener un error "
        "ortográfico y se entiende igual; en código, un carácter mal puesto puede hacer que toda "
        "la aplicación falle."
    )

    parrafo(
        "Segundo, la dependencia de otros. En proyectos reales, rara vez decides tú solo qué hacer "
        "y cómo hacerlo. Los objetivos los pone el cliente, los plazos los pone el jefe, y las "
        "restricciones las pone la tecnología disponible. Brooks señala que esto puede ser "
        "frustrante para alguien que está acostumbrado a la libertad creativa de programar solo."
    )

    parrafo(
        "Tercero, el miedo a la obsolescencia. En nuestra carrera todo cambia muy rápido. El "
        "framework que aprendiste hace dos años ya tiene una versión completamente nueva, el "
        "lenguaje que dominabas ya tiene un competidor que todos prefieren. Hay que estar "
        "constantemente actualizándose, y eso puede ser agotador."
    )

    subtitulo("Relación con los proyectos de software actuales")

    parrafo(
        "Lo más impresionante de este capítulo es que fue escrito en 1975, pero sus ideas siguen "
        "siendo completamente vigentes. En la industria del software actual seguimos cayendo en "
        "el mismo pozo de alquitrán. Proyectos que se estiman en tres meses terminan tardando un "
        "año. Equipos de desarrollo que crecen pero en vez de avanzar más rápido se hacen más "
        "lentos por la complejidad de la comunicación. Software que funciona en desarrollo pero "
        "falla en producción porque nadie probó todos los casos."
    )

    parrafo(
        "En mi experiencia como estudiante de TI, he visto cómo proyectos en equipo sufren "
        "exactamente de estos problemas. Cuando trabajamos en el taller mecánico que desarrollamos "
        "para la materia de bases de datos, lo que empezó como \"un CRUD sencillo\" terminó siendo "
        "un sistema con múltiples tablas relacionadas, validaciones, vistas y consultas complejas. "
        "El esfuerzo real fue mucho mayor que el estimado, porque no solo era escribir código: era "
        "diseñar una base de datos coherente, documentar, probar y asegurar que todo funcionara "
        "junto. Exactamente el multiplicador ×9 que Brooks describe."
    )

    parrafo(
        "Las metodologías ágiles que usamos hoy, como Scrum, son en parte una respuesta a los "
        "problemas que Brooks identificó hace casi 50 años. Los sprints cortos, las entregas "
        "incrementales y la comunicación constante con el cliente son formas de evitar hundirse "
        "en el pozo de alquitrán. Pero aun así, la esencia del problema sigue ahí: el software "
        "es inherentemente complejo, y esa complejidad no se puede eliminar, solo se puede gestionar."
    )

    # --- CONCLUSIÓN ---
    subtitulo("Conclusión")

    parrafo(
        "El capítulo 1 de \"The Mythical Man-Month\" es una lectura que debería ser obligatoria "
        "para cualquier estudiante de desarrollo de software. No porque diga algo que no sepamos "
        "intuitivamente, sino porque le pone nombre y estructura a lo que todos hemos sentido: "
        "que programar es maravilloso y tortuoso al mismo tiempo, que un proyecto de software es "
        "mucho más que escribir código, y que la complejidad se multiplica de formas que no esperamos."
    )

    parrafo(
        "Como futuro profesional de TI, este capítulo me deja una lección clara: antes de sentarme "
        "a programar, necesito entender el verdadero alcance de lo que estoy construyendo. ¿Es solo "
        "un programa para mí, o es un producto que otros van a usar? ¿Es un componente aislado o "
        "parte de un sistema? Esa reflexión inicial puede marcar la diferencia entre un proyecto "
        "exitoso y uno que se queda atrapado en el pozo de alquitrán."
    )

    # --- REFERENCIA ---
    doc.add_paragraph()
    h = doc.add_heading("Referencia", level=2)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)

    p = doc.add_paragraph()
    run = p.add_run("Brooks, F. P. (1995). ")
    run.font.size = Pt(11)
    run = p.add_run("The Mythical Man-Month: Essays on Software Engineering, Anniversary Edition. ")
    run.font.size = Pt(11)
    run.italic = True
    run = p.add_run("Addison-Wesley. Capítulo 1: The Tar Pit (pp. 3-12).")
    run.font.size = Pt(11)

    # Guardar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT_DOCX))
    print(f"Documento generado: {OUTPUT_DOCX}")

    # Limpiar portada temporal
    temp = BASE_DIR / "assets" / "portada_ensayo_temp.png"
    if temp.exists():
        temp.unlink()


if __name__ == "__main__":
    main()
