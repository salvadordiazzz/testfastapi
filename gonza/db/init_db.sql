-- Eliminar tablas si existen
DROP TABLE IF EXISTS alertas CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS licitaciones CASCADE;

-- Tabla de licitaciones
CREATE TABLE licitaciones (
    id SERIAL PRIMARY KEY,
    empresa VARCHAR(255) NOT NULL,
    numero_licitacion VARCHAR(100),
    fecha DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para licitaciones
CREATE INDEX idx_licitaciones_empresa ON licitaciones(empresa);
CREATE INDEX idx_licitaciones_fecha ON licitaciones(fecha);

-- Tabla de items
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    licitacion_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    cantidad INTEGER DEFAULT 1,
    precio_unitario DECIMAL(15, 2) NOT NULL,
    precio_total DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id) ON DELETE CASCADE
);

-- Índices para items
CREATE INDEX idx_items_licitacion ON items(licitacion_id);
CREATE INDEX idx_items_descripcion ON items(descripcion);
CREATE INDEX idx_items_created_at ON items(created_at DESC);

-- Tabla de alertas
CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    tipo_anomalia VARCHAR(50) NOT NULL,
    descripcion TEXT,
    score_riesgo INTEGER CHECK (score_riesgo >= 0 AND score_riesgo <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- Índices para alertas
CREATE INDEX idx_alertas_item ON alertas(item_id);
CREATE INDEX idx_alertas_score ON alertas(score_riesgo DESC);
CREATE INDEX idx_alertas_tipo ON alertas(tipo_anomalia);

-- Comentarios para documentación
COMMENT ON TABLE licitaciones IS 'Almacena información de las licitaciones';
COMMENT ON TABLE items IS 'Almacena los items cotizados en cada licitación';
COMMENT ON TABLE alertas IS 'Almacena las alertas de anomalías detectadas';