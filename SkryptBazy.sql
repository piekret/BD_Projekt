USE master
GO
CREATE DATABASE SklepMiesny

USE SklepMiesny
GO

CREATE TABLE Pracownik (
	PracownikID INT IDENTITY(1,1) PRIMARY KEY,
	Imie VARCHAR(50) NOT NULL,
	Nazwisko VARCHAR(100) NOT NULL,
	DataZatrudnienia DATE NOT NULL
)

CREATE TABLE Produkt (
	ProduktID INT IDENTITY(1,1) PRIMARY KEY,
	Nazwa VARCHAR(200) NOT NULL,
	DomyslnaCena MONEY NOT NULL
)

CREATE TABLE Dostawca (
	DostawcaID INT IDENTITY(1,1) PRIMARY KEY,
	Nazwa VARCHAR(200) NOT NULL,
	Email VARCHAR(50) NOT NULL,
	[Status] CHAR(1) NOT NULL,
	Miasto VARCHAR(64) NOT NULL,
)

CREATE TABLE Zamowienie (
	ZamowienieID INT IDENTITY(1,1) PRIMARY KEY,
	DostawcaID INT FOREIGN KEY REFERENCES dbo.Dostawca(DostawcaID),
	Opis VARCHAR(2000) NOT NULL,
	Numer INT NOT NULL,
	DataZamowienia DATE NOT NULL,
	[Status] VARCHAR(20) NOT NULL
)

CREATE TABLE ZamowienieSzczegoly (
	ID INT IDENTITY(1,1) PRIMARY KEY,
	ZamowienieID INT FOREIGN KEY REFERENCES dbo.Zamowienie(ZamowienieID),
	ProduktID INT FOREIGN KEY REFERENCES dbo.Produkt(ProduktID),
	Ilosc FLOAT NOT NULL,
	Cena MONEY NOT NULL
)

CREATE TABLE Magazyn (
	ID INT IDENTITY(1,1) PRIMARY KEY,
	ProduktID INT FOREIGN KEY REFERENCES dbo.Produkt(ProduktID),
	Ilosc FLOAT,
	DataWaznosci DATE,
	ZamowienieID INT FOREIGN KEY REFERENCES dbo.Zamowienie(ZamowienieID)
)

CREATE TABLE Sprzedaz (
	SprzedazID INT IDENTITY(1,1) PRIMARY KEY,
	PracownikID INT FOREIGN KEY REFERENCES dbo.Pracownik(PracownikID),
	[Data] DATE,
	RodzajPlatnosci VARCHAR(25)
)

CREATE TABLE SprzedazSzczegoly (
	ID INT IDENTITY(1,1) PRIMARY KEY,
	SprzedazID INT FOREIGN KEY REFERENCES dbo.Sprzedaz(SprzedazID),
	ProduktID INT FOREIGN KEY REFERENCES dbo.Produkt(ProduktID),
	Cena MONEY,
	Ilosc FLOAT
)

ALTER TABLE Pracownik
ADD [Status] VARCHAR(20)

ALTER TABLE Dostawca
ADD [Status] CHAR(1)

ALTER TABLE ZamowienieSzczegoly
ADD DataWaznosci DATE


CREATE VIEW vAktywniPracownicy
AS
	SELECT * FROM Pracownik
	WHERE [Status] = 'Pracuje'


CREATE VIEW vAktywniDostawcy
AS
	SELECT * FROM Dostawca
	WHERE [Status] = 'T'


CREATE VIEW vNieZrealizowane
AS
	SELECT * FROM Zamowienie
	WHERE [Status] = 'W Realizacji'


CREATE VIEW vZamowienie
AS
	SELECT z.ZamowienieID, d.Nazwa, z.Opis, z.DataZamowienia, z.[Status]
	FROM Zamowienie z
	JOIN Dostawca d ON z.DostawcaID = d.DostawcaID


CREATE VIEW vSprzedSzczeg
AS
	SELECT s.SprzedazID, p.Nazwa, s.Cena, s.Ilosc
	FROM SprzedazSzczegoly s
	JOIN Produkt p ON p.ProduktID = s.ProduktID


CREATE VIEW vMagazyn
AS
	SELECT m.ID, p.Nazwa, m.Ilosc, m.DataWaznosci
	FROM Magazyn m
	JOIN Produkt p ON m.ProduktID = p.ProduktID


CREATE VIEW vZamSzczeg
AS
	SELECT zs.ID, zs.ZamowienieID, p.Nazwa, zs.Ilosc, zs.Cena, zs.DataWaznosci
	FROM ZamowienieSzczegoly zs
	JOIN Produkt p ON p.ProduktID = zs.ProduktID


CREATE OR ALTER PROC uspDodajDoZamowienia(@ZamowienieID INT, @ProduktID INT, @Ilosc FLOAT, @Cena MONEY)
AS
BEGIN
    IF EXISTS (SELECT 1 FROM Zamowienie WHERE ZamowienieID = @ZamowienieID AND [Status] NOT IN ('Zrealizowane', 'Anulowane'))
    BEGIN
        INSERT INTO ZamowienieSzczegoly(ZamowienieID, ProduktID, Ilosc, Cena)
        VALUES (@ZamowienieID, @ProduktID, @Ilosc, @Cena)
    END
    ELSE
    BEGIN
        RAISERROR('Nie prawidłowe zamówienie', 10, 10)
    END
END


CREATE TRIGGER trMagazyn ON Magazyn
INSTEAD OF INSERT, UPDATE, DELETE
AS
BEGIN
	RAISERROR('Użyj Procedury', 10, 10)
	ROLLBACK TRAN
