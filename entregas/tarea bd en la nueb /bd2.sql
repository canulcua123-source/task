-- ============================================================
-- Base de datos: Taller Mecánico Automotriz (versión corregida)
-- ============================================================

-- 1. Fabricante
CREATE TABLE fabricante (
    id_fabricante BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 2. Modelo
CREATE TABLE modelo (
    id_modelo      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    id_fabricante  BIGINT       NOT NULL,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_modelo_fabricante
        FOREIGN KEY (id_fabricante) REFERENCES fabricante(id_fabricante)
        ON DELETE RESTRICT
);

-- 3. Cliente (apellidos separados)
CREATE TABLE cliente (
    id_cliente       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre           VARCHAR(60)  NOT NULL,
    apellido_paterno VARCHAR(60)  NOT NULL,
    apellido_materno VARCHAR(60),
    telefono         VARCHAR(20),
    correo           VARCHAR(150),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_cliente_correo UNIQUE (correo)
);

CREATE INDEX idx_cliente_apellidos ON cliente (apellido_paterno, apellido_materno);

-- 4. Vehículo
CREATE TABLE vehiculo (
    id_vehiculo       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    placa             VARCHAR(15)  NOT NULL,
    anio_fabricacion  INTEGER      NOT NULL,
    color             VARCHAR(50),
    id_cliente        BIGINT       NOT NULL,
    id_modelo         BIGINT       NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_vehiculo_placa UNIQUE (placa),

    CONSTRAINT fk_vehiculo_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
        ON DELETE RESTRICT,

    CONSTRAINT fk_vehiculo_modelo
        FOREIGN KEY (id_modelo) REFERENCES modelo(id_modelo)
        ON DELETE RESTRICT
);

CREATE INDEX idx_vehiculo_placa ON vehiculo (placa);

-- 5. Mecánico (apellidos separados)
CREATE TABLE mecanico (
    id_mecanico      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre           VARCHAR(60)  NOT NULL,
    apellido_paterno VARCHAR(60)  NOT NULL,
    apellido_materno VARCHAR(60),
    fecha_ingreso    DATE         NOT NULL DEFAULT CURRENT_DATE,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mecanico_apellidos ON mecanico (apellido_paterno, apellido_materno);

-- 6. Especialidad
CREATE TABLE especialidad (
    id_especialidad BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL UNIQUE
);

-- 7. Mecánico ↔ Especialidad (N:M)
CREATE TABLE mecanico_especialidad (
    id_mecanico     BIGINT NOT NULL,
    id_especialidad BIGINT NOT NULL,

    PRIMARY KEY (id_mecanico, id_especialidad),

    CONSTRAINT fk_me_mecanico
        FOREIGN KEY (id_mecanico) REFERENCES mecanico(id_mecanico)
        ON DELETE CASCADE,

    CONSTRAINT fk_me_especialidad
        FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad)
        ON DELETE RESTRICT
);

-- 8. Orden de servicio (sin costo_total, con fecha_salida)
CREATE TABLE orden_servicio (
    id_orden       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio          VARCHAR(30)  NOT NULL,
    fecha_ingreso  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    fecha_salida   TIMESTAMPTZ,
    diagnostico    TEXT,
    kilometraje    INTEGER      NOT NULL CHECK (kilometraje >= 0),
    estado         VARCHAR(20)  NOT NULL DEFAULT 'Pendiente'
                   CHECK (estado IN ('Pendiente', 'En proceso', 'Terminado', 'Entregado', 'Cancelado')),
    id_vehiculo    BIGINT       NOT NULL,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_orden_folio UNIQUE (folio),

    CONSTRAINT fk_orden_vehiculo
        FOREIGN KEY (id_vehiculo) REFERENCES vehiculo(id_vehiculo)
        ON DELETE RESTRICT
);

CREATE INDEX idx_orden_folio ON orden_servicio (folio);

-- 9. Mecánico ↔ Orden (N:M — varios mecánicos por orden)
CREATE TABLE mecanico_orden (
    id_mecanico BIGINT      NOT NULL,
    id_orden    BIGINT      NOT NULL,
    rol         VARCHAR(50) NOT NULL DEFAULT 'Principal',

    PRIMARY KEY (id_mecanico, id_orden),

    CONSTRAINT fk_mo_mecanico
        FOREIGN KEY (id_mecanico) REFERENCES mecanico(id_mecanico)
        ON DELETE RESTRICT,

    CONSTRAINT fk_mo_orden
        FOREIGN KEY (id_orden) REFERENCES orden_servicio(id_orden)
        ON DELETE CASCADE
);

-- 10. Refacción
CREATE TABLE refaccion (
    id_refaccion BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_p     VARCHAR(50)   NOT NULL,
    nombre       VARCHAR(150)  NOT NULL,
    precio       NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    existencias  INTEGER       NOT NULL DEFAULT 0 CHECK (existencias >= 0),
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_refaccion_codigo UNIQUE (codigo_p)
);

CREATE INDEX idx_refaccion_codigo ON refaccion (codigo_p);

-- 11. Detalle de orden (PK propia)
CREATE TABLE detalle_orden (
    id_detalle   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_orden     BIGINT        NOT NULL,
    id_refaccion BIGINT        NOT NULL,
    cantidad     INTEGER       NOT NULL CHECK (cantidad > 0),
    precio       NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_detalle_orden
        FOREIGN KEY (id_orden) REFERENCES orden_servicio(id_orden)
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_refaccion
        FOREIGN KEY (id_refaccion) REFERENCES refaccion(id_refaccion)
        ON DELETE RESTRICT
);

-- ============================================================
-- Vista: costo total por orden (reemplaza el campo costo_total)
-- ============================================================
CREATE VIEW v_costo_orden AS
SELECT
    id_orden,
    COALESCE(SUM(cantidad * precio), 0) AS costo_total
FROM detalle_orden
GROUP BY id_orden;


-- ============================================================
-- CONSULTAS DE EJEMPLO (INNER JOIN y LEFT JOIN)
-- ============================================================

-- 1. Clientes con sus vehículos — INNER JOIN
-- Solo clientes que TIENEN vehículos. Filtra por apellido.
SELECT
    c.nombre,
    c.apellido_paterno,
    c.apellido_materno,
    v.placa,
    m.nombre AS modelo,
    f.nombre AS fabricante
FROM cliente c
INNER JOIN vehiculo v   ON v.id_cliente = c.id_cliente
INNER JOIN modelo m     ON v.id_modelo = m.id_modelo
INNER JOIN fabricante f ON m.id_fabricante = f.id_fabricante
WHERE c.apellido_paterno = 'García'
ORDER BY c.apellido_paterno, c.apellido_materno, c.nombre;


-- 2. Clientes SIN vehículos — LEFT JOIN
-- Detecta clientes registrados que nunca han traído un vehículo.
SELECT
    c.apellido_paterno || ' ' || c.apellido_materno || ', ' || c.nombre AS nombre_completo,
    c.telefono,
    c.correo
FROM cliente c
LEFT JOIN vehiculo v ON v.id_cliente = c.id_cliente
WHERE v.id_vehiculo IS NULL;


-- 3. Órdenes con mecánicos asignados — INNER JOIN (tabla intermedia)
-- Muestra todos los mecánicos que trabajaron en cada orden.
SELECT
    os.folio,
    os.fecha_ingreso,
    m.nombre || ' ' || m.apellido_paterno AS mecanico,
    mo.rol,
    os.estado
FROM orden_servicio os
INNER JOIN mecanico_orden mo ON mo.id_orden = os.id_orden
INNER JOIN mecanico m        ON m.id_mecanico = mo.id_mecanico
ORDER BY os.fecha_ingreso DESC;


-- 4. Mecánicos SIN órdenes asignadas — LEFT JOIN
-- Detecta mecánicos ociosos.
SELECT
    m.nombre,
    m.apellido_paterno,
    m.apellido_materno
FROM mecanico m
LEFT JOIN mecanico_orden mo ON mo.id_mecanico = m.id_mecanico
WHERE mo.id_orden IS NULL;


-- 5. Detalle de orden con refacciones — INNER JOIN
-- Refacciones usadas en la orden 1 con subtotales.
SELECT
    r.codigo_p,
    r.nombre AS refaccion,
    d.cantidad,
    d.precio AS precio_unitario,
    (d.cantidad * d.precio) AS subtotal
FROM detalle_orden d
INNER JOIN refaccion r ON r.id_refaccion = d.id_refaccion
WHERE d.id_orden = 1;


-- 6. Refacciones SIN uso — LEFT JOIN
-- Refacciones en inventario que nunca se han usado.
SELECT
    r.codigo_p,
    r.nombre,
    r.existencias,
    r.precio
FROM refaccion r
LEFT JOIN detalle_orden d ON d.id_refaccion = r.id_refaccion
WHERE d.id_detalle IS NULL
ORDER BY r.existencias DESC;


-- 7. Buscar duplicados por apellidos — INNER JOIN (self-join)
-- IMPOSIBLE sin campos de apellido separados.
SELECT
    c1.id_cliente AS id_1,
    c1.nombre || ' ' || c1.apellido_paterno || ' ' || c1.apellido_materno AS cliente_1,
    c2.id_cliente AS id_2,
    c2.nombre || ' ' || c2.apellido_paterno || ' ' || c2.apellido_materno AS cliente_2
FROM cliente c1
INNER JOIN cliente c2
    ON  c1.apellido_paterno = c2.apellido_paterno
    AND c1.apellido_materno = c2.apellido_materno
    AND c1.id_cliente < c2.id_cliente;


-- 8. Historial completo de un vehículo — INNER JOIN múltiple
SELECT
    v.placa,
    f.nombre AS fabricante,
    mo.nombre AS modelo,
    c.apellido_paterno || ' ' || c.nombre AS propietario,
    os.folio,
    os.fecha_ingreso,
    os.fecha_salida,
    os.diagnostico,
    os.estado
FROM vehiculo v
INNER JOIN cliente c         ON v.id_cliente = c.id_cliente
INNER JOIN modelo mo         ON v.id_modelo = mo.id_modelo
INNER JOIN fabricante f      ON mo.id_fabricante = f.id_fabricante
INNER JOIN orden_servicio os ON os.id_vehiculo = v.id_vehiculo
WHERE v.placa = 'ABC1234'
ORDER BY os.fecha_ingreso DESC;


-- 9. Modelos SIN vehículos registrados — LEFT JOIN
SELECT
    f.nombre AS fabricante,
    m.nombre AS modelo
FROM modelo m
INNER JOIN fabricante f ON m.id_fabricante = f.id_fabricante
LEFT JOIN vehiculo v    ON v.id_modelo = m.id_modelo
WHERE v.id_vehiculo IS NULL
ORDER BY f.nombre, m.nombre;


-- 10. Total facturado por cliente — INNER JOIN + GROUP BY
-- Demuestra que costo_total es innecesario: se calcula al vuelo.
SELECT
    c.apellido_paterno,
    c.apellido_materno,
    c.nombre,
    COUNT(DISTINCT os.id_orden) AS total_ordenes,
    SUM(d.cantidad * d.precio)  AS total_facturado
FROM cliente c
INNER JOIN vehiculo v         ON v.id_cliente = c.id_cliente
INNER JOIN orden_servicio os  ON os.id_vehiculo = v.id_vehiculo
INNER JOIN detalle_orden d    ON d.id_orden = os.id_orden
GROUP BY c.id_cliente, c.apellido_paterno, c.apellido_materno, c.nombre
ORDER BY c.apellido_paterno, c.apellido_materno;
