Create Table Cliente(
id_cliente Serial primary key,
nombre varchar(100) not null,
correo varchar(100),
telefono varchar(20),
direccion varchar(150)
);

Create Table Reservas(
id_reserva Serial primary key,
id_cliente INT REFERENCES Cliente(id_cliente),
tipo_evento varchar(45) not null,
fecha_evento DATE not null,
lugar varchar(20),
costo NUMERIC(10,2)
);

Create Table Meseros(
id_mesero Serial primary key,
nombre varchar(20) not null,
correo varchar(20),
telefono varchar(20),
direccion varchar(150)
);

INSERT INTO Cliente (nombre, correo, telefono, direccion) VALUES
('Ana Lucas', 'ana123@gmail.com', '4433221100','Calle 1, Ciudad A'),
('Michelle Vazquez', 'michelle123@gmail.com', '4433221100','Calle 2, Ciudad B'),
('Luis Alverdi', 'luis123@gmail.com', '4433221100','Calle 3, Ciudad C'),
('Alexis Guzman', 'alexis123@gmail.com', '4433221100','Calle 4, Ciudad D'),
('Marco Ramos', 'marco123@gmail.com', '4433221100','Calle 5, Ciudad E'),
('Nancy Acosta', 'nancy123@gmail.com', '4433221100','Calle 6, Ciudad F'),
('Eduardo Sosa', 'eduardo123@gmail.com', '4433221100','Calle 7, Ciudad G'),
('Kira Tejeda', 'kira123@gmail.com', '4433221100','Calle 8, Ciudad H'),
('Mony Tejeda', 'mony123@gmail.com', '4433221100','Calle 9, Ciudad I'),
('Enrique Guzman', 'enrique123@gmail.com', '4433221100','Calle 10, Ciudad J');

INSERT INTO Reservas (id_reserva, tipo_evento, fecha_evento, lugar, costo) VALUES 
(1, 'Boda', '2025-12-20', 'San Juan', 8000),
(2, 'Cumpleaños', '2026-07-09', 'San Juan', 5000),
(3, 'Bautizo', '2025-10-02', 'San Juan', 5000),
(4, 'Aniversario', '2026-06-10', 'San Juan', 8000),
(5, 'Graduacion', '2025-12-23', 'San Juan', 4000),
(6, 'Fiesta Infantil', '2026-08-30', 'San Juan', 5000),
(7, 'Boda', '2025-03-04', 'San Juan', 8000),
(8, 'Titulacion', '2026-02-15', 'San Juan', 10000),
(9, 'Cumpleaños', '2025-05-31', 'San Juan', 5000),
(10,'Celebridad', '2026-08-27', 'San Juan', 3000);