#!/usr/bin/env python3
"""Agrega el reporte de vulnerabilidades y los 3 parches al docx del reglamento existente."""

from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = Path(__file__).parent
DOCX_PATH = BASE_DIR / "entregas" / "etica_2_Reglamento_para_una_empresa_de.docx"
OUTPUT_PATH = BASE_DIR / "entregas" / "etica_2_Reglamento_para_una_empresa_de.docx"


def add_page_break(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    run.add_break(docx.enum.text.WD_BREAK.PAGE)


def set_cell_shading(cell, color):
    """Aplica color de fondo a una celda."""
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor(0, 51, 102)
    return h


def add_vuln_table(doc, num, data):
    """Agrega una tabla de vulnerabilidad al documento."""
    # Título de vulnerabilidad
    p = doc.add_paragraph()
    run = p.add_run(f"Vulnerabilidad #{num}: {data['titulo']}")
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(255, 255, 255)
    # Shading del párrafo
    grav = data["gravedad"]
    if grav == "Alta":
        bg = "B41E1E"
    elif grav == "Media":
        bg = "C88C00"
    else:
        bg = "3C8C3C"
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), bg)
    shading.set(qn("w:val"), "clear")
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pPr.append(shading)

    rows_data = [
        ("1. Situación", data["situacion"]),
        ("2. Artículo relacionado", data["articulo"]),
        ("3. Vulnerabilidad", data["vulnerabilidad"]),
        ("4. Riesgo", data["riesgo"]),
        ("5. Categoría", data["categoria"]),
        ("6. Gravedad", data["gravedad"]),
        ("7. Propuesta de parche", data["parche"]),
    ]

    table = doc.add_table(rows=len(rows_data), cols=2)
    table.style = "Table Grid"
    table.autofit = True

    for i, (label, value) in enumerate(rows_data):
        cell_label = table.cell(i, 0)
        cell_value = table.cell(i, 1)

        cell_label.text = ""
        p_label = cell_label.paragraphs[0]
        run_label = p_label.add_run(label)
        run_label.bold = True
        run_label.font.size = Pt(10)
        run_label.font.color.rgb = RGBColor(0, 51, 102)
        set_cell_shading(cell_label, "E6F0FA")

        cell_value.text = ""
        p_value = cell_value.paragraphs[0]
        run_value = p_value.add_run(value)
        run_value.font.size = Pt(10)

    # Set column widths
    for row in table.rows:
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.7)

    doc.add_paragraph()  # Espacio


