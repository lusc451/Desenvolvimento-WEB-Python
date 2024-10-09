CREATE TABLE LucasAntunes_tbusuario(
	codigo INT,
	nome VARCHAR(80),
	email VARCHAR(50),
	senha VARCHAR(30)
);


DROP TABLE LucasAntunes_tbusuario;

SELECT Codigo, nome, email, senha FROM LucasAntunes_tbusuario;

INSERT INTO LucasAntunes_tbusuario(codigo, nome, email, senha) VALUES (1, 'Lucas', 'lucasantunes@gmail.com', 'P@ssw0rd');

INSERT INTO LucasAntunes_tbusuario(codigo) VALUES (3);

CREATE TABLE LucasAntunes_tbusuario(
	codigo INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(80),
	email VARCHAR(50) UNIQUE,
	senha VARCHAR(30)
);

INSERT INTO LucasAntunes_tbusuario(nome, email, senha) VALUES ('Lucas', 'lucasantunes1@gmail.com', 'P@ssw0rd');

SELECT Codigo, nome, email, senha FROM LucasAntunes_tbusuario WHERE codigo = 1 -- <> = diferente