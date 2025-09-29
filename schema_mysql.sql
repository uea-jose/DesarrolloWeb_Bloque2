"
-- schema_mysql.sql
CREATE TABLE IF NOT EXISTS categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL UNIQUE,
  descripcion TEXT NULL,
  categoria_id INT NOT NULL,
  precio DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_prod_cat FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inventario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  producto_id INT NOT NULL UNIQUE,
  stock INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_inv_prod FOREIGN KEY (producto_id) REFERENCES productos(id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT IGNORE INTO categorias(nombre) VALUES ('Femenino'),('Masculino'),('Esencia');
