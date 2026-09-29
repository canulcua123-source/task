-- ============================================================
-- CLAUDENT — Sistema de gestión odontológica en la nube
-- Script completo: DDL + Índices + DML + Consultas + DCL
-- Motor: PostgreSQL (Supabase)
-- Equipo 2 — BD en la Nube, Unidad 1
-- ============================================================

-- ************************************************************
-- SECCIÓN 1: DDL — CREACIÓN DE ESQUEMA Y TABLAS
-- ************************************************************
-- Documentación de Normalización:
--
-- 1FN (Primera Forma Normal):
--   - Todos los campos contienen valores atómicos (indivisibles).
--   - No hay grupos repetitivos ni arrays en ninguna columna.
--   - Ejemplo: nombre y apellido están separados en dentista/paciente
--     en vez de un solo campo "nombre_completo".
--
-- 2FN (Segunda Forma Normal):
--   - Cumple 1FN + cada atributo no clave depende de TODA la PK.
--   - Todas las PKs son simples (SERIAL), por lo que 2FN se cumple
--     automáticamente al no existir claves compuestas.
--
-- 3FN (Tercera Forma Normal):
--   - Cumple 2FN + no hay dependencias transitivas.
--   - Catálogos independientes: rol, especialidad, servicio están
--     en tablas separadas referenciadas por FK, evitando que datos
--     como nombre_especialidad dependan transitivamente de id_dentista.
--   - La tabla consulta separa la relación cita-servicio en vez de
--     almacenar el servicio directamente en la cita.
--   - Los estados usan restricciones CHECK en lugar de una tabla
--     de catálogo de estados, manteniendo simplicidad sin violar 3FN
--     ya que el estado es un atributo propio de cada entidad.
-- ************************************************************

CREATE SCHEMA IF NOT EXISTS claudent;
SET search_path TO claudent;

-- Catálogo de roles del sistema
CREATE TABLE rol (
  id_rol SERIAL PRIMARY KEY,
  nombre_rol VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(200)
);

-- Usuarios con acceso al sistema
CREATE TABLE usuario (
  id_usuario SERIAL PRIMARY KEY,
  id_rol INT NOT NULL REFERENCES rol(id_rol),
  nombre_usuario VARCHAR(80) NOT NULL,
  correo VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  estado VARCHAR(20) DEFAULT 'ACTIVO',
  CHECK(estado IN ('ACTIVO','INACTIVO'))
);

-- Catálogo de especialidades odontológicas
CREATE TABLE especialidad (
  id_especialidad SERIAL PRIMARY KEY,
  nombre_especialidad VARCHAR(100) NOT NULL UNIQUE,
  descripcion VARCHAR(200)
);

-- Profesionales odontológicos
CREATE TABLE dentista (
  id_dentista SERIAL PRIMARY KEY,
  id_especialidad INT NOT NULL REFERENCES especialidad(id_especialidad),
  nombre VARCHAR(80) NOT NULL,
  apellido VARCHAR(80) NOT NULL,
  telefono VARCHAR(15) UNIQUE,
  correo VARCHAR(120) UNIQUE,
  cedula_profesional VARCHAR(50) UNIQUE
);

-- Datos de pacientes
CREATE TABLE paciente (
  id_paciente SERIAL PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  apellido VARCHAR(80) NOT NULL,
  fecha_nacimiento DATE,
  telefono VARCHAR(15) UNIQUE,
  correo VARCHAR(120) UNIQUE,
  direccion VARCHAR(200),
  fecha_registro DATE DEFAULT CURRENT_DATE
);

-- Catálogo de servicios/tratamientos
CREATE TABLE servicio (
  id_servicio SERIAL PRIMARY KEY,
  nombre_servicio VARCHAR(100) NOT NULL UNIQUE,
  descripcion VARCHAR(250),
  costo NUMERIC(10,2) NOT NULL CHECK(costo > 0),
  estado VARCHAR(20) DEFAULT 'ACTIVO',
  CHECK(estado IN ('ACTIVO','INACTIVO'))
);

