"""
Modul pro testování správce úkolů pomocí pytestu a databáze MySQL.

Testy ověřují funkčnost následujících operací:
- Přidání úkolu (pozitivní i negativní scénáře)
- Aktualizace úkolu (pozitivní i negativní scénáře)
- Odstranění úkolu (pozitivní i negativní scénáře)

Každý test využívá testovací databázi `spravce_ukolu_test`, která je před každým testem vymazána,
a byla zajištěna izolace testovacích případů. Pro připojení k databázi se používají fixturny pytestu.

Použité funkce jsou importovány z modulu `spravce_ukolu.py`.
"""

import pytest
import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from spravce_ukolu import vytvoreni_tabulky, pridat_ukol, aktualizovat_ukol, odstranit_ukol, nacist_ukoly

TEST_DB_NAME = "spravce_ukolu_test"

def pripoj_test_db() -> MySQLConnection:
    """
    Připojí se k testovací databázi.

    Returns:
        MySQLConnection: Připojení k databázi.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database=TEST_DB_NAME
    )

def vytvor_test_db() -> None:
    """
    Vytvoří testovací databázi, pokud ještě neexistuje.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1111"
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"❌ Chyba při vytváření testovací databáze: {e}")

@pytest.fixture(scope="function")
def test_conn() -> MySQLConnection:
    """
    Fixture pro připojení k testovací databázi a vyčištění tabulky `ukoly` před a po každém testu.

    Yields:
        MySQLConnection: Připojení k testovací databázi.
    """
    vytvor_test_db()
    conn = pripoj_test_db()
    vytvoreni_tabulky(conn)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    yield conn
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()
    conn.close()

# 1. Přidání úkolu

def test_pridat_ukol_pozitivni(test_conn: MySQLConnection) -> None:

    """Ověřuje, že úkol lze úspěšně přidat do databáze."""

    pridat_ukol(test_conn, "Testovací úkol", "Popis testovacího úkolu")
    ukoly = nacist_ukoly(test_conn)
    assert any(u[1] == "Testovací úkol" and u[2] == "Popis testovacího úkolu" for u in ukoly)

def test_pridat_ukol_negativni(test_conn: MySQLConnection) -> None:

    """Ověřuje, že přidání úkolu s prázdnými poli vyvolá chybu."""

    with pytest.raises(Error):
        pridat_ukol(test_conn, "", "")

# 2. Aktualizace úkolu

def test_aktualizovat_ukol_pozitivni(test_conn: MySQLConnection) -> None:

    """Ověřuje, že stav úkolu lze úspěšně aktualizovat."""

    pridat_ukol(test_conn, "Úkol k aktualizaci", "Popis")
    id_ukolu = nacist_ukoly(test_conn)[0][0]
    aktualizovat_ukol(test_conn, id_ukolu, "Hotovo")
    ukoly = nacist_ukoly(test_conn)
    assert any(u[0] == id_ukolu and u[3] == "Hotovo" for u in ukoly)

def test_aktualizovat_ukol_negativni(test_conn: MySQLConnection) -> None:
    """Ověřuje, že aktualizace neexistujícího úkolu vyvolá chybu."""
    with pytest.raises(Error):
        aktualizovat_ukol(test_conn, 99999, "Neexistuje")

# 3. Odstranění úkolu

def test_odstranit_ukol_pozitivni(test_conn: MySQLConnection) -> None:

    """Ověřuje, že úkol lze úspěšně odstranit z databáze."""

    pridat_ukol(test_conn, "Úkol ke smazání", "Popis")
    id_ukolu = nacist_ukoly(test_conn)[0][0]
    odstranit_ukol(test_conn, id_ukolu)
    ukoly = nacist_ukoly(test_conn)
    assert all(u[0] != id_ukolu for u in ukoly)

def test_odstranit_ukol_negativni(test_conn: MySQLConnection) -> None:

    """Ověřuje, že odstranění neexistujícího úkolu nevyvolá chybu."""

    odstranit_ukol(test_conn, 123456)
    assert True  