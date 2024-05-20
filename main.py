from tkinter import *
from tkinter import ttk
import pyodbc as dbc


def dbConnect(conn_string):
    conn = dbc.connect(conn_string)
    cursor = conn.cursor()
    return cursor


def wracaj():
    okno.destroy()
    menu_glowne()


def dodajPrzyciskWracaj():
    Button(text='wróć', command=wracaj).place(x=0, y=0)


def ttreeview(*args):
    tabela = ttk.Treeview(okno, show='headings')
    tabela['columns'] = args

    for i in args:
        tabela.column(f'{i}', width=598//len(args))
        tabela.heading(f'{i}', text=f'{i}', anchor=CENTER)

    return tabela


def dodajDost():
    dodaj = Tk()
    dodaj.title('Dodawanie Dostawcy')
    dodaj.geometry('350x200')

    nazwatxt = Label(dodaj, text='Nazwa:').pack()
    nazwa = Entry(dodaj)
    nazwa.pack()

    emailtxt = Label(dodaj, text='Email:').pack()
    email = Entry(dodaj)
    email.pack()

    adrestxt = Label(dodaj, text='Adres:').pack()
    adres = Entry(dodaj)
    adres.pack()

    def dodajDo():
        if len(nazwa.get()) > 0 and len(email.get()) > 0 and len(adres.get()) > 0:
            session.execute("INSERT INTO Dostawca VALUES(?, ?, ?, 'T')",
                            nazwa.get(), email.get(), adres.get())
            session.commit()
            dodaj.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(dodaj, text='Wypełnij pola').pack()

    dodajBtn = Button(dodaj, text='Dodaj', command=dodajDo).pack()


def nieaktywnyDost():
    selected_item = tabela.selection()[0]
    dostawcaId = tabela.item(selected_item, 'values')[0]

    session.execute(f"UPDATE Dostawca SET Status = 'N' WHERE DostawcaID = {dostawcaId}")
    session.commit()


def edytujDost():
    edytuj = Tk()
    edytuj.title('Edytowanie Dostawcy')
    edytuj.geometry('375x230')

    selected_item = tabela.selection()[0]
    dostawcaID = tabela.item(selected_item, 'values')[0]
    nazwa2 = tabela.item(selected_item, 'values')[1]
    email2 = tabela.item(selected_item, 'values')[2]
    adres2 = tabela.item(selected_item, 'values')[3]

    nazwatxt = Label(edytuj, text='Nazwa:').pack()
    nazwa = Entry(edytuj)
    nazwa.insert(0, nazwa2)
    nazwa.pack()

    emailtxt = Label(edytuj, text='Email:').pack()
    email = Entry(edytuj)
    email.insert(0, email2)
    email.pack()

    adrestxt = Label(edytuj, text='Miasto:').pack()
    adres = Entry(edytuj)
    adres.insert(0, adres2)
    adres.pack()


    def edytujDOST():
        if len(nazwa.get()) > 0 and len(email.get()) > 0 and len(adres.get()) > 0:
            session.execute("UPDATE Dostawca SET Nazwa = ?, Email = ?, Miasto = ? WHERE DostawcaID = ?",
                            nazwa.get(), email.get(), adres.get(), dostawcaID)
            session.commit()
            edytuj.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(edytuj, text='Wypełnij Pola').pack()

    btn = Button(edytuj, text='Ok', command=edytujDOST).pack()


def wyswietlaktywnych():
    tabela.delete(*tabela.get_children())
    aktywni = session.execute("SELECT * FROM vAktywniDostawcy")
    for i, dost in enumerate(aktywni):
        tabela.insert(parent='', index=i, values=(dost.DostawcaID,
                                                  dost.Nazwa,
                                                  dost.Email,
                                                  dost.Miasto,
                                                  dost.Status))


def dostawcy():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Dostawcy')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("DostawcaID", "Nazwa", "Email", "Miasto", "Status")

    dostawcyy = session.execute("SELECT * FROM Dostawca")
    for i, dost in enumerate(dostawcyy):
        tabela.insert(parent='', index=i, values=(dost.DostawcaID,
                                                  dost.Nazwa,
                                                  dost.Email,
                                                  dost.Miasto,
                                                  dost.Status))
    tabela.pack(pady=20, padx=75)

    dodajDostawce = Button(okno, text='Dodaj', command=dodajDost).place(x=50, y=400)
    nieaktywny = Button(okno, text='Dostawca Nieaktywny', command=nieaktywnyDost).place(x=100, y=400)
    edytujbtn = Button(okno, text='Edytuj', command=edytujDost).place(x=235, y=400)
    aktbtn = Button(okno, text='Aktywni', command=wyswietlaktywnych).place(x=300, y=400)

    dodajPrzyciskWracaj()


def usunprze():
    potwierdz = Tk()
    potwierdz.title('Powierdzanie')
    potwierdz.geometry('300x150')

    def tak():
        session.execute("EXEC uspUsunPrzeterminowane")
        session.commit()
        potwierdz.destroy()

    txt = Label(potwierdz, text='Na pewno?').pack()
    btn = Button(potwierdz, text='Tak', command=tak).pack()


def magazynek():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Magazyn')
    okno.geometry('750x500')

    tabela = ttreeview("ID", "Nazwa", "Ilosc", "DataWaznosci")

    linie = session.execute("SELECT * FROM vMagazyn")
    for i, ln in enumerate(linie):
        tabela.insert(parent='', index=i, values=(ln.ID,
                                                  ln.Nazwa,
                                                  ln.Ilosc,
                                                  ln.DataWaznosci))
    tabela.pack()

    btn = Button(okno, text='Wywal Przeterminowane', command=usunprze).place(x=50, y=400)

    dodajPrzyciskWracaj()


def dodajPracownika():
    dodawanie = Tk()
    dodawanie.title('Nowy Pracownik')
    dodawanie.geometry('350x175')

    imietxt = Label(dodawanie, text='Imie:').pack()
    imie = Entry(dodawanie)
    imie.pack()
    nazwiskotxt = Label(dodawanie, text='Nazwisko:').pack()
    nazwisko = Entry(dodawanie)
    nazwisko.pack()

    def dodajpr():
        if len(nazwisko.get()) > 0 and len(imie.get()) > 0:
            session.execute("INSERT INTO Pracownik (Imie, Nazwisko, DataZatrudnienia, Status) VALUES (?, ?, GETDATE(), 'Pracuje')",
                            imie.get(), nazwisko.get())
            session.commit()
            dodawanie.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(dodawanie, text='Wypełnij Pola').pack()

    dodajBtn = Button(dodawanie, text='Dodaj', command=dodajpr)
    dodajBtn.pack()


def edytujPrac():
    edytuj = Tk()
    edytuj.title('Edytowanie Pracownika')
    edytuj.geometry('375x200')

    selected_item = tabela.selection()[0]
    imie2 = tabela.item(selected_item, 'values')[1]
    nazwisko2 = tabela.item(selected_item, 'values')[2]
    pracownikID = tabela.item(selected_item, 'values')[0]

    imietxt = Label(edytuj, text="Imie:").pack()
    imie = Entry(edytuj)
    imie.insert(0, imie2)
    imie.pack()

    nazwiskotxt = Label(edytuj, text="Nazwisko:").pack()
    nazwisko = Entry(edytuj)
    nazwisko.insert(0, nazwisko2)
    nazwisko.pack()

    opcje = ['Pracuje', 'Zwolniony']
    status = StringVar(edytuj, value=tabela.item(selected_item, 'values')[-1])
    statustxt = Label(edytuj, text='Status: ').pack()
    statusopcj = OptionMenu(edytuj, status, *opcje)
    statusopcj.pack()

    def edytujPR():
        session.execute("UPDATE Pracownik SET Imie = ?, Nazwisko = ?, Status = ? WHERE PracownikID = ?",
                         imie.get(), nazwisko.get(), status.get(), pracownikID)
        session.commit()
        edytuj.destroy()

    edytujBtn = Button(edytuj, text='ok', command=edytujPR).pack()


def wyswietlAktywnych():
    tabela.delete(*tabela.get_children())
    pracownicy = session.execute("SELECT * FROM vAktywniPracownicy")
    for i, pr in enumerate(pracownicy):
        tabela.insert(parent='', index=i, values=(pr.PracownikID,
                                                  pr.Imie,
                                                  pr.Nazwisko,
                                                  pr.DataZatrudnienia,
                                                  pr.Status))
        

def pracownicy():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Pracownicy')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("PracownikID", "Imie", "Nazwisko", "DataZatrudnienia", "Status")

    pracownicy = session.execute("SELECT * FROM Pracownik")
    for i, pr in enumerate(pracownicy):
        tabela.insert(parent='', index=i, values=(pr.PracownikID,
                                                  pr.Imie,
                                                  pr.Nazwisko,
                                                  pr.DataZatrudnienia,
                                                  pr.Status)) 
    tabela.pack(pady=20, padx=75)

    dodajPrac = Button(okno, text='Dodaj', command=dodajPracownika).place(x=50, y=400)
    edytujprac = Button(okno, text='Edytuj', command=edytujPrac).place(x=100, y=400)
    wyswietl = Button(okno, text='Wyświetl Pracujących', command=wyswietlAktywnych).place(x=160, y=400)

    dodajPrzyciskWracaj()


def dodajProdukt():
    dodaj = Tk()
    dodaj.title('Dodawanie Produktu')
    dodaj.geometry('350x175')

    nazwatxt = Label(dodaj, text='Nazwa:').pack()
    nazwa = Entry(dodaj)
    nazwa.pack()

    domyslnatxt = Label(dodaj, text='Domyślna Cena:').pack()
    domyslnacena = Entry(dodaj)
    domyslnacena.pack()

    def dodajProd():
        if len(nazwa.get()) > 0 and len(domyslnacena.get()) > 0:
            session.execute("INSERT INTO Produkt VALUES(?, ?)", nazwa.get(), domyslnacena.get())
            session.commit()
            dodaj.destroy()
            Label(okno, text='Powiodło sie').pack()
        else:
            Label(dodaj, text='Wypełnij Pola').pack()

    dodajp = Button(dodaj, text='Dodaj', command=dodajProd).pack()


def usunProdukt():
    selected_item = tabela.selection()[0]
    prodId = tabela.item(selected_item, 'values')[0]

    session.execute(f"DELETE FROM Produkt WHERE ProduktID = {prodId}")
    session.commit()


def edytujProd():
    edytuj = Tk()
    edytuj.title('Edytowanie Produktu')
    edytuj.geometry('375x150')

    selected_item = tabela.selection()[0]
    nazwa2 = tabela.item(selected_item, 'values')[1]
    domyslnacena2 = tabela.item(selected_item, 'values')[2]
    produktID = tabela.item(selected_item, 'values')[0]

    nazwatxt = Label(edytuj, text="Imie:").pack()
    nazwa = Entry(edytuj)
    nazwa.insert(0, nazwa2)
    nazwa.pack()

    domyslnacenatxt = Label(edytuj, text="Imie:").pack()
    domyslnacena = Entry(edytuj)
    domyslnacena.insert(0, domyslnacena2)
    domyslnacena.pack()

    def edytujPROD():
        session.execute("UPDATE Produkt SET Nazwa = ?, DomyslnaCena = ? WHERE ProduktID = ?",
                        nazwa.get(), domyslnacena.get(), produktID)
        session.commit()
        edytuj.destroy()

    edytujBtn = Button(edytuj, text='ok', command=edytujPROD).pack()


def produkty():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Produkty')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("ProduktID", "Nazwa", "DomyslnaCena")

    produkt = session.execute("SELECT * FROM Produkt")
    for i, prod in enumerate(produkt):
        tabela.insert(parent='', index=i, values=(prod.ProduktID,  
                                                  prod.Nazwa,
                                                  f'{prod.DomyslnaCena:.2f}'))
        tabela.pack(pady=20, padx=75)

    dodajprodukt = Button(okno, text='Dodaj', command=dodajProdukt).place(x=50, y=400)
    usunprodukt = Button(okno, text='Usuń', command=usunProdukt).place(x=150, y=400)
    edytujBTN = Button(okno, text='Edytuj', )

    dodajPrzyciskWracaj()


def dodajSprzed():
    zamow = Tk()
    zamow.title('Sprzedaż')
    zamow.geometry('375x275')

    opcjePracownika = [prac.PracownikID for prac in session.execute("SELECT * FROM vAktywniPracownicy")]
    pracownik = IntVar(zamow, value=opcjePracownika[0])
    pracowniktxt = Label(zamow, text='Pracownik:').pack()
    wyborPracownika = OptionMenu(zamow, pracownik, *opcjePracownika)
    wyborPracownika.pack()

    opcjerodzaju = ['elektroniczna', 'gotówka']
    rodzaj = StringVar(zamow, value=opcjerodzaju[1])
    rodzajtxt = Label(zamow, text='Platnosc').pack()
    rodzaja = OptionMenu(zamow, rodzaj, *opcjerodzaju)
    rodzaja.pack()

    opcjeProduktu = [prod[0] for prod in session.execute("SELECT Nazwa FROM Produkt")]
    produkt = StringVar(zamow, value=opcjeProduktu[0])
    produkttxt = Label(zamow, text='Produkt:').pack()
    wyborProduktu = OptionMenu(zamow, produkt, *opcjeProduktu)
    wyborProduktu.pack()

    ilosctxt = Label(zamow, text='Ilosc (kg):').pack()
    ilosc = Entry(zamow)
    ilosc.pack()

    cenatxt = Label(zamow, text='Cena:').pack()
    cena = Entry(zamow)
    cena.pack()

    def dodajspr():
        if len(ilosc.get()) > 0 and len(cena.get()) > 0 and len(rodzaj.get()) > 0:
            pracownikID = [x[0] for x in session.execute("SELECT PracownikID FROM Pracownik WHERE PracownikID = ?", pracownik.get())][0]
            ProduktID = [p[0] for p in session.execute("SELECT ProduktID FROM Produkt WHERE Nazwa = ?", produkt.get())][0]

            session.execute("EXEC uspDodajSprzedaz @PracownikID = ?, @RodzajPlatnosci = ?, @ProduktID = ?, @Cena = ?, @Ilosc = ?",
                            pracownikID, rodzaj.get(), ProduktID, float(cena.get()), float(ilosc.get()))
            session.commit()
            zamow.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(zamow, text='Wypełnij Pola').pack()


    btn = Button(zamow, text='Złóż Zamówienie', command=dodajspr).pack()


def sprzedaznosc():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Sprzedaże')
    okno.geometry('750x500')

    tabela = ttreeview("SprzedazID", "PracownikID", "Data", "RodzajPlatnosci")

    sprzedaze = session.execute("SELECT * FROM Sprzedaz")
    for i, sprz in enumerate(sprzedaze):
        tabela.insert(parent='', index=i, values=(sprz.SprzedazID,
                                                  sprz.PracownikID,
                                                  sprz.Data,
                                                  sprz.RodzajPlatnosci))
    tabela.pack(pady=20, padx=75)

    dodajsprzedaz = Button(okno, text='Dodaj', command=dodajSprzed).place(x=50, y=400)
    sprzedazscg = Button(okno, text='Sprzedaż Sczegóły', command=sprzedaznoscSczeg).place(x=540, y=250)

    dodajPrzyciskWracaj()


def dodajDoSprzed():
    dodaj = Tk()
    dodaj.title('Dodawanie Do Sprzedazy')
    dodaj.geometry('375x200')

    selected_item = tabela.selection()[0]
    sprzedazID = tabela.item(selected_item, 'values')[1]

    opcjeProduktu = [prod[0] for prod in session.execute("SELECT Nazwa FROM Produkt")]
    produkt = StringVar(dodaj, value=opcjeProduktu[0])
    produkttxt = Label(dodaj, text='Produkt:').pack()
    wyborProduktu = OptionMenu(dodaj, produkt, *opcjeProduktu)
    wyborProduktu.pack()

    ilosctxt = Label(dodaj, text='Ilosc (kg):').pack()
    ilosc = Entry(dodaj)
    ilosc.pack()

    cenatxt = Label(dodaj, text='Cena:').pack()
    cena = Entry(dodaj)
    cena.pack()

    def dodajdosprzed():
        if len(ilosc.get()) > 0 and len(cena.get()) > 0 and len(produkt.get()) > 0:
            produktID = [p[0] for p in session.execute("SELECT ProduktID FROM Produkt WHERE Nazwa = ?", produkt.get())][0]
            session.execute("INSERT INTO SprzedazSzczegoly VALUES (?, ?, ?, ?)",
                            sprzedazID, produktID, cena.get(), ilosc.get())
            session.commit()
            dodaj.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(dodaj, text='Wypełnij pola').pack()

    btn = Button(dodaj, text='Dodaj', command=dodajdosprzed).pack()


def sprzedaznoscSczeg():
    global okno
    okno.destroy()
    okno = Tk()
    okno.title('Sprzedaże - Szczegóły')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("SprzedazID", "Nazwa", "Cena", "Ilosc")

    sprzedazescg = session.execute("SELECT * FROM vSprzedSzczeg")
    for i, scg in enumerate(sprzedazescg):
        tabela.insert(parent='', index=i, values=(scg.SprzedazID,
                                                  scg.Nazwa,
                                                  f'{scg.Cena:.2f}',
                                                  scg.Ilosc))
    tabela.pack(pady=20, padx=75)
    dodajbtn = Button(okno, text='Dodaj do sprzedaży', command=dodajDoSprzed).place(x=50, y=400)

    dodajPrzyciskWracaj()


def zlozZamowienie():
    zamow = Tk()
    zamow.title('Składanie Zamówienia')
    zamow.geometry('375x275')

    opcjeDostawcy = [dost.Nazwa for dost in session.execute("SELECT * FROM vAktywniDostawcy")]
    dostawca = StringVar(zamow, value=opcjeDostawcy[0])
    dostawcatxt = Label(zamow, text='Dostawca:').pack()
    wyborDostawcy = OptionMenu(zamow, dostawca, *opcjeDostawcy)
    wyborDostawcy.pack()

    opistxt = Label(zamow, text='Opis:').pack()
    opis = Entry(zamow)
    opis.pack()

    opcjeProduktu = [prod[0] for prod in session.execute("SELECT Nazwa FROM Produkt")]
    produkt = StringVar(zamow, value=opcjeProduktu[0])
    produkttxt = Label(zamow, text='Produkt:').pack()
    wyborProduktu = OptionMenu(zamow, produkt, *opcjeProduktu)
    wyborProduktu.pack()

    ilosctxt = Label(zamow, text='Ilosc (kg):').pack()
    ilosc = Entry(zamow)
    ilosc.pack()

    cenatxt = Label(zamow, text='Cena:').pack()
    cena = Entry(zamow)
    cena.pack()

    def dodajzam():
        if len(opis.get()) > 0 and len(ilosc.get()) > 0 and len(cena.get()) > 0 and len(dostawca.get()) > 0 and len(produkt.get()) > 0:
            DostawcaID = [x[0] for x in session.execute("SELECT DostawcaID FROM Dostawca WHERE Nazwa = ?", dostawca.get())][0]
            ProduktID = [p[0] for p in session.execute("SELECT ProduktID FROM Produkt WHERE Nazwa = ?", produkt.get())][0]

            session.execute("INSERT INTO Zamowienie VALUES(?, ?, GETDATE(), 'W Realizacji')",
                            DostawcaID, opis.get())

            identity = [x[0] for x in session.execute("SELECT @@IDENTITY")][0]
            session.execute("INSERT INTO ZamowienieSzczegoly(ZamowienieID, ProduktID, Ilosc, Cena) VALUES(?, ?, ?, ?)",
                            identity, ProduktID, float(ilosc.get()), float(cena.get()))
            session.commit()
            zamow.destroy()
            Label(okno, text='Powodło się').pack()
        else:
            Label(zamow, text='wypełnij pola').pack()

    btn = Button(zamow, text='Złóż Zamówienie', command=dodajzam).pack()


def zrealizowane():
    selected_item = tabela.selection()[0]
    zamowienieID = tabela.item(selected_item, 'values')[0]
    status = tabela.item(selected_item, 'values')[-1]

    for i in [x[0] for x in session.execute("SELECT DataWaznosci FROM ZamowienieSzczegoly WHERE ZamowienieID = ?", zamowienieID)]:
        if i == None:
            tekst = Label(okno, text='Brak Daty Ważnosci').pack()
        else:
            session.execute("EXEC uspZamowienieZrealizowane @ZamowienieID = ?", zamowienieID) if status == 'W Realizacji' else print("złe zamówienie")
            session.commit()


def anulujzam():
    selected_item = tabela.selection()[0]
    zamowienieID = tabela.item(selected_item, 'values')[0]
    for i in [x[0] for x in session.execute("SELECT Status FROM Zamowienie WHERE ZamowienieID = ?", zamowienieID)]:
        if i != 'Zrealizowane':
            session.execute("UPDATE Zamowienie SET Status = 'Anulowane' WHERE ZamowienieID = ?", zamowienieID)
            session.commit()
        else:
            tekst = Label(okno, text='Już Zrealizowane').pack()


def wyswietlNieZrealizowane():
    tabela.delete(*tabela.get_children())
    for i, zam in enumerate(session.execute("SELECT * FROM vNieZrealizowane")):
        tabela.insert(parent='', index=i, values=(zam.ZamowienieID,
                                                  zam.DostawcaID,
                                                  zam.Opis,
                                                  zam.DataZamowienia,
                                                  zam.Status))



def zamowienia():
    ekran.destroy()
    global okno
    okno = Tk()
    okno.title('Sklep Mięsny - Zamówienia')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("ZamowienieID", "DostawcaID", "Opis", "DataZamowienia", "Status")
    zamowienia = session.execute("SELECT * FROM vZamowienie")
    for i, zam in enumerate(zamowienia):
        tabela.insert(parent='', index=i, values=(zam.ZamowienieID,
                                                  zam.Nazwa,
                                                  zam.Opis,
                                                  zam.DataZamowienia,
                                                  zam.Status))
    tabela.pack(pady=20, padx=75)

    zlozZamowienieBtn = Button(okno, text='Złóż Zamówienie', command=zlozZamowienie).place(x=50, y=400)
    zamowScgBtn = Button(okno, text='Zamowienia Szczegóły', command=zamowieniaSczeg).place(x=540, y=250)
    zrealizowanebtn = Button(okno, text='Zrealizowane', command=zrealizowane).place(x=150, y=400)
    anulujbtn = Button(okno, text='Anuluj', command=anulujzam).place(x=240, y=400)
    niezrealizowanebtn = Button(okno, text='Nie Zrealizowane', command=wyswietlNieZrealizowane).place(x=290, y=400)

    dodajPrzyciskWracaj()


def dodajDoZam():
    dodaj = Tk()
    dodaj.title('Dodawanie Do Zamówienia')
    dodaj.geometry('375x200')

    selected_item = tabela.selection()[0]
    dostawcaID = tabela.item(selected_item, 'values')[1]

    opcjeProduktu = [prod[0] for prod in session.execute("SELECT Nazwa FROM Produkt")]
    produkt = StringVar(dodaj)
    produkttxt = Label(dodaj, text='Produkt:').pack()
    wyborProduktu = OptionMenu(dodaj, produkt, *opcjeProduktu)
    wyborProduktu.pack()

    ilosctxt = Label(dodaj, text='Ilosc (kg):').pack()
    ilosc = Entry(dodaj)
    ilosc.pack()

    cenatxt = Label(dodaj, text='Cena:').pack()
    cena = Entry(dodaj)
    cena.pack()

    def dodajdozam():
        if len(ilosc.get()) > 0 and len(cena.get()) > 0:
            produktID = [p[0] for p in session.execute("SELECT ProduktID FROM Produkt WHERE Nazwa = ?", produkt.get())][0]
            session.execute("EXEC uspDodajDoZamowienia @ZamowienieID = ?, @ProduktID = ?, @Ilosc = ?, @Cena = ?",
                            dostawcaID, produktID, float(ilosc.get()), float(cena.get()))
            session.commit()
            dodaj.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(dodaj, text='wypełnij pola').pack()

    btn = Button(dodaj, text='Dodaj', command=dodajdozam).pack()


def edytujDate():
    edytuj = Tk()
    edytuj.title('data waznosci')
    edytuj.geometry('375x150')

    selected_item = tabela.selection()[0]
    iD = tabela.item(selected_item, 'values')[0]
    
    datawaznoscitxt = Label(edytuj, text='Data Ważnosci (yyyy-mm-dd):').pack()
    data = Entry(edytuj)
    data.pack()

    def dodajDate():
        if len(data.get()) > 0:
            session.execute("UPDATE ZamowienieSzczegoly SET DataWaznosci = ? WHERE ID = ?", data.get(), iD)
            session.commit()
            edytuj.destroy()
            Label(okno, text='Powiodło się').pack()
        else:
            Label(edytuj, text='Wypełnij Pole').pack()

    btn = Button(edytuj, text='Dodaj', command=dodajDate).pack()


def zamowieniaSczeg():
    global okno
    okno.destroy()
    okno = Tk()
    okno.title('Zamówienia - Szczegóły')
    okno.geometry('750x500')

    global tabela
    tabela = ttreeview("ID", "ZamowienieID", "ProduktID", "Ilosc", "Cena", "DataWaznosci")
    szczeg = session.execute("SELECT * FROM vZamSzczeg")
    for i, sc in enumerate(szczeg):
        tabela.insert(parent='', index=i, values=(sc.ID,
                                                  sc.ZamowienieID,
                                                  sc.Nazwa,
                                                  sc.Ilosc,
                                                  f'{sc.Cena:.2f}',
                                                  sc.DataWaznosci))
    tabela.pack()

    dodajBtn = Button(okno, text='Dodaj do Zamówienia', command=dodajDoZam).place(x=50, y=400)
    dodajdatebtn = Button(okno, text='Dodaj Date', command=edytujDate).place(x=200, y=400)

    dodajPrzyciskWracaj()


def menu_glowne():
    global ekran
    ekran = Tk()
    ekran.geometry('750x500')
    ekran.title('Sklep Mięsny')

    panel = Label(text='Panel', font=('Comic Sans MS', 20))
    panel.place(anchor=N, relx=0.5)

    dostawcyBtn = Button(text='Dostawcy', command=dostawcy)
    dostawcyBtn.place(x=150, y=75)

    magazynBtn = Button(text='Magazyn', command=magazynek)
    magazynBtn.place(x=250, y=75)

    pracownikBtn = Button(text='Pracownicy', command=pracownicy)
    pracownikBtn.place(x=350, y=75)

    produktBtn = Button(text='Produkt', command=produkty)
    produktBtn.place(x=465, y=75)

    sprzedazBtn = Button(text='Sprzedaże', command=sprzedaznosc)
    sprzedazBtn.place(x=550, y=75)

    ZamowienieBtn = Button(text='Zamówienia', command=zamowienia)
    ZamowienieBtn.place(x=335, y=150)



def main():
    menu_glowne()
    global session
    session = dbConnect("DRIVER={SQL SERVER};"
                       "SERVER=DESKTOP-RS1ONME\\SQLEXPRESS;"
                       "Database=SklepMiesny;"
                       "Trusted_Connection=yes;")
    mainloop()


if __name__ == '__main__':
    main()