-- Citas programadas
CREATE TABLE cita (
  id_cita SERIAL PRIMARY KEY,
  id_paciente INT NOT NULL REFERENCES paciente(id_paciente),
  id_dentista INT NOT NULL REFERENCES dentista(id_dentista),
  fecha_cita DATE NOT NULL,
  hora_cita TIME NOT NULL,
  motivo VARCHAR(200),
  estado VARCHAR(20) DEFAULT 'PROGRAMADA',
  CHECK(estado IN ('PROGRAMADA','ATENDIDA','CANCELADA'))
);

-- Consultas/atenciones realizadas
CREATE TABLE consulta (
  id_consulta SERIAL PRIMARY KEY,
  id_cita INT NOT NULL REFERENCES cita(id_cita),
  id_servicio INT NOT NULL REFERENCES servicio(id_servicio),
  diagnostico VARCHAR(300),
  observaciones VARCHAR(300),
  fecha_consulta DATE DEFAULT CURRENT_DATE
);

-- Control de pagos
CREATE TABLE pago (
  id_pago SERIAL PRIMARY KEY,
  id_consulta INT NOT NULL REFERENCES consulta(id_consulta),
  monto NUMERIC(10,2) NOT NULL CHECK(monto > 0),
  metodo_pago VARCHAR(30) NOT NULL,
  fecha_pago DATE DEFAULT CURRENT_DATE,
  CHECK(metodo_pago IN ('EFECTIVO','TRANSFERENCIA','TARJETA'))
);

-- Bitácora de auditoría
CREATE TABLE bitacora_auditoria (
  id_bitacora SERIAL PRIMARY KEY,
  id_usuario INT REFERENCES usuario(id_usuario),
  operacion VARCHAR(20) NOT NULL,
  tabla_afectada VARCHAR(50) NOT NULL,
  fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  descripcion TEXT
);

-- ************************************************************
-- SECCIÓN 2: ÍNDICES PARA BÚSQUEDAS OPTIMIZADAS
-- ************************************************************
-- Justificación de performance:
-- Los índices aceleran las consultas más frecuentes del sistema
-- (búsqueda de citas por fecha, pacientes por nombre, pagos por
-- fecha) sin penalizar significativamente las escrituras, ya que
-- la proporción lectura/escritura en una clínica es alta.
-- ************************************************************

-- Búsqueda rápida de citas por fecha (agenda diaria/semanal)
CREATE INDEX idx_cita_fecha ON cita(fecha_cita);

-- Búsqueda de citas por estado (filtrar programadas vs atendidas)
CREATE INDEX idx_cita_estado ON cita(estado);

-- Búsqueda de citas por paciente (historial del paciente)
CREATE INDEX idx_cita_paciente ON cita(id_paciente);

-- Búsqueda de citas por dentista (agenda del dentista)
CREATE INDEX idx_cita_dentista ON cita(id_dentista);

-- Búsqueda de pacientes por apellido (recepción busca por nombre)
CREATE INDEX idx_paciente_apellido ON paciente(apellido);

-- Búsqueda de pacientes por nombre completo (búsqueda combinada)
CREATE INDEX idx_paciente_nombre_apellido ON paciente(nombre, apellido);

-- Búsqueda de consultas por fecha (reportes diarios)
CREATE INDEX idx_consulta_fecha ON consulta(fecha_consulta);

-- Búsqueda de pagos por fecha (cortes de caja)
CREATE INDEX idx_pago_fecha ON pago(fecha_pago);

-- Búsqueda de pagos por método (reportes financieros)
CREATE INDEX idx_pago_metodo ON pago(metodo_pago);

-- Búsqueda en bitácora por fecha (auditoría temporal)
CREATE INDEX idx_bitacora_fecha ON bitacora_auditoria(fecha_evento);

-- Búsqueda en bitácora por tabla afectada (auditoría específica)
CREATE INDEX idx_bitacora_tabla ON bitacora_auditoria(tabla_afectada);

-- Búsqueda de dentistas por especialidad
CREATE INDEX idx_dentista_especialidad ON dentista(id_especialidad);

-- Búsqueda de usuarios por rol
CREATE INDEX idx_usuario_rol ON usuario(id_rol);

-- ************************************************************
-- SECCIÓN 3: TRIGGER DE AUDITORÍA AUTOMÁTICA
-- ************************************************************
-- Registra automáticamente INSERT, UPDATE y DELETE en la tabla
-- paciente dentro de bitacora_auditoria.
-- ************************************************************

