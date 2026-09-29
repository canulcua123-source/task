#!/usr/bin/env python3
"""Genera el ensayo sobre el Capítulo 1 de The Mythical Man-Month directamente en PDF."""

from fpdf import FPDF
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT = BASE_DIR / "entregas" / "formulacion de proyecto" / "formulacion_1_Ensayo_Mythical_Man_Month.pdf"


class EnsayoPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font("Arial", "", "/System/Library/Fonts/Supplemental/Arial.ttf")
        self.add_font("Arial", "B", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        self.add_font("Arial", "I", "/System/Library/Fonts/Supplemental/Arial Italic.ttf")
        self.add_font("Arial", "BI", "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf")
        self._is_cover = True

    def header(self):
        if not self._is_cover and self.page_no() > 1:
            self.set_draw_color(0, 51, 102)
            self.set_line_width(0.4)
            self.line(10, 10, 200, 10)
            self.set_y(12)
            self.set_font("Arial", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, "Ensayo: El pozo de alquitran - The Mythical Man-Month", align="C")
            self.ln(8)

    def footer(self):
        if not self._is_cover:
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Página {self.page_no() - 1}", align="C")


def draw_cover(pdf):
    pdf.add_page()
    pw = pdf.w
    ph = pdf.h

    colors = [(0, 51, 102), (0, 76, 140), (51, 122, 183), (100, 160, 210), (173, 200, 230)]
    bar_w = 6
    x = 8
    for c in colors:
        pdf.set_fill_color(*c)
        pdf.rect(x, 0, bar_w, ph, "F")
        x += bar_w + 1.5

    cx = 50
    cw = pw - cx - 15

    pdf.set_xy(cx, 35)
    pdf.set_font("Arial", "B", 36)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(cw, 15, "UTM", align="C")

    pdf.set_xy(cx, 55)
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(cw, 10, "UNIVERSIDAD TECNOLÓGICA\nMETROPOLITANA", align="C")

    pdf.set_xy(cx, 85)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(cw, 7, "TECNOLOGÍAS DE LA INFORMACIÓN\nINNOVACIÓN DIGITAL", align="C")

    pdf.set_xy(cx, 115)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(cw, 7, "Actividad:", align="C")
    pdf.set_xy(cx, 124)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(cw, 7, "Ensayo sobre el Capítulo 1 de\nThe Mythical Man-Month", align="C")

    pdf.set_xy(cx, 150)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(cw, 7, "Materia:", align="C")
    pdf.set_xy(cx, 159)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(cw, 7, "Formulación de Proyectos de TI", align="C")

    pdf.set_xy(cx, 178)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(cw, 7, "Maestro:", align="C")
    pdf.set_xy(cx, 187)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(cw, 7, "Omar", align="C")

    pdf.set_xy(cx, 206)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(cw, 7, "Alumno:", align="C")
    pdf.set_xy(cx, 215)
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(cw, 7, "Jesús Guadalupe Canul", align="C")

    pdf.set_xy(cx, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(cw, 7, "Grado: 7° Cuatrimestre\nGrupo: A", align="C")


def titulo(pdf, texto):
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, texto)
    pdf.ln(10)
    pdf.set_draw_color(0, 51, 102)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)


def subtitulo(pdf, texto):
    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, texto)
    pdf.ln(10)


def parrafo(pdf, texto):
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 7, texto, align="J")
    pdf.ln(3)


def bullet(pdf, texto):
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(30, 30, 30)
    x = pdf.get_x()
    pdf.cell(8, 7, "•")
    pdf.multi_cell(0, 7, texto, align="J")
    pdf.ln(2)


