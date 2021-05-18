from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open(os.path.join("data/products", "pilona.txt")) as f:
    productos_pilona = f.read().splitlines()

with open(os.path.join("data/products", "poli.txt")) as f:
    productos_poli = f.read().splitlines()

productos_totales = productos_poli + productos_pilona

def set_initial_prices(productos_totales):
    db.autosave(AsyncIOScheduler())

    db.multiexec("INSERT OR IGNORE INTO precio (ProductoID) VALUES (?)",
				(hola for hola in lista))

    to_remove = []
    stored_members = db.column("SELECT ProductoID FROM precio")
    for producto in stored_members:
      if producto not in lista:
        to_remove.append(producto)

    db.multiexec("DELETE FROM exp WHERE UserID = ?",
					 (producto for producto in to_remove))

    db.commit()

def main():
    while True:
        set_initial_prices()

if __name__ == "__main__":
	main()