CREATE OR REPLACE FUNCTION fn_auditoria_paciente()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO claudent.bitacora_auditoria(operacion, tabla_afectada, descripcion)
  VALUES (
    TG_OP,
    'paciente',
    CASE
      WHEN TG_OP = 'INSERT' THEN 'Nuevo paciente: ' || NEW.nombre || ' ' || NEW.apellido
      WHEN TG_OP = 'UPDATE' THEN 'Actualizado paciente ID: ' || OLD.id_paciente
      WHEN TG_OP = 'DELETE' THEN 'Eliminado paciente: ' || OLD.nombre || ' ' || OLD.apellido
    END
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditoria_paciente
AFTER INSERT OR UPDATE OR DELETE ON paciente
FOR EACH ROW EXECUTE FUNCTION fn_auditoria_paciente();


-- ************************************************************
-- SECCIÓN 4: DML — POBLADO DE DATOS (30-50 registros)
-- ************************************************************
-- Datos ficticios generados con IA, verosímiles para una
-- clínica odontológica en México.
-- ************************************************************

-- 4.1 Roles (3 registros)
INSERT INTO rol(nombre_rol, descripcion) VALUES
('Administrador', 'Control total del sistema, gestión de usuarios y permisos'),
('Odontólogo', 'Acceso a información clínica de pacientes y tratamientos'),
('Recepcionista', 'Gestión de citas, pacientes e información administrativa');

-- 4.2 Especialidades (5 registros)
INSERT INTO especialidad(nombre_especialidad, descripcion) VALUES
('Odontología General', 'Atención integral y preventiva'),
('Ortodoncia', 'Corrección de posición dental mediante aparatos'),
('Endodoncia', 'Tratamiento de conductos radiculares'),
('Periodoncia', 'Tratamiento de encías y tejidos de soporte'),
('Odontopediatría', 'Atención dental infantil');

-- 4.3 Dentistas (5 registros)
INSERT INTO dentista(id_especialidad, nombre, apellido, telefono, correo, cedula_profesional) VALUES
(1, 'Carlos', 'Mendoza López', '9991234501', 'carlos.mendoza@claudent.mx', 'CED-001-OG'),
(2, 'María', 'García Pérez', '9991234502', 'maria.garcia@claudent.mx', 'CED-002-OR'),
(3, 'Roberto', 'Hernández Díaz', '9991234503', 'roberto.hernandez@claudent.mx', 'CED-003-EN'),
(4, 'Ana', 'Martínez Sosa', '9991234504', 'ana.martinez@claudent.mx', 'CED-004-PE'),
(5, 'Luis', 'Cervantes Ruiz', '9991234505', 'luis.cervantes@claudent.mx', 'CED-005-OP');

-- 4.4 Pacientes (10 registros)
INSERT INTO paciente(nombre, apellido, fecha_nacimiento, telefono, correo, direccion) VALUES
('Juan', 'Pérez Canul', '1990-03-15', '9997654301', 'juan.perez@mail.com', 'Calle 60 #401, Centro, Mérida'),
('Laura', 'Sánchez May', '1985-07-22', '9997654302', 'laura.sanchez@mail.com', 'Av. Itzáes #120, Mérida'),
('Pedro', 'López Tun', '1978-11-10', '9997654303', 'pedro.lopez@mail.com', 'Calle 50 #305, Centro, Mérida'),
('Sofía', 'Ramírez Chan', '2000-01-05', '9997654304', 'sofia.ramirez@mail.com', 'Fracc. Las Américas, Mérida'),
('Diego', 'Torres Pech', '1995-09-18', '9997654305', 'diego.torres@mail.com', 'Col. García Ginerés, Mérida'),
('Valentina', 'Cruz Balam', '2010-04-30', '9997654306', 'valentina.cruz@mail.com', 'Fracc. Francisco de Montejo, Mérida'),
('Miguel', 'Flores Ek', '1968-12-25', '9997654307', 'miguel.flores@mail.com', 'Calle 39 #200, Centro, Mérida'),
('Carmen', 'Vega Poot', '1992-06-14', '9997654308', 'carmen.vega@mail.com', 'Col. Chuburná, Mérida'),
('Andrés', 'Domínguez Ku', '1988-08-03', '9997654309', 'andres.dominguez@mail.com', 'Fracc. Altabrisa, Mérida'),
('Isabella', 'Moreno Cab', '2015-02-20', '9997654310', 'isabella.moreno@mail.com', 'Col. México Norte, Mérida');

-- 4.5 Usuarios (4 registros)
INSERT INTO usuario(id_rol, nombre_usuario, correo, password_hash) VALUES
(1, 'Admin Sistema', 'admin@claudent.mx', '$2b$12$LJ3m5xKzVq8r7WfD3YmBNe'),
(2, 'Dr. Carlos Mendoza', 'carlos.mendoza@claudent.mx', '$2b$12$Xk9pLmNvBw2s4TfG6hJcQe'),
(2, 'Dra. María García', 'maria.garcia@claudent.mx', '$2b$12$Rn7qHjYzAx1u3VdE5gIbMa'),
(3, 'Recepción Principal', 'recepcion@claudent.mx', '$2b$12$Wp4sKlOyC03t6XhF8jNdRi');

-- 4.6 Servicios (8 registros)
INSERT INTO servicio(nombre_servicio, descripcion, costo) VALUES
('Limpieza Dental', 'Profilaxis dental completa con ultrasonido', 800.00),
('Extracción Simple', 'Extracción de pieza dental sin complicaciones', 1200.00),
('Resina Dental', 'Restauración con resina fotopolimerizable', 900.00),
('Tratamiento de Conductos', 'Endodoncia unirradicular completa', 4500.00),
('Ortodoncia Brackets', 'Colocación de brackets metálicos convencionales', 15000.00),
('Blanqueamiento Dental', 'Blanqueamiento con peróxido de hidrógeno al 35%', 3500.00),
('Corona Dental', 'Corona de porcelana sobre metal', 5000.00),
('Consulta General', 'Revisión y diagnóstico odontológico general', 500.00);

-- 4.7 Citas (12 registros)
INSERT INTO cita(id_paciente, id_dentista, fecha_cita, hora_cita, motivo, estado) VALUES
(1, 1, '2025-09-01', '09:00', 'Limpieza dental semestral', 'ATENDIDA'),
(2, 2, '2025-09-01', '10:00', 'Revisión de brackets', 'ATENDIDA'),
(3, 3, '2025-09-02', '11:00', 'Dolor molar intenso', 'ATENDIDA'),
(4, 1, '2025-09-03', '09:30', 'Revisión general primera vez', 'ATENDIDA'),
(5, 4, '2025-09-04', '14:00', 'Sangrado de encías', 'ATENDIDA'),
(6, 5, '2025-09-05', '10:00', 'Revisión dental infantil', 'ATENDIDA'),
(7, 1, '2025-09-08', '08:30', 'Corona dental', 'ATENDIDA'),
(8, 3, '2025-09-09', '15:00', 'Dolor al masticar', 'ATENDIDA'),
(1, 1, '2025-09-15', '09:00', 'Revisión post-limpieza', 'PROGRAMADA'),
(9, 2, '2025-09-16', '11:00', 'Evaluación para ortodoncia', 'PROGRAMADA'),
(10, 5, '2025-09-17', '10:00', 'Primera consulta infantil', 'PROGRAMADA'),
(3, 1, '2025-09-20', '16:00', 'Seguimiento tratamiento', 'CANCELADA');

-- 4.8 Consultas (8 registros — las citas atendidas)
INSERT INTO consulta(id_cita, id_servicio, diagnostico, observaciones) VALUES
(1, 1, 'Acumulación moderada de sarro', 'Se realizó limpieza completa. Próxima en 6 meses.'),
(2, 5, 'Progreso normal de ortodoncia', 'Ajuste de arco superior. Control en 4 semanas.'),
(3, 4, 'Pulpitis irreversible en molar 36', 'Se inicia endodoncia. Segunda cita para obturación.'),
(4, 8, 'Paciente sin caries activas', 'Buena higiene bucal. Se recomienda selladores.'),
(5, 1, 'Gingivitis leve generalizada', 'Se realizó profilaxis y se instruyó técnica de cepillado.'),
(6, 8, 'Dentición mixta normal para la edad', 'Sin anomalías. Próxima revisión en 6 meses.'),
(7, 7, 'Fractura coronal en premolar 14', 'Se prepara para corona dental. Toma de impresión.'),
(8, 3, 'Caries profunda en molar 46', 'Restauración con resina. Sin exposición pulpar.');

-- 4.9 Pagos (8 registros)
INSERT INTO pago(id_consulta, monto, metodo_pago) VALUES
(1, 800.00, 'EFECTIVO'),
(2, 2500.00, 'TARJETA'),
(3, 4500.00, 'TRANSFERENCIA'),
(4, 500.00, 'EFECTIVO'),
(5, 800.00, 'TARJETA'),
(6, 500.00, 'EFECTIVO'),
(7, 5000.00, 'TRANSFERENCIA'),
(8, 900.00, 'TARJETA');

-- 4.10 Bitácora (registros manuales adicionales, 3 registros)
INSERT INTO bitacora_auditoria(id_usuario, operacion, tabla_afectada, descripcion) VALUES
(1, 'CREATE', 'usuario', 'Se creó usuario para Dr. Carlos Mendoza'),
(1, 'CREATE', 'usuario', 'Se creó usuario para Dra. María García'),
(1, 'GRANT', 'sistema', 'Se asignaron privilegios al rol Recepcionista');

-- Total de registros insertados: 63
-- rol(3) + especialidad(5) + dentista(5) + paciente(10) + usuario(4)
-- + servicio(8) + cita(12) + consulta(8) + pago(8) + bitacora(3)


-- ************************************************************
-- SECCIÓN 5: CONSULTAS ANALÍTICAS DE NEGOCIO (8 consultas)
-- ************************************************************

-- CONSULTA 1: Listado de pacientes con sus citas programadas
-- Usa INNER JOIN para cruzar paciente-cita-dentista
SELECT
    p.nombre || ' ' || p.apellido AS paciente,
    d.nombre || ' ' || d.apellido AS dentista,
    c.fecha_cita,
    c.hora_cita,
    c.motivo,
    c.estado
FROM cita c
INNER JOIN paciente p ON c.id_paciente = p.id_paciente
INNER JOIN dentista d ON c.id_dentista = d.id_dentista
WHERE c.estado = 'PROGRAMADA'
ORDER BY c.fecha_cita, c.hora_cita;

-- CONSULTA 2: Cantidad de pacientes atendidos por odontólogo
-- Usa COUNT + GROUP BY + INNER JOIN
SELECT
    d.nombre || ' ' || d.apellido AS dentista,
    e.nombre_especialidad AS especialidad,
    COUNT(DISTINCT c.id_paciente) AS pacientes_atendidos,
    COUNT(c.id_cita) AS total_citas
FROM dentista d
INNER JOIN especialidad e ON d.id_especialidad = e.id_especialidad
LEFT JOIN cita c ON d.id_dentista = c.id_dentista AND c.estado = 'ATENDIDA'
GROUP BY d.id_dentista, d.nombre, d.apellido, e.nombre_especialidad
ORDER BY pacientes_atendidos DESC;

-- CONSULTA 3: Ingresos totales por servicio/tratamiento
-- Usa SUM + GROUP BY + INNER JOIN entre consulta-servicio-pago
SELECT
    s.nombre_servicio,
    COUNT(co.id_consulta) AS veces_realizado,
    SUM(pa.monto) AS ingreso_total,
    AVG(pa.monto) AS ingreso_promedio
FROM servicio s
INNER JOIN consulta co ON s.id_servicio = co.id_servicio
INNER JOIN pago pa ON co.id_consulta = pa.id_consulta
GROUP BY s.id_servicio, s.nombre_servicio
ORDER BY ingreso_total DESC;

-- CONSULTA 4: Promedio de pagos por método de pago
-- Usa AVG + COUNT + SUM + GROUP BY
SELECT
    metodo_pago,
    COUNT(*) AS cantidad_pagos,
    SUM(monto) AS total_recaudado,
    AVG(monto) AS promedio_pago,
    MIN(monto) AS pago_minimo,
    MAX(monto) AS pago_maximo
FROM pago
GROUP BY metodo_pago
ORDER BY total_recaudado DESC;

-- CONSULTA 5: Tratamientos más solicitados con ranking
-- Usa COUNT + GROUP BY + HAVING para filtrar los más populares
SELECT
    s.nombre_servicio,
    s.costo AS precio_lista,
    COUNT(co.id_consulta) AS veces_solicitado,
    SUM(pa.monto) AS ingresos_generados
FROM servicio s
INNER JOIN consulta co ON s.id_servicio = co.id_servicio
INNER JOIN pago pa ON co.id_consulta = pa.id_consulta
GROUP BY s.id_servicio, s.nombre_servicio, s.costo
HAVING COUNT(co.id_consulta) >= 1
ORDER BY veces_solicitado DESC;

-- CONSULTA 6: Pacientes sin citas registradas
-- Usa LEFT JOIN para encontrar pacientes inactivos
SELECT
    p.id_paciente,
    p.nombre || ' ' || p.apellido AS paciente,
    p.telefono,
    p.correo,
    p.fecha_registro
FROM paciente p
LEFT JOIN cita c ON p.id_paciente = c.id_paciente
WHERE c.id_cita IS NULL
ORDER BY p.fecha_registro;

-- CONSULTA 7: Historial completo de atención por paciente
-- Usa múltiples INNER JOIN para cruzar 5 tablas
SELECT
    p.nombre || ' ' || p.apellido AS paciente,
    ci.fecha_cita,
    d.nombre || ' ' || d.apellido AS dentista,
    s.nombre_servicio AS tratamiento,
    co.diagnostico,
    pa.monto,
    pa.metodo_pago
FROM paciente p
INNER JOIN cita ci ON p.id_paciente = ci.id_paciente
INNER JOIN consulta co ON ci.id_cita = co.id_cita
INNER JOIN dentista d ON ci.id_dentista = d.id_dentista
INNER JOIN servicio s ON co.id_servicio = s.id_servicio
INNER JOIN pago pa ON co.id_consulta = pa.id_consulta
ORDER BY p.apellido, ci.fecha_cita;

-- CONSULTA 8: Reporte mensual de ingresos por dentista
-- Usa SUM + COUNT + GROUP BY + ORDER BY con múltiples JOINs
SELECT
    d.nombre || ' ' || d.apellido AS dentista,
    e.nombre_especialidad,
    COUNT(DISTINCT ci.id_cita) AS citas_atendidas,
    COUNT(co.id_consulta) AS consultas_realizadas,
    COALESCE(SUM(pa.monto), 0) AS ingresos_generados
FROM dentista d
INNER JOIN especialidad e ON d.id_especialidad = e.id_especialidad
LEFT JOIN cita ci ON d.id_dentista = ci.id_dentista AND ci.estado = 'ATENDIDA'
LEFT JOIN consulta co ON ci.id_cita = co.id_cita
LEFT JOIN pago pa ON co.id_consulta = pa.id_consulta
GROUP BY d.id_dentista, d.nombre, d.apellido, e.nombre_especialidad
ORDER BY ingresos_generados DESC;


-- ************************************************************
-- SECCIÓN 6: DCL — ROLES, PRIVILEGIOS Y SEGURIDAD
-- ************************************************************
-- Se implementan 3 roles con privilegios diferenciados,
-- aplicando el principio de mínimo privilegio.
-- ************************************************************

-- 6.1 Crear roles
CREATE ROLE claudent_admin WITH LOGIN PASSWORD 'Admin2025$Clau';
CREATE ROLE claudent_odontologo WITH LOGIN PASSWORD 'Odont2025$Clau';
CREATE ROLE claudent_recepcionista WITH LOGIN PASSWORD 'Recep2025$Clau';

-- 6.2 Conceder acceso al esquema
GRANT USAGE ON SCHEMA claudent TO claudent_admin, claudent_odontologo, claudent_recepcionista;

-- 6.3 Permisos del Administrador (acceso total)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA claudent TO claudent_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA claudent TO claudent_admin;

-- 6.4 Permisos del Odontólogo (acceso clínico, lectura + escritura parcial)
-- Lectura: paciente, cita, consulta, servicio, especialidad, dentista
GRANT SELECT ON claudent.paciente, claudent.cita, claudent.consulta,
    claudent.servicio, claudent.especialidad, claudent.dentista
TO claudent_odontologo;
-- Escritura: puede registrar consultas y actualizar citas
GRANT INSERT, UPDATE ON claudent.consulta TO claudent_odontologo;
GRANT UPDATE(estado) ON claudent.cita TO claudent_odontologo;
-- Secuencias necesarias para INSERT
GRANT USAGE ON SEQUENCE claudent.consulta_id_consulta_seq TO claudent_odontologo;
-- SIN acceso a: usuario, rol, pago, bitacora_auditoria

-- 6.5 Permisos de la Recepcionista (acceso administrativo)
-- Lectura: paciente, cita, servicio, dentista, especialidad
GRANT SELECT ON claudent.paciente, claudent.cita, claudent.servicio,
    claudent.dentista, claudent.especialidad
TO claudent_recepcionista;
-- Escritura: puede gestionar pacientes y citas
GRANT INSERT, UPDATE ON claudent.paciente TO claudent_recepcionista;
GRANT INSERT, UPDATE ON claudent.cita TO claudent_recepcionista;
-- Secuencias necesarias
GRANT USAGE ON SEQUENCE claudent.paciente_id_paciente_seq TO claudent_recepcionista;
GRANT USAGE ON SEQUENCE claudent.cita_id_cita_seq TO claudent_recepcionista;
-- SIN acceso a: consulta (escritura), pago, usuario, rol, bitacora_auditoria

-- 6.6 Revocar permisos explícitamente (reforzar mínimo privilegio)
REVOKE ALL ON claudent.usuario FROM claudent_odontologo, claudent_recepcionista;
REVOKE ALL ON claudent.rol FROM claudent_odontologo, claudent_recepcionista;
REVOKE ALL ON claudent.bitacora_auditoria FROM claudent_odontologo, claudent_recepcionista;
REVOKE ALL ON claudent.pago FROM claudent_recepcionista;

-- ************************************************************
-- SECCIÓN 7: PRUEBAS DE SEGURIDAD
-- ************************************************************
-- Ejecutar cada bloque con SET ROLE para simular accesos.
-- ************************************************************

-- PRUEBA 1: Administrador consulta todas las tablas (PERMITIDO)
SET ROLE claudent_admin;
SELECT * FROM claudent.usuario LIMIT 3;
SELECT * FROM claudent.pago LIMIT 3;
RESET ROLE;

-- PRUEBA 2: Odontólogo consulta pacientes (PERMITIDO)
SET ROLE claudent_odontologo;
SELECT * FROM claudent.paciente LIMIT 3;
RESET ROLE;

-- PRUEBA 3: Recepcionista crea una cita (PERMITIDO)
SET ROLE claudent_recepcionista;
INSERT INTO claudent.cita(id_paciente, id_dentista, fecha_cita, hora_cita, motivo)
VALUES (2, 1, '2025-10-01', '09:00', 'Limpieza dental');
RESET ROLE;

-- PRUEBA 4: Recepcionista intenta ver pagos (BLOQUEADO — permission denied)
SET ROLE claudent_recepcionista;
SELECT * FROM claudent.pago;  -- ERROR: permission denied for table pago
RESET ROLE;

-- PRUEBA 5: Odontólogo intenta administrar usuarios (BLOQUEADO — permission denied)
SET ROLE claudent_odontologo;
INSERT INTO claudent.usuario(id_rol, nombre_usuario, correo, password_hash)
VALUES (2, 'Intruso', 'intruso@mail.com', 'hash123');  -- ERROR: permission denied
RESET ROLE;

-- ************************************************************
-- Matriz de Roles y Privilegios
-- ************************************************************
-- Tabla               | Administrador | Odontólogo    | Recepcionista
-- --------------------|---------------|---------------|---------------
-- rol                 | ALL           | -             | -
-- usuario             | ALL           | -             | -
-- especialidad        | ALL           | SELECT        | SELECT
-- dentista            | ALL           | SELECT        | SELECT
-- paciente            | ALL           | SELECT        | SELECT,INSERT,UPDATE
-- servicio            | ALL           | SELECT        | SELECT
-- cita                | ALL           | SELECT,UPDATE | SELECT,INSERT,UPDATE
-- consulta            | ALL           | SELECT,INSERT,UPDATE | -
-- pago                | ALL           | -             | -
-- bitacora_auditoria  | ALL           | -             | -
-- ************************************************************