END


CREATE TRIGGER trSprzedaz ON Sprzedaz
INSTEAD OF INSERT, UPDATE, DELETE
AS
BEGIN
	RAISERROR('Użyj Procedury', 10, 10)
	ROLLBACK TRAN
END


CREATE OR ALTER PROC uspZamowienieZrealizowane(@ZamowienieID INT)
AS
BEGIN
	;DISABLE TRIGGER trMagazyn ON Magazyn

	DECLARE @linie CURSOR
	DECLARE @ProduktID INT
	DECLARE @Ilosc FLOAT
	DECLARE @Cena MONEY
	DECLARE @DataWaznosci DATE

	SET @linie = CURSOR FOR
	SELECT ProduktID, Ilosc, Cena, DataWaznosci FROM ZamowienieSzczegoly
	WHERE ZamowienieID = @ZamowienieID

	OPEN @linie 
	FETCH NEXT FROM @linie
	INTO @ProduktID, @Ilosc, @Cena, @DataWaznosci

	WHILE @@FETCH_STATUS = 0
	BEGIN
		IF EXISTS (SELECT 1 FROM Magazyn WHERE ProduktID = @ProduktID AND DataWaznosci = @DataWaznosci)
		BEGIN
			UPDATE Magazyn
			SET Ilosc = Ilosc + @Ilosc
			WHERE ProduktID = @ProduktID AND DataWaznosci = @DataWaznosci
		END
		ELSE
		BEGIN
			INSERT INTO Magazyn VALUES (@ProduktID, @Ilosc, @DataWaznosci)
		END

		FETCH NEXT FROM @linie
		INTO @ProduktID, @Ilosc, @Cena, @DataWaznosci
	END

	UPDATE Zamowienie
	SET [Status] = 'Zrealizowane'
	WHERE ZamowienieID = @ZamowienieID

	CLOSE @linie
	DEALLOCATE @linie

	;ENABLE TRIGGER trMagazyn ON Magazyn
END


CREATE OR ALTER PROC uspUsunPrzeterminowane
AS
BEGIN
	;DISABLE TRIGGER trMagazyn ON Magazyn

	DELETE FROM Magazyn
	WHERE DataWaznosci < GETDATE()

	;ENABLE TRIGGER trMagazyn ON Magazyn
END

CREATE OR ALTER PROC uspSprzedaz(@SprzedazID INT)
AS
BEGIN
	;DISABLE TRIGGER trMagazyn ON Magazyn

	DECLARE @linie CURSOR
	DECLARE @ID INT
	DECLARE @ProduktID INT	
	DECLARE @Ilosc FLOAT
	DECLARE @MinData DATE
	DECLARE @MagazynID INT
	DECLARE @IloscWmagazynie FLOAT

	SET @linie = CURSOR FOR
	SELECT ID, ProduktID, Ilosc FROM SprzedazSzczegoly
	WHERE SprzedazID = @SprzedazID
	
	OPEN @linie
	FETCH NEXT FROM @linie
	INTO @ID, @ProduktID, @Ilosc

	WHILE @@FETCH_STATUS = 0
	BEGIN
		SELECT @MinData = MIN(DataWaznosci)
		FROM Magazyn
		WHERE ProduktID = @ProduktID
		
		SELECT @MagazynID = ID, @IloscWmagazynie = Ilosc
		FROM Magazyn
		WHERE ProduktID = @ProduktID AND DataWaznosci = @MinData

		IF (@Ilosc > @IloscWmagazynie)
		BEGIN
			DELETE FROM Magazyn
			WHERE ProduktID = @ProduktID AND DataWaznosci = @MinData

			SET @Ilosc = @Ilosc - @IloscWmagazynie

			SELECT @MinData = MIN(DataWaznosci)
			FROM Magazyn
			WHERE ProduktID = @ProduktID
		
			SELECT @MagazynID = ID, @IloscWmagazynie = Ilosc
			FROM Magazyn
			WHERE ProduktID = @ProduktID AND DataWaznosci = @MinData

			UPDATE Magazyn
			SET Ilosc = Ilosc - @Ilosc
			WHERE ID = @MagazynID
		END
		
		IF (@Ilosc = @IloscWmagazynie)
		BEGIN
			DELETE FROM Magazyn
			WHERE ID = @MagazynID
		END

		IF (@Ilosc < @IloscWmagazynie)
		BEGIN
			UPDATE Magazyn
			SET Ilosc = Ilosc - @Ilosc
			WHERE ID = @MagazynID
		END
		FETCH NEXT FROM @linie
		INTO @ID, @ProduktID, @Ilosc
	END

	CLOSE @linie
	DEALLOCATE @linie

	;ENABLE TRIGGER trMagazyn ON Magazyn
END

CREATE OR ALTER PROC uspDodajSprzedaz(@PracownikID INT, @RodzajPlatnosci VARCHAR(25), @ProduktID INT, @Cena MONEY, @Ilosc FLOAT)
AS
BEGIN
	DECLARE @idnt INT
	;DISABLE TRIGGER trSprzedaz ON Sprzedaz

	INSERT INTO Sprzedaz VALUES(@PracownikID, GETDATE(),@RodzajPlatnosci)
	SELECT @idnt = @@IDENTITY
	INSERT INTO SprzedazSzczegoly VALUES(@idnt, @ProduktID, @Cena, @Ilosc)

	EXEC uspSprzedaz @idnt

	;ENABLE TRIGGER trSprzedaz ON Sprzedaz
END