def main():
    pdf = EnsayoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    # Portada
    draw_cover(pdf)
    pdf._is_cover = False

    # Contenido
    pdf.add_page()
    titulo(pdf, "Ensayo: El pozo de alquitrán")

    pdf.set_font("Arial", "I", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, 'Capitulo 1 de "The Mythical Man-Month" - Frederick P. Brooks Jr.')
    pdf.ln(12)

    # INTRODUCCIÓN
    subtitulo(pdf, "Introducción")

    parrafo(pdf,
        "Cuando uno empieza a programar, todo parece sencillo: abres un editor, escribes unas "
        "líneas de código, lo corres y funciona. Esa sensación de crear algo de la nada es lo que "
        "engancha a la mayoría de los que estudiamos desarrollo de software. Pero conforme los "
        "proyectos crecen, esa simplicidad se convierte en algo muy diferente. Frederick Brooks, "
        "en el primer capítulo de su libro \"The Mythical Man-Month\", lo compara con un pozo de "
        "alquitrán: un lugar donde entre más luchas por avanzar, más te hundes. Este capítulo me "
        "hizo reflexionar sobre lo que realmente implica desarrollar software a gran escala y por "
        "qué tantos proyectos terminan fallando a pesar de tener programadores talentosos."
    )

    # DESARROLLO
    subtitulo(pdf, "El programa vs. el producto: no es lo mismo")

    parrafo(pdf,
        "Una de las ideas que más me llamó la atención del capítulo es la distinción que hace "
        "Brooks entre un programa y un producto de programación. Un programa es algo que tú haces "
        "para ti mismo: funciona en tu máquina, tú sabes cómo usarlo y si se rompe, tú lo arreglas. "
        "Pero un producto de programación es otra cosa completamente diferente. Necesita documentación, "
        "pruebas, manejo de errores, interfaces claras, y tiene que funcionar en ambientes que tú no "
        "controlas. Brooks dice que pasar de un programa a un producto cuesta al menos tres veces más "
        "esfuerzo. Y si además tiene que funcionar como parte de un sistema más grande, el costo se "
        "multiplica por nueve."
    )

    parrafo(pdf,
        "Esto lo he vivido en mis propios proyectos de la carrera. A veces hago un script en Python "
        "que me funciona perfecto en mi laptop, pero cuando lo tengo que entregar como un proyecto "
        "formal, con base de datos, con interfaz, con validaciones, el trabajo se multiplica "
        "enormemente. Y ni hablar cuando hay que trabajar en equipo: el código que escribo tiene que "
        "ser entendible para los demás, tiene que integrarse con lo que ellos hicieron, y todo tiene "
        "que probarse en conjunto. Es exactamente lo que Brooks describe: el pozo de alquitrán donde "
        "cada paso cuesta más de lo que esperabas."
    )

    subtitulo(pdf, "Las alegrías de programar")

    parrafo(pdf,
        "Algo que me gustó mucho del capítulo es que Brooks no solo habla de lo difícil que es "
        "el desarrollo de software, sino que también reconoce por qué nos gusta. Identifica cinco "
        "alegrías de programar que yo comparto completamente:"
    )

    bullet(pdf,
        "La alegría de crear cosas. Hay algo profundamente satisfactorio en construir algo que "
        "antes no existía. Es como ser un artesano digital: diseñas, construyes y al final tienes "
        "algo funcional que puedes ver y usar."
    )
    bullet(pdf,
        "El placer de hacer cosas útiles para otros. Cuando alguien usa tu software y le resuelve "
        "un problema real, esa sensación no tiene precio. No es solo código, es una herramienta "
        "que le facilita la vida a alguien."
    )
    bullet(pdf,
        "La fascinación de armar rompecabezas complejos. Programar es resolver problemas "
        "constantemente. Cada bug es un misterio, cada algoritmo es un acertijo. Para los que "
        "nos gusta pensar, eso es adictivo."
    )
    bullet(pdf,
        "El aprendizaje continuo. En esta carrera nunca dejas de aprender. Cada proyecto te "
        "obliga a investigar algo nuevo, a usar una tecnología diferente, a pensar de otra manera."
    )
    bullet(pdf,
        "Trabajar con un medio maleable. A diferencia de un ingeniero civil que trabaja con "
        "concreto, nosotros trabajamos con algo que podemos cambiar fácilmente. Si algo no "
        "funciona, lo reescribes. El software es flexible, y eso nos da mucha libertad creativa."
    )

    subtitulo(pdf, "Los sufrimientos del oficio")

    parrafo(pdf,
        "Pero así como hay alegrías, Brooks también describe los sufrimientos que vienen con el "
        "trabajo. Y creo que cualquier persona que ha programado en equipo o en un proyecto grande "
        "puede identificarse con esto."
    )

    parrafo(pdf,
        "Primero, la exigencia de perfección. La computadora no perdona: si falta un punto y coma, "
        "una variable mal nombrada o un caso borde que no contemplaste, todo se cae. Ninguna otra "
        "disciplina exige tanta precisión en cada detalle. En un ensayo puedes tener un error "
        "ortográfico y se entiende igual; en código, un carácter mal puesto puede hacer que toda "
        "la aplicación falle."
    )

    parrafo(pdf,
        "Segundo, la dependencia de otros. En proyectos reales, rara vez decides tú solo qué hacer "
        "y cómo hacerlo. Los objetivos los pone el cliente, los plazos los pone el jefe, y las "
        "restricciones las pone la tecnología disponible. Brooks señala que esto puede ser "
        "frustrante para alguien que está acostumbrado a la libertad creativa de programar solo."
    )

    parrafo(pdf,
        "Tercero, el miedo a la obsolescencia. En nuestra carrera todo cambia muy rápido. El "
        "framework que aprendiste hace dos años ya tiene una versión completamente nueva, el "
        "lenguaje que dominabas ya tiene un competidor que todos prefieren. Hay que estar "
        "constantemente actualizándose, y eso puede ser agotador."
    )

    subtitulo(pdf, "Relación con los proyectos de software actuales")

    parrafo(pdf,
        "Lo más impresionante de este capítulo es que fue escrito en 1975, pero sus ideas siguen "
        "siendo completamente vigentes. En la industria del software actual seguimos cayendo en "
        "el mismo pozo de alquitrán. Proyectos que se estiman en tres meses terminan tardando un "
        "año. Equipos de desarrollo que crecen pero en vez de avanzar más rápido se hacen más "
        "lentos por la complejidad de la comunicación. Software que funciona en desarrollo pero "
        "falla en producción porque nadie probó todos los casos."
    )

    parrafo(pdf,
        "En mi experiencia como estudiante de TI, he visto cómo proyectos en equipo sufren "
        "exactamente de estos problemas. Cuando trabajamos en el taller mecánico que desarrollamos "
        "para la materia de bases de datos, lo que empezó como \"un CRUD sencillo\" terminó siendo "
        "un sistema con múltiples tablas relacionadas, validaciones, vistas y consultas complejas. "
        "El esfuerzo real fue mucho mayor que el estimado, porque no solo era escribir código: era "
        "diseñar una base de datos coherente, documentar, probar y asegurar que todo funcionara "
        "junto. Exactamente el multiplicador ×9 que Brooks describe."
    )

    parrafo(pdf,
        "Las metodologias agiles que usamos hoy, como Scrum, son en parte una respuesta a los "
        "problemas que Brooks identifico hace casi 50 anios. Los sprints cortos, las entregas "
        "incrementales y la comunicacion constante con el cliente son formas de evitar hundirse "
        "en el pozo de alquitran. Pero aun asi, la esencia del problema sigue ahi: el software "
        "es inherentemente complejo, y esa complejidad no se puede eliminar, solo se puede gestionar."
    )

    parrafo(pdf,
        "Otro aspecto que conecta directamente con la realidad actual es la estimacion de tiempos. "
        "Brooks dedica gran parte de su libro a explicar por que los proyectos de software siempre "
        "tardan mas de lo planeado, y el capitulo 1 ya siembra esa semilla. Cuando un programador "
        "dice \"esto lo hago en una semana\", esta pensando en el programa, no en el producto. No "
        "esta contemplando las pruebas, la documentacion, la integracion, los casos borde, las "
        "revisiones de codigo ni los cambios de requerimientos que inevitablemente van a llegar. "
        "En la industria actual, herramientas como Jira o Azure DevOps intentan hacer mas visible "
        "este problema, pero la tendencia humana a subestimar la complejidad sigue siendo la misma "
        "que Brooks describio."
    )

    subtitulo(pdf, "La complejidad como enemigo invisible")

    parrafo(pdf,
        "Brooks introduce una idea que hoy sigue siendo fundamental en la ingenieria de software: "
        "la complejidad no es accidental, es esencial. Un sistema de software es complejo porque el "
        "problema que resuelve es complejo. No puedes simplificar el software sin simplificar el "
        "problema, y muchas veces el problema no se puede simplificar porque asi es la realidad."
    )

    parrafo(pdf,
        "En mi experiencia personal, esto lo veo claramente en los proyectos que hemos desarrollado "
        "durante la carrera. Por ejemplo, cuando nos pidieron hacer un sistema para un taller "
        "mecanico, parecia sencillo: registrar clientes, vehiculos y ordenes de servicio. Pero "
        "conforme fuimos entendiendo el problema real, aparecieron las complejidades: un vehiculo "
        "puede tener multiples ordenes, una orden puede tener multiples mecanicos, las refacciones "
        "tienen inventario que se debe actualizar, los precios pueden cambiar entre el catalogo y "
        "lo que realmente se cobra. Cada una de estas reglas de negocio agrega complejidad que no "
        "puedes evitar, porque es parte del problema real."
    )

    parrafo(pdf,
        "Esta complejidad esencial es lo que hace que el desarrollo de software sea fundamentalmente "
        "diferente a otras disciplinas de ingenieria. Un puente, una vez disenado y construido, no "
        "cambia. Pero un sistema de software vive y evoluciona: los usuarios piden nuevas funciones, "
        "las leyes cambian, la tecnologia avanza, los competidores lanzan productos mejores. El "
        "software que no evoluciona muere, pero cada cambio trae consigo el riesgo de romper algo "
        "que ya funcionaba. Es un ciclo que Brooks ya anticipaba en 1975 y que hoy vivimos a diario."
    )

    subtitulo(pdf, "Lecciones para la formulacion de proyectos")

    parrafo(pdf,
        "Desde la perspectiva de la formulacion de proyectos de TI, el capitulo 1 de Brooks nos "
        "deja varias lecciones practicas que deberiamos aplicar en cada proyecto que emprendamos:"
    )

    bullet(pdf,
        "Definir claramente si estamos construyendo un programa, un producto o un sistema. Esta "
        "distincion afecta directamente el tiempo, el costo y los recursos necesarios. Un error "
        "en esta clasificacion inicial puede hacer que todo el proyecto fracase."
    )
    bullet(pdf,
        "Incluir en la planificacion el esfuerzo de documentacion, pruebas e integracion. Estos "
        "no son extras opcionales, son parte fundamental del producto. Si no los contemplamos "
        "desde el inicio, el proyecto va a exceder su presupuesto y su plazo."
    )
    bullet(pdf,
        "Reconocer que la complejidad es inherente al problema. Intentar simplificar demasiado "
        "un sistema puede llevar a un producto que no resuelve el problema real del usuario. Es "
        "mejor gestionar la complejidad que negarla."
    )
    bullet(pdf,
        "Mantener equipos motivados reconociendo tanto las alegrias como los sufrimientos del "
        "trabajo. Un buen lider de proyecto entiende que los programadores necesitan retos "
        "intelectuales y autonomia creativa, pero tambien necesitan claridad en los objetivos "
        "y herramientas adecuadas para hacer su trabajo."
    )

    parrafo(pdf,
        "En el contexto mexicano, donde muchas empresas de desarrollo de software son pequenias "
        "o medianas, estas lecciones son especialmente relevantes. Con recursos limitados, es "
        "tentador tomar atajos: no documentar, no probar, no planificar. Pero como Brooks nos "
        "ensenia, esos atajos son los que nos hunden en el pozo de alquitran. La diferencia entre "
        "un proyecto exitoso y uno que fracasa no esta en la cantidad de codigo que se escribe, "
        "sino en la calidad de la planificacion y la gestion que hay detras."
    )

    # CONCLUSION
    subtitulo(pdf, "Conclusion")

    parrafo(pdf,
        "El capitulo 1 de \"The Mythical Man-Month\" es una lectura que deberia ser obligatoria "
        "para cualquier estudiante de desarrollo de software. No porque diga algo que no sepamos "
        "intuitivamente, sino porque le pone nombre y estructura a lo que todos hemos sentido: "
        "que programar es maravilloso y tortuoso al mismo tiempo, que un proyecto de software es "
        "mucho mas que escribir codigo, y que la complejidad se multiplica de formas que no esperamos."
    )

    parrafo(pdf,
        "Como futuro profesional de TI, este capitulo me deja una leccion clara: antes de sentarme "
        "a programar, necesito entender el verdadero alcance de lo que estoy construyendo. Es solo "
        "un programa para mi, o es un producto que otros van a usar? Es un componente aislado o "
        "parte de un sistema? Esa reflexion inicial puede marcar la diferencia entre un proyecto "
        "exitoso y uno que se queda atrapado en el pozo de alquitran."
    )

    parrafo(pdf,
        "Finalmente, Brooks nos recuerda que a pesar de todas las dificultades, vale la pena. Las "
        "alegrias de crear, de resolver problemas, de aprender constantemente y de hacer cosas "
        "utiles para los demas superan los sufrimientos del oficio. Y quizas eso es lo mas importante "
        "que podemos llevarnos de este capitulo: la programacion es dificil, pero es dificil de la "
        "manera correcta. Es el tipo de dificultad que nos hace crecer como profesionales y como "
        "personas. Y si entendemos eso desde el inicio, estamos mejor preparados para enfrentar "
        "cualquier proyecto que se nos presente en nuestra carrera."
    )

    # REFERENCIA
    subtitulo(pdf, "Referencia")

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6,
        "Brooks, F. P. (1995). The Mythical Man-Month: Essays on Software Engineering, "
        "Anniversary Edition. Addison-Wesley. Capitulo 1: The Tar Pit (pp. 3-12)."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    main()
