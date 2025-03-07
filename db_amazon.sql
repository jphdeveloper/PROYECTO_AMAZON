CREATE DATABASE IF NOT EXISTS db_amazon;

USE db_amazon;
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asesor`
--

CREATE TABLE `asesor` (
  `idf_cliente` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `idf_empleado` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `asesor`
--

INSERT INTO `asesor` (`idf_cliente`, `idf_empleado`) VALUES
('12345', '10101'),
('00128', '45565'),
('1131', '45565'),
('76543', '45565');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `nombre_categoria` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_sucursal` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `presupuesto` decimal(20,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`nombre_categoria`, `nombre_sucursal`, `presupuesto`) VALUES
('Accesorios', 'Guacarí', 33000000.00),
('Camisas', 'Guacarí', 34000000.00),
('Camisetas', 'Viva Sincelejo', 28700000.00),
('Jeans', 'Guacarí', 119000000.00),
('Pantalones', 'Guacarí', 109000000.00),
('Polos', 'Guacarí', 70000000.00),
('Ropa Interior', 'Viva Sincelejo', 79000000.00),
('Vestidos', 'Guacarí', 78000000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_cliente` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_categoria` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `estado` varchar(12) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`id_cliente`, `nombre_cliente`, `nombre_categoria`, `estado`) VALUES
('00128', 'Sarai Fuentes Pertuz', 'Polos', 'Activo'),
('1131', 'Pablo Velez Altamiranda', 'Pantalones', 'Activo'),
('12345', 'Maria Paula', 'Vestidos', 'Activo'),
('19991', 'Sofia Beleño Castro', 'Pantalones', 'Activo'),
('2468', 'Juan Jaramillo', 'Camisetas', 'Activo'),
('54321', 'William Alvarez Quiroz', 'Camisetas', 'Activo'),
('55739', 'Sarah Sanchez Voz', 'Vestidos', 'Activo'),
('64567', 'Pedro Suarez', 'Accesorios', 'Activo'),
('76543', 'Ana Maria Del Mar Rios', 'Camisas', 'Activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_empleado` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_categoria` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `salario` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleado`, `nombre_empleado`, `nombre_categoria`, `salario`) VALUES
('10101', 'Avelina Alfaro', 'Polos', 3500000.00),
('1102798', 'Carlos Alfaro', 'Vestidos', 2780000.00),
('12121', 'Winner Acosta Lastre', 'Vestidos', 2900000.00),
('15151', 'Maria Castro Feria', 'Polos', 4500000.00),
('18181', 'Amanda Sevilla Lara', 'Ropa Interior', 3500000.00),
('22222', 'Elizabeth Perez Alviz', 'Ropa Interior', 4950000.00),
('32343', 'Camila Villegas Oslo', 'Camisetas', 4600000.00),
('45565', 'Katty Saenz Moron', 'Camisetas', 3750000.00),
('58583', 'Carmen Alma Vega', 'Camisetas', 5620000.00),
('76766', 'Ramiro Rojas PErez', 'Camisas', 3720000.00),
('83821', 'Brenda Osorio Bertel', 'Camisas', 3920000.00),
('98345', 'Amir Salas Martinez', 'Accesorios', 3800000.00);

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nombre_categoria` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `precio` decimal(50,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `descripcion`, `nombre_categoria`, `precio`) VALUES
('A-40A0139', 'Soporte de teléfono 3 en 1 mejorado para automóvil', 'Automotriz', 34000),
('C-50B0176', 'ANCEL AD310 Escáner universal clásico mejorado OBD II', 'Automotriz', 129000);

-- --------------------------------------------------------