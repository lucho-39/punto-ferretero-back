CREATE DATABASE IF NOT EXISTS puntoferretero;
USE puntoferretero;

CREATE TABLE IF NOT EXISTS category (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) DEFAULT NULL,
  `unit` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

LOCK TABLES `category` WRITE;
INSERT INTO `category` (`id`, `name`, `unit`) VALUES 
(1, 'Pruebas', 'Unidad'),
(2, 'Venta por Unidad', 'Unidad'),
(3, 'Venta por Metro', 'Metros'),
(4, 'Venta por Kilo', 'Kilogramo'),
(5, 'Bazar', 'Unidades'),
(6, 'Bicicleteria', 'Unidades'),
(7, 'Camping', 'Unidades'),
(8, 'Carpinteria', 'Unidades'),
(9, 'Electricidad', 'Unidades'),
(10, 'Ferreteria', 'Unidades'),
(11, 'Herramientas', 'Unidades'),
(12, 'Jardineria', 'Unidades'),
(13, 'Limpieza', 'Unidades'),
(14, 'Pintureria', 'Unidades'),
(15, 'Repuestos', 'Unidades'),
(16, 'Sanitarios', 'Unidades'),
(17, 'Cables por Rollo', 'Unidades'),
(18, 'Cables por Metro', 'Metros');
UNLOCK TABLES;

CREATE TABLE IF NOT EXISTS image (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `url_img` VARCHAR(80) DEFAULT NULL,
  `txt_alt` VARCHAR(60) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

LOCK TABLES `image` WRITE;
INSERT INTO `image` (`id`, `url_img`, `txt_alt`) VALUES 
(1, 'https://', 'Una imagen de pruebas'),
(2, 'https://', 'Otra imagen de pruebas');
UNLOCK TABLES;

CREATE TABLE IF NOT EXISTS prov (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `cod` VARCHAR(10) DEFAULT NULL,
  `name` VARCHAR(50) DEFAULT NULL,
  `obs` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

LOCK TABLES `prov` WRITE;
INSERT INTO `prov` (`id`, `cod`, `name`, `obs`) VALUES 
(1, '1', 'Proveedor General', 'Observaciones'),
(2, '100', 'MACROLED', ''),
(3, '200', 'OSRAM', ''),
(4, '300', 'CAELBI', ''),
(5, '400', 'DABOR', ''),
(6, '500', 'EMANAL', ''),
(7, '600', 'SICA', ''),
(8, '700', 'ESTRADA', ''),
(9, '1000', 'JELUZ', ''),
(10, '1100', 'KALOPS', ''),
(11, '1200', 'LORD', ''),
(12, '1800', 'SERRA', ''),
(13, '2300', 'WERKE', '');
UNLOCK TABLES;

CREATE TABLE IF NOT EXISTS product (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `art` VARCHAR(10) DEFAULT NULL,
  `cod` VARCHAR(10) DEFAULT NULL,
  `tit` VARCHAR(50) DEFAULT NULL,
  `desc` VARCHAR(200) DEFAULT NULL,
  `cat_id` INT(11) NOT NULL,
  `img_id` INT(11) NOT NULL,
  `prov_id` INT(11) NOT NULL,
  `rating` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cat_id` (`cat_id`),
  KEY `img_id` (`img_id`),
  KEY `prov_id` (`prov_id`),
  CONSTRAINT `product_ibfk_1` FOREIGN KEY (`cat_id`) REFERENCES `category` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `product_ibfk_2` FOREIGN KEY (`img_id`) REFERENCES `image` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `product_ibfk_3` FOREIGN KEY (`prov_id`) REFERENCES `prov` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

LOCK TABLES `product` WRITE;
INSERT INTO `product` (`id`, `art`, `cod`, `tit`, `desc`, `cat_id`, `img_id`, `prov_id`, `rating`) VALUES 
(1, '1000', '1000', 'Producto Inicial de Pruebas', 'Descripcion pendiente...', 1, 1, 1, 'Rating cero'),
(2, '1001', '1001', 'Segundo Producto de Pruebas', 'Descripcion del segundo producto.', 1, 1, 1, 'Rating cero');
UNLOCK TABLES;