CREATE DATABASE IF NOT EXISTS desarrollo_web
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE desarrollo_web;

CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre     VARCHAR(100) NOT NULL,
  email      VARCHAR(100) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL
);