def main():
    import docx.enum.text

    doc = Document(str(DOCX_PATH))

    # --- Salto de página antes del reporte ---
    doc.add_page_break()

    # =========================================
    # SECCIÓN 2: REPORTE DE VULNERABILIDADES
    # =========================================
    add_heading_styled(doc, "Reporte de Vulnerabilidades Detectadas", level=1)

    p = doc.add_paragraph()
    run = p.add_run(
        "A continuación se presenta el reporte de vulnerabilidades detectadas en el reglamento, "
        "siguiendo la estructura establecida en clase. Se identificaron 7 vulnerabilidades "
        "clasificadas por categoría y gravedad, cada una con su propuesta de parche."
    )
    run.font.size = Pt(11)

    # Resumen
    p = doc.add_paragraph()
    run = p.add_run("Resumen: ")
    run.bold = True
    run.font.size = Pt(11)
    run = p.add_run("4 gravedad Alta, 2 gravedad Media, 1 gravedad Baja.")
    run.font.size = Pt(11)

    doc.add_paragraph()

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
            "vulnerabilidad": "La prohibición absoluta de uso personal es ambigua y poco realista. ¿Revisar un correo personal durante el almuerzo es una violación? ¿Usar el navegador para una consulta médica? Sin definición clara, la regla es inaplicable o se aplica de forma arbitraria.",
            "riesgo": "Aplicación selectiva y arbitraria de la norma, generando un ambiente laboral hostil. Posibles demandas por discriminación si se sanciona a unos empleados y no a otros por la misma conducta. Desmotivación del equipo por reglas percibidas como excesivas.",
            "categoria": "Ético",
            "gravedad": "Baja",
            "parche": "Reformular el Artículo 5: 'Se permite el uso personal breve e incidental de los recursos tecnológicos (consultas personales, comunicación familiar urgente) siempre que no interfiera con las funciones laborales ni comprometa la seguridad de la información. Queda estrictamente prohibido: descargar software no autorizado, acceder a contenido inapropiado, usar los equipos para actividades comerciales ajenas a la empresa o almacenar archivos personales en servidores corporativos.'",
        },
    ]

    for i, v in enumerate(vulnerabilidades, 1):
        add_vuln_table(doc, i, v)

    # =========================================
    # SECCIÓN 3: TRES PARCHES AL REGLAMENTO
    # =========================================
    doc.add_page_break()
    add_heading_styled(doc, "Parches Aplicados al Reglamento", level=1)

    p = doc.add_paragraph()
    run = p.add_run(
        "Con base en las vulnerabilidades de mayor gravedad detectadas, se presentan "
        "los siguientes tres parches que mejoran, especifican y amplían las reglas del "
        "reglamento unificado."
    )
    run.font.size = Pt(11)

    # Parche 1
    add_heading_styled(doc, "Parche 1: Artículo 1 — NDA con alcance y duración definidos", level=2)
    p = doc.add_paragraph()
    run = p.add_run("Versión original: ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(180, 30, 30)
    p = doc.add_paragraph(
        "\"Todo empleado firmará un contrato de confidencialidad (NDA) al momento de su "
        "contratación y mantendrá la reserva de información interna, proyectos y datos de "
        "clientes durante y después de la relación laboral.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)
        run.italic = True

    p = doc.add_paragraph()
    run = p.add_run("Versión parcheada: ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 120, 0)
    p = doc.add_paragraph(
        "\"Artículo 1. Todo empleado firmará un contrato de confidencialidad (NDA) al momento "
        "de su contratación. Dicho contrato deberá especificar:\n"
        "a) Alcance: la obligación cubre código fuente, datos de clientes, procesos internos, "
        "arquitectura técnica, estrategias comerciales y cualquier información clasificada como confidencial.\n"
        "b) Duración: la obligación de confidencialidad permanecerá vigente durante la relación "
        "laboral y por un periodo mínimo de 2 (dos) años posteriores a la terminación del contrato.\n"
        "c) Sanciones: el incumplimiento dará lugar a indemnización por daños y perjuicios, así "
        "como acciones legales conforme a la LFPDPPP y el Código Penal Federal.\n"
        "d) El NDA será un documento independiente, firmado por ambas partes ante dos testigos, "
        "con copia para el empleado.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)

    p = doc.add_paragraph()
    run = p.add_run("Justificación: ")
    run.bold = True
    run.font.size = Pt(11)
    run = p.add_run(
        "La versión original no definía alcance, duración post-empleo ni consecuencias, "
        "lo que permitiría a un ex-empleado divulgar información sensible sin respaldo legal "
        "claro para la empresa. El parche cierra esta vulnerabilidad con especificaciones "
        "concretas alineadas a la legislación mexicana vigente."
    )
    run.font.size = Pt(11)

    # Parche 2
    add_heading_styled(doc, "Parche 2: Artículo 14-bis — Protocolo de brechas de seguridad (nuevo)", level=2)
    p = doc.add_paragraph()
    run = p.add_run("Artículo original (14): ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(180, 30, 30)
    p = doc.add_paragraph(
        "\"Los datos personales serán tratados conforme a la Ley Federal de Protección de Datos "
        "Personales. Los usuarios podrán solicitar la eliminación de sus datos en cualquier momento.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)
        run.italic = True

    p = doc.add_paragraph()
    run = p.add_run("Nuevo Artículo 14-bis (agregado): ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 120, 0)
    p = doc.add_paragraph(
        "\"Artículo 14-bis. Protocolo de respuesta ante brechas de seguridad de datos personales.\n"
        "En caso de que se detecte una brecha de seguridad que comprometa datos personales de usuarios, "
        "la empresa deberá:\n"
        "a) Designar un Oficial de Protección de Datos (DPO) como responsable de coordinar la respuesta.\n"
        "b) Contener la brecha y mitigar el daño en un plazo máximo de 24 horas desde su detección.\n"
        "c) Notificar a los usuarios afectados por correo electrónico y a través de los canales oficiales "
        "dentro de las 72 horas siguientes a la detección.\n"
        "d) Reportar el incidente al Instituto Nacional de Transparencia (INAI) conforme al artículo 20 "
        "de la LFPDPPP.\n"
        "e) Documentar el incidente en un registro interno que incluya: causa, datos comprometidos, "
        "usuarios afectados, acciones de contención y medidas preventivas implementadas.\n"
        "f) Realizar una auditoría de seguridad dentro de los 30 días posteriores al incidente.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)

    p = doc.add_paragraph()
    run = p.add_run("Justificación: ")
    run.bold = True
    run.font.size = Pt(11)
    run = p.add_run(
        "El reglamento original menciona la LFPDPPP pero no define qué hacer en caso de brecha "
        "de seguridad. Sin este protocolo, la empresa se expone a multas del INAI de hasta 320,000 UMA "
        "(aproximadamente $34 millones MXN) y a la pérdida de confianza de sus clientes. "
        "Este artículo nuevo cubre la obligación legal y establece un proceso claro de respuesta."
    )
    run.font.size = Pt(11)

    # Parche 3
    add_heading_styled(doc, "Parche 3: Artículo 10 — Sanciones con debido proceso", level=2)
    p = doc.add_paragraph()
    run = p.add_run("Versión original: ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(180, 30, 30)
    p = doc.add_paragraph(
        "\"Las faltas injustificadas se sancionarán con descuento salarial proporcional. "
        "Tres faltas consecutivas injustificadas serán motivo de rescisión de contrato. "
        "El incumplimiento reiterado de normas se sancionará de forma progresiva.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)
        run.italic = True

    p = doc.add_paragraph()
    run = p.add_run("Versión parcheada: ")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 120, 0)
    p = doc.add_paragraph(
        "\"Artículo 10. Régimen de sanciones y debido proceso.\n"
        "Las faltas injustificadas se sancionarán con descuento salarial proporcional. "
        "Tres faltas consecutivas injustificadas serán motivo de rescisión de contrato. "
        "El incumplimiento reiterado de normas se sancionará de forma progresiva.\n\n"
        "Antes de aplicar cualquier sanción, se garantiza el siguiente procedimiento:\n"
        "a) El empleado será notificado por escrito de la falta imputada, describiendo los hechos, "
        "la fecha y la norma presuntamente incumplida.\n"
        "b) El empleado dispondrá de 5 (cinco) días hábiles para presentar su defensa por escrito "
        "y aportar las pruebas que considere pertinentes.\n"
        "c) El empleado podrá solicitar revisión de su caso ante el comité de Recursos Humanos.\n"
        "d) Se levantará acta administrativa firmada por ambas partes y un testigo.\n"
        "e) Las faltas por causa de fuerza mayor debidamente comprobada (emergencia médica, "
        "desastre natural, fallecimiento de familiar directo) no se contabilizarán como injustificadas.\n\n"
        "Las sanciones progresivas serán: (1) amonestación verbal, (2) amonestación escrita, "
        "(3) suspensión temporal sin goce de sueldo de 1 a 3 días, (4) rescisión de contrato.\""
    )
    p.paragraph_format.left_indent = Inches(0.5)
    for run in p.runs:
        run.font.size = Pt(11)

    p = doc.add_paragraph()
    run = p.add_run("Justificación: ")
    run.bold = True
    run.font.size = Pt(11)
    run = p.add_run(
        "La versión original no contemplaba ningún mecanismo de defensa para el empleado, "
        "violando el principio de audiencia de la Ley Federal del Trabajo (Art. 47). Sin debido "
        "proceso, cualquier despido podría ser declarado injustificado por la Junta de Conciliación "
        "y Arbitraje, obligando a la empresa a pagar indemnización completa. El parche establece "
        "un proceso claro, documentado y justo que protege tanto al empleado como a la empresa."
    )
    run.font.size = Pt(11)

    # Guardar
    doc.save(str(OUTPUT_PATH))
    print(f"Documento actualizado: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
