"""Projekt: Vylepšený task manager"""

import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from datetime import date

DB_NAME = 'spravce_ukolu'

def vytvoreni_db() -> None:
    """
    Vytvoří databázi s názvem 'spravce_ukolu', pokud ještě neexistuje.
    Připojí se k MySQL serveru a vytvoří databázi s UTF-8 nastavením.
    """
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1111'
        )
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
        )
        print(f"✅ Databáze '{DB_NAME}' byla vytvořena nebo již existuje.")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"❌ Chyba při vytváření databáze: {e}")

def pripojeni_db() -> MySQLConnection | None:
    """
    Připojí se k databázi 'spravce_ukolu'.

    Returns:
        MySQLConnection | None: Aktivní připojení nebo None při chybě.
    """
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1111',
            database=DB_NAME
        )
        return conn
    except Error as e:
        print(f"❌ Chyba při připojení k databázi: {e}")
        return None

def vytvoreni_tabulky(conn: MySQLConnection) -> None:
    """
    Vytvoří tabulku 'ukoly', pokud ještě neexistuje.

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.
    """
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis VARCHAR(255) NOT NULL,
                stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
                datum_vytvoreni DATE NOT NULL DEFAULT (CURRENT_DATE)
            )
        ''')
        conn.commit()
        print("✅ Tabulka 'ukoly' byla vytvořena nebo již existuje.")
    except Error as e:
        print(f"❌ Chyba při vytváření tabulky: {e}")

def pridat_ukol(conn: MySQLConnection, nazev: str, popis: str) -> None:
    """
    Přidá nový úkol do tabulky 'ukoly'.

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.
        nazev (str): Název úkolu.
        popis (str): Popis úkolu.

    Raises:
        Error: Pokud jsou vstupní hodnoty prázdné.
    """
    if not nazev or not popis:
        raise Error("Název a popis úkolu nesmí být prázdné")
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
        (nazev, popis)
    )
    conn.commit()
    cursor.close()

def zobrazit_ukoly(conn: MySQLConnection) -> None:
    """
    Zobrazí seznam úkolů se stavem 'Nezahájeno' nebo 'Probíhá'.

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.
    """
    ukoly = nacist_ukoly(conn)
    filtrovane = [u for u in ukoly if u[3] in ("Nezahájeno", "Probíhá")]

    if not filtrovane:
        print("ℹ️  Seznam je prázdný.")
    else:
        print("\n--- Aktivní úkoly ---")
        for id, nazev, popis, stav in filtrovane:
            print(f"ID: {id}, Název: {nazev}, Popis: {popis}, Stav: {stav}")

def aktualizovat_ukol(conn: MySQLConnection, id_ukolu: int, novy_stav: str) -> None:
    cursor = conn.cursor()
    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
    conn.commit()
    if cursor.rowcount == 0:
        cursor.close()
        raise Error(f"Úkol s ID {id_ukolu} neexistuje.")
    cursor.close()

def odstranit_ukol(conn: MySQLConnection, id_ukolu: int) -> None:
    """
    Odstraní úkol z tabulky 'ukoly' podle ID.

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.
        id_ukolu (int): ID úkolu, který má být odstraněn.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
    conn.commit()
    cursor.close()

def nacist_ukoly(conn: MySQLConnection) -> list[tuple]:
    """
    Načete všechny úkoly z tabulky 'ukoly' v databázi.

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.

    Returns:
        list[tuple]: Seznam úkolů jako n-tice (id, nazev, popis, stav).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, nazev, popis, stav FROM ukoly")
    vysledky = cursor.fetchall()
    cursor.close()
    return vysledky

def hlavni_menu(conn: MySQLConnection) -> None:
    """
    Zobrazí hlavní menu pro správu úkolů:
    1. Přidat úkol
    2. Zobrazit úkoly
    3. Aktualizovat úkol
    4. Odstranit úkol
    5. Ukončit program

    Args:
        conn (MySQLConnection): Aktivní připojení k databázi.
    """
    while True:
        print("\n===== SPRÁVCE ÚKOLŮ =====")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("Vyberte akci: ")

        if volba == "1":
            nazev = input("Zadejte název úkolu: ").strip()
            popis = input("Zadejte popis úkolu: ").strip()
            if nazev and popis:
                pridat_ukol(conn, nazev, popis)
                print("✅ Úkol byl přidán.")
            else:
                print("❌ Název i popis jsou povinné.")

        elif volba == "2":
            zobrazit_ukoly(conn)

        elif volba == "3":
            ukoly = nacist_ukoly(conn)
            for id, nazev, _, stav in ukoly:
                print(f"ID: {id}, Název: {nazev}, Stav: {stav}")
            try:
                id_ukolu = int(input("Zadejte ID úkolu k aktualizaci: "))
                if not any(u[0] == id_ukolu for u in ukoly):
                    print("❌ Útol s daným ID neexistuje.")
                    continue
                print("Zvolte nový stav: \n 1. Probíhá\n 2. Hotovo")
                stav_volba = input("Volba: ")
                if stav_volba == "1":
                    novy_stav = "Probíhá"
                elif stav_volba == "2":
                    novy_stav = "Hotovo"
                else:
                    print("❌ Neplatná volba stavu.")
                    continue
                aktualizovat_ukol(conn, id_ukolu, novy_stav)
                print("✅ Útol byl aktualizován.")
            except ValueError:
                print("❌ Neplatné ID.")

        elif volba == "4":
            ukoly = nacist_ukoly(conn)
            for id, nazev, _, stav in ukoly:
                print(f"ID: {id}, Název: {nazev}, Stav: {stav}")
            try:
                id_ukolu = int(input("Zadejte ID úkolu k odstranění: "))
                if not any(u[0] == id_ukolu for u in ukoly):
                    print("❌ Útol s daným ID neexistuje.")
                    continue
                odstranit_ukol(conn, id_ukolu)
                print("✅ Útol byl odstraněn.")
            except ValueError:
                print("❌ Neplatné ID.")

        elif volba == "5":
            print("👋 Ukončuji správce úkolů.")
            break

        else:
            print("❌ Neplatná volba, zkuste to znovu.")

if __name__ == "__main__":
    vytvoreni_db()
    conn = pripojeni_db()
    if conn:
        vytvoreni_tabulky(conn)
        hlavni_menu(conn)

        conn.close()
