-- One-shot DB setup for the app
CREATE DATABASE IF NOT EXISTS flask_login_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE flask_login_db;

CREATE TABLE IF NOT EXISTS usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(120) NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('admin','user') DEFAULT 'user',
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
