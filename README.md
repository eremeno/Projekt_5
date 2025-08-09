# 🗂️ Správce úkolů s MySQL a pytest

Tento projekt slouží jako jednoduchý správce úkolů s podporou ukládání dat do MySQL databáze a pokrytím testy pomocí `pytest`. Cílem je procvičit práci s databázemi, psaní funkcí pro CRUD operace a jejich automatizované testování.

---

## 📁 
Struktura projektu
[[_TOC_]]

---

## 🛠️ Funkce

Projekt umožňuje:

- ✅ Přidávat úkoly do databáze
- 📝 Aktualizovat stav úkolu
- ❌ Odstraňovat úkoly
- 📄 Načítat a zobrazovat všechny úkoly

---

## 🧪 Testování

Pro testování slouží soubor `test_spravce_ukolu.py`, který pokrývá:

- **Přidání úkolu**
  - pozitivní (správná data)
  - negativní (prázdný název/popis)
- **Aktualizaci úkolu**
  - pozitivní (existující úkol)
  - negativní (neexistující ID)
- **Odstranění úkolu**
  - pozitivní (existující úkol)
  - negativní (neexistující ID)

Každý test využívá samostatnou testovací databázi `spravce_ukolu_test`, která je před a po každém testu vyčištěna pro zajištění izolace.

---

## 🧩 Závislosti

Nainstaluj pomocí:

```
pip install -r requirements.txt
```

requirements.txt obsahuje:
- mysql-connector-python
- pytest
- pytest-html

---

## ⚙️ Konfigurace MySQL

Ujisti se, že máš spuštěný MySQL server a dostupného uživatele `root` s heslem `1111`.

Projekt používá dvě databáze:
- spravce_ukolu (produkční)
- spravce_ukolu_test (pro testy)

---

## ▶️ Spuštění testů
Pro spuštění testů:
```
pytest
```
Výstupní HTML report najdeš jako `report.html` v kořenové složce projektu.

---

## 📌 Poznámky
Tabulka ukoly obsahuje sloupce:
- id (INT, AUTO_INCREMENT)
- nazev (VARCHAR)
- popis (VARCHAR)
- stav (ENUM)
- datum_vytvoreni (DATE)

Testy jsou odděleny od produkční databáze, aby nedošlo k nechtěné ztrátě dat.

---

## 📚 Autor
Tento projekt byl vytvořen jako součást výukového kurzu Python Akademie od Engeto.
