#!/usr/bin/env python3
"""Genera el Reporte de Vulnerabilidades del reglamento en PDF con portada UTM."""

from fpdf import FPDF
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT = BASE_DIR / "entregas" / "etica y legislacion" / "etica_3_Reporte_de_vulnerabilidades.pdf"


class ReportePDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Registrar Arial con soporte Unicode
        self.add_font("ArialUni", "", "/System/Library/Fonts/Supplemental/Arial.ttf", uni=True)
        self.add_font("ArialUni", "B", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", uni=True)
        self.add_font("ArialUni", "I", "/System/Library/Fonts/Supplemental/Arial Italic.ttf", uni=True)
        self.add_font("ArialUni", "BI", "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf", uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("ArialUni", "I", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "Reporte de Vulnerabilidades — Reglamento para una Empresa de Desarrollo de Software", align="C")
            self.ln(4)
            self.set_draw_color(0, 51, 102)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("ArialUni", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Página {self.page_no() - 1}", align="C")


def draw_cover(pdf):
    """Portada estilo UTM con barras azules."""
    pdf.add_page()
    pw = pdf.w
    ph = pdf.h

    # Barras azules laterales
    colors = [(0, 51, 102), (0, 76, 140), (51, 122, 183), (100, 160, 210), (173, 200, 230)]
    bar_w = 6
    x = 8
    for c in colors:
        pdf.set_fill_color(*c)
        pdf.rect(x, 0, bar_w, ph, "F")
        x += bar_w + 1.5

    # Contenido centrado
    cx = 50
    content_w = pw - cx - 15

    # UTM
    pdf.set_xy(cx, 35)
    pdf.set_font("ArialUni", "B", 36)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(content_w, 15, "UTM", align="C")

    # Universidad
    pdf.set_xy(cx, 55)
    pdf.set_font("ArialUni", "B", 20)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(content_w, 10, "UNIVERSIDAD TECNOLÓGICA\nMETROPOLITANA", align="C")

    # Carrera
    pdf.set_xy(cx, 85)
    pdf.set_font("ArialUni", "B", 13)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(content_w, 7, "TECNOLOGÍAS DE LA INFORMACIÓN\nINNOVACIÓN DIGITAL", align="C")

    # Actividad
    pdf.set_xy(cx, 115)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(content_w, 7, "Actividad:", align="C")
    pdf.set_xy(cx, 124)
    pdf.set_font("ArialUni", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(content_w, 7, "Reporte de Vulnerabilidades del Reglamento\npara una Empresa de Desarrollo de Software", align="C")

    # Materia
    pdf.set_xy(cx, 150)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(content_w, 7, "Materia:", align="C")
    pdf.set_xy(cx, 159)
    pdf.set_font("ArialUni", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(content_w, 7, "Ética y Legislación en Tecnologías de la Información", align="C")

    # Maestro
    pdf.set_xy(cx, 178)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(content_w, 7, "Maestro:", align="C")
    pdf.set_xy(cx, 187)
    pdf.set_font("ArialUni", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(content_w, 7, "Mirian Magaly Canche Caamal", align="C")

    # Integrantes
    pdf.set_xy(cx, 206)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(content_w, 7, "Integrantes:", align="C")
    pdf.set_xy(cx, 215)
    pdf.set_font("ArialUni", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(content_w, 6, "Jesús Guadalupe Canul\nCocom Pech Brian Alberto\nTun Cauich Brandon Andrei", align="C")

    # Grado y grupo
    pdf.set_xy(cx, 245)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.multi_cell(content_w, 7, "Grado: 7° Cuatrimestre\nGrupo: A", align="C")


def section_title(pdf, text):
    pdf.set_font("ArialUni", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, text)
    pdf.ln(10)
    pdf.set_draw_color(0, 51, 102)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def vuln_block(pdf, num, data):
    """Dibuja un bloque de vulnerabilidad con formato de tabla."""
    pdf.set_font("ArialUni", "B", 13)
    pdf.set_text_color(255, 255, 255)

    # Header del bloque
    grav = data["gravedad"]
    if grav == "Alta":
        pdf.set_fill_color(180, 30, 30)
    elif grav == "Media":
        pdf.set_fill_color(200, 140, 0)
    else:
        pdf.set_fill_color(60, 140, 60)

    pdf.cell(0, 9, f"  Vulnerabilidad #{num}: {data['titulo']}", fill=True)
    pdf.ln(11)

    rows = [
        ("1. Situación", data["situacion"]),
        ("2. Artículo relacionado", data["articulo"]),
        ("3. Vulnerabilidad", data["vulnerabilidad"]),
        ("4. Riesgo", data["riesgo"]),
        ("5. Categoría", data["categoria"]),
        ("6. Gravedad", data["gravedad"]),
        ("7. Propuesta de parche", data["parche"]),
    ]

    margin_l = pdf.l_margin  # 10
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin  # 190
    label_w = 48
    val_w = usable_w - label_w  # 142

    for label, value in rows:
        y_start = pdf.get_y()

        # Calcular alto del valor
        pdf.set_font("ArialUni", "", 10)
        lines = pdf.multi_cell(val_w - 2, 5.5, value, dry_run=True, output="LINES")
        val_h = max(len(lines) * 5.5, 7)
        row_h = val_h

        # Check page break
        if y_start + row_h > 270:
            pdf.add_page()
            y_start = pdf.get_y()

        # Label cell
        pdf.set_xy(margin_l, y_start)
        pdf.set_font("ArialUni", "B", 10)
        pdf.set_text_color(0, 51, 102)
        pdf.set_fill_color(230, 240, 250)
        pdf.set_draw_color(180, 200, 220)
        pdf.cell(label_w, row_h, f" {label}", border=1, fill=True)

        # Value cell
        pdf.set_xy(margin_l + label_w, y_start)
        pdf.set_font("ArialUni", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_fill_color(255, 255, 255)
        pdf.multi_cell(val_w, 5.5, value, border=1)

        new_y = max(pdf.get_y(), y_start + row_h)
        pdf.set_y(new_y)

    pdf.ln(8)


def main():
    vulnerabilidades = [
        {
            "titulo": "NDA sin alcance ni duración definidos",
            "situacion": "El Artículo 1 del reglamento unificado obliga a todo empleado a firmar un contrato de confidencialidad (NDA) al momento de su contratación, pero no especifica el alcance de la información protegida, la duración de la obligación después de terminada la relación laboral, ni las consecuencias específicas por incumplimiento.",
            "articulo": "Artículo 1 — Sección I (Empleados)",
            "vulnerabilidad": "Un ex-empleado podría argumentar que su obligación de confidencialidad terminó junto con su contrato laboral, y divulgar información sensible de proyectos, clientes o arquitectura de software sin consecuencias legales claras.",
            "riesgo": "Fuga de información confidencial, código fuente, datos de clientes o estrategias de negocio por parte de ex-empleados sin que la empresa tenga respaldo legal claro para actuar.",
            "categoria": "Legal",
            "gravedad": "Alta",
            "parche": "Especificar en el Artículo 1: (a) el alcance del NDA (código fuente, datos de clientes, procesos internos, arquitectura técnica), (b) la duración post-empleo (mínimo 2 años después de la separación), (c) las sanciones por incumplimiento (indemnización, acciones legales conforme a la LFPDPPP y Código Penal Federal), y (d) que el NDA debe ser un documento separado firmado por ambas partes con testigos.",
        },
        {
            "titulo": "Propiedad intelectual sin distinción de proyectos personales",
            "situacion": "El Artículo 8 declara que 'todo desarrollo realizado durante la relación laboral es propiedad intelectual de la empresa', sin distinguir entre trabajo realizado en horario laboral con recursos de la empresa y proyectos personales del empleado en su tiempo libre.",
            "articulo": "Artículo 8 — Sección I (Empleados)",
            "vulnerabilidad": "La redacción actual es demasiado amplia y podría interpretarse como que la empresa reclama propiedad sobre cualquier código o proyecto que el empleado desarrolle mientras esté contratado, incluso si fue creado en tiempo personal, con recursos propios y sin relación con las actividades de la empresa.",
            "riesgo": "Conflictos legales con empleados que contribuyen a proyectos open source o tienen emprendimientos paralelos. Posible violación del derecho moral de autor del empleado (Ley Federal del Derecho de Autor, Art. 18-23). Desmotivación de desarrolladores talentosos que temen perder sus proyectos personales.",
            "categoria": "Propiedad intelectual",
            "gravedad": "Alta",
            "parche": "Reformular el Artículo 8 para especificar: 'Todo desarrollo realizado durante el horario laboral, con recursos de la empresa o relacionado con los proyectos asignados, es propiedad intelectual de la empresa. Los proyectos personales realizados fuera del horario laboral y sin uso de recursos corporativos no están sujetos a esta cláusula, siempre que no compitan directamente con los productos de la empresa ni utilicen información confidencial.'",
        },
        {
            "titulo": "Protección de datos sin protocolo de brechas de seguridad",
            "situacion": "El Artículo 14 establece que los datos personales serán tratados conforme a la Ley Federal de Protección de Datos Personales (LFPDPPP) y que los usuarios pueden solicitar la eliminación de sus datos. Sin embargo, no se define qué sucede en caso de una brecha de seguridad, ni quién es responsable de notificar a los afectados.",
            "articulo": "Artículo 14 — Sección II (Usuarios)",
            "vulnerabilidad": "En caso de una filtración de datos personales de usuarios (hackeo, acceso no autorizado, error humano), el reglamento no establece un protocolo de respuesta: no define tiempos de notificación, responsable designado (DPO), canales de comunicación con afectados ni medidas de contención.",
            "riesgo": "Incumplimiento del artículo 20 de la LFPDPPP que exige notificar brechas de seguridad. Multas del INAI de hasta 320,000 UMA (aprox. $34 millones MXN). Pérdida de confianza de clientes y daño reputacional.",
            "categoria": "Privacidad",
            "gravedad": "Alta",
            "parche": "Agregar un Artículo 14-bis: 'En caso de brecha de seguridad que comprometa datos personales, la empresa deberá: (a) designar un Oficial de Protección de Datos responsable, (b) contener la brecha en un máximo de 24 horas, (c) notificar a los usuarios afectados y al INAI dentro de las 72 horas siguientes, (d) documentar el incidente y las medidas correctivas aplicadas, conforme a los artículos 19 y 20 de la LFPDPPP.'",
        },
        {
            "titulo": "Sanciones laborales sin debido proceso",
            "situacion": "El Artículo 10 establece descuento salarial proporcional por faltas injustificadas y rescisión de contrato tras tres faltas consecutivas. El incumplimiento reiterado de normas se sanciona 'de forma progresiva', pero no se define un procedimiento de debido proceso ni un mecanismo de apelación.",
            "articulo": "Artículo 10 — Sección I (Empleados)",
            "vulnerabilidad": "Un empleado sancionado no tiene mecanismo formal para presentar su defensa, aportar pruebas justificativas (emergencia médica, fuerza mayor) o apelar la decisión. Esto viola el principio de audiencia establecido en la Ley Federal del Trabajo (Art. 47).",
            "riesgo": "Demandas laborales ante la Junta de Conciliación y Arbitraje por despido injustificado. La empresa podría perder el caso y pagar indemnización completa (3 meses + 20 días por año) por no haber seguido un debido proceso documentado.",
            "categoria": "Laboral",
            "gravedad": "Alta",
            "parche": "Reformular el Artículo 10 para incluir: 'Antes de aplicar cualquier sanción, el empleado tendrá derecho a: (a) ser notificado por escrito de la falta imputada, (b) presentar su defensa y pruebas en un plazo de 5 días hábiles, (c) solicitar revisión ante el comité de recursos humanos. Se levantará acta administrativa firmada por ambas partes. Las faltas por causa de fuerza mayor debidamente comprobada no se contabilizarán como injustificadas.'",
        },
        {
            "titulo": "Software 'as-is' contradice soporte obligatorio de 48 horas",
            "situacion": "El Artículo 16 garantiza respuesta de soporte técnico en un plazo máximo de 48 horas hábiles, pero en el análisis comparativo del documento se señala la contradicción con la cláusula 'as-is' que establece que el software se entrega sin garantía de funcionamiento al 100%.",
            "articulo": "Artículos 16 y 17 — Sección II (Usuarios)",
            "vulnerabilidad": "La contradicción entre 'no garantizamos que funcione' y 'te respondemos en 48 horas' genera ambigüedad jurídica. Un usuario podría exigir soporte para funcionalidades que la empresa no garantiza, o la empresa podría negar soporte amparándose en la cláusula 'as-is' y dejar sin efecto el compromiso de 48 horas.",
            "riesgo": "Demandas por incumplimiento contractual. Pérdida de clientes por expectativas no cumplidas. El reglamento se vuelve inaplicable en disputas legales por la contradicción interna.",
            "categoria": "Legal",
            "gravedad": "Media",
            "parche": "Clarificar en el Artículo 16: 'La empresa garantiza respuesta de soporte técnico en 48 horas hábiles para incidentes reportados por los canales oficiales. El soporte cubre: errores reproducibles, fallos de seguridad y problemas de acceso. No cubre: funcionalidades no documentadas, personalizaciones fuera del alcance contratado ni incompatibilidades con software de terceros.' Eliminar la referencia genérica 'as-is' y sustituir por un listado claro de exclusiones.",
        },
        {
            "titulo": "Uso de IA no regulado en el desarrollo",
            "situacion": "El reglamento no contiene ninguna disposición sobre el uso de herramientas de inteligencia artificial (GitHub Copilot, ChatGPT, Claude, etc.) en el proceso de desarrollo de software, ni establece políticas sobre la revisión del código generado por IA.",
            "articulo": "No existe — Sección III (Desarrolladores)",
            "vulnerabilidad": "Los desarrolladores podrían usar herramientas de IA para generar código sin revisión adecuada, introduciendo vulnerabilidades de seguridad, código con licencias incompatibles (entrenado con código GPL), o enviando código propietario de la empresa a servidores externos (prompts con código fuente confidencial).",
            "riesgo": "Filtración de código fuente confidencial a través de prompts en herramientas de IA externas. Introducción de vulnerabilidades no detectadas en código generado automáticamente. Posibles violaciones de licencias de software. Problemas de propiedad intelectual sobre código generado por IA.",
            "categoria": "Uso de IA",
            "gravedad": "Media",
            "parche": "Agregar un nuevo Artículo 28: 'El uso de herramientas de inteligencia artificial para generación de código está permitido bajo las siguientes condiciones: (a) no se enviará código fuente propietario como prompt a herramientas de IA externas, (b) todo código generado por IA debe pasar por revisión de código (code review) obligatoria, (c) se verificará que el código generado no introduzca dependencias con licencias incompatibles, (d) se documentará el uso de IA en los commits correspondientes.'",
        },
        {
            "titulo": "Definición vaga de 'uso personal' de recursos",
            "situacion": "El Artículo 5 prohíbe el uso de recursos tecnológicos de la empresa para fines personales durante el horario laboral, pero no define qué constituye 'uso personal' ni establece excepciones razonables.",
            "articulo": "Artículo 5 — Sección I (Empleados)",
            "vulnerabilidad": "La prohibición absoluta de uso personal es ambigua y poco realista. ¿Revisar un correo personal durante el almuerzo es una violación? ¿Usar el navegador para una consulta médica? ¿Escuchar música mientras se programa? Sin definición clara, la regla es inaplicable o se aplica de forma arbitraria.",
            "riesgo": "Aplicación selectiva y arbitraria de la norma, generando un ambiente laboral hostil. Posibles demandas por discriminación si se sanciona a unos empleados y no a otros por la misma conducta. Desmotivación del equipo por reglas percibidas como excesivas.",
            "categoria": "Ético",
            "gravedad": "Baja",
            "parche": "Reformular el Artículo 5: 'Se permite el uso personal breve e incidental de los recursos tecnológicos (consultas personales, comunicación familiar urgente) siempre que no interfiera con las funciones laborales ni comprometa la seguridad de la información. Queda estrictamente prohibido: descargar software no autorizado, acceder a contenido inapropiado, usar los equipos para actividades comerciales ajenas a la empresa o almacenar archivos personales en servidores corporativos.'",
        },
    ]

    pdf = ReportePDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- Portada ---
    draw_cover(pdf)

    # --- Introducción ---
    pdf.add_page()
    section_title(pdf, "Introducción")
    pdf.set_font("ArialUni", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6,
        "El presente documento contiene el reporte de vulnerabilidades detectadas en el "
        "Reglamento Unificado para una Empresa de Desarrollo de Software, elaborado por el equipo "
        "conformado por Jesús Guadalupe Canul, Brando Cocom Pech Bryan Alberto y Brandon Andrey Tun Cauich.\n\n"
        "El análisis se realizó siguiendo la estructura establecida en clase para el reporte de vulnerabilidades, "
        "evaluando cada artículo del reglamento unificado en busca de vacíos legales, ambigüedades, "
        "contradicciones y omisiones que pudieran representar un riesgo ético, legal o de seguridad "
        "para la empresa, sus empleados o sus usuarios.\n\n"
        "Se identificaron un total de 7 vulnerabilidades, clasificadas por categoría y gravedad, "
        "cada una con su respectiva propuesta de parche para fortalecer el reglamento."
    )
    pdf.ln(6)

    # Resumen de gravedad
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "Resumen de hallazgos:")
    pdf.ln(10)

    counts = {"Alta": 0, "Media": 0, "Baja": 0}
    for v in vulnerabilidades:
        counts[v["gravedad"]] += 1

    for grav, count in counts.items():
        if grav == "Alta":
            pdf.set_fill_color(180, 30, 30)
        elif grav == "Media":
            pdf.set_fill_color(200, 140, 0)
        else:
            pdf.set_fill_color(60, 140, 60)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("ArialUni", "B", 11)
        pdf.cell(50, 8, f"  {grav}: {count}", fill=True)
        pdf.ln(10)

    pdf.ln(4)

    # --- Vulnerabilidades ---
    pdf.add_page()
    section_title(pdf, "Vulnerabilidades Detectadas")

    for i, v in enumerate(vulnerabilidades, 1):
        vuln_block(pdf, i, v)

    # --- Conclusión ---
    pdf.add_page()
    section_title(pdf, "Conclusión")
    pdf.set_font("ArialUni", "", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, 6,
        "El reglamento unificado presenta una base sólida que cubre las tres secciones fundamentales "
        "(empleados, usuarios y desarrolladores) e incorpora principios éticos relevantes como la "
        "privacidad, seguridad, responsabilidad, propiedad intelectual y acceso equitativo.\n\n"
        "Sin embargo, las 7 vulnerabilidades identificadas revelan áreas de mejora importantes, "
        "principalmente en:\n\n"
        "• Precisión legal: varios artículos usan términos ambiguos que dificultan su aplicación "
        "y podrían ser impugnados en instancias legales (NDA sin alcance, sanciones sin debido proceso).\n\n"
        "• Actualización tecnológica: el reglamento no contempla el uso de inteligencia artificial, "
        "una herramienta cada vez más presente en el desarrollo de software.\n\n"
        "• Coherencia interna: existen contradicciones entre artículos (soporte garantizado vs. "
        "software sin garantía) que debilitan la credibilidad del documento.\n\n"
        "• Protección de datos: aunque se menciona la LFPDPPP, no se define un protocolo de "
        "respuesta ante brechas de seguridad, dejando a la empresa expuesta a sanciones del INAI.\n\n"
        "Se recomienda aplicar los 7 parches propuestos para fortalecer el reglamento y asegurar "
        "su viabilidad legal, ética y operativa."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    main()
