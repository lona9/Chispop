from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from requests_html import AsyncHTMLSession

with open(os.path.join("data/products", "pokemon.txt")) as f:
    productos = f.read().splitlines()

async def session(link):
    asession = AsyncHTMLSession()
    r = await asession.get(link)

    ## zmart
    if "zmart" in link:
        info = check_zmart(r, link)
        return info

    elif "microplay" in link:
        info = check_microplay(r, link)
        return info

    elif "weplay" in link:
        info = check_weplay(r, link)
        return info

    elif "warpig" in link:
        info = check_warpig(r, link)
        return info

    elif "planetaloz" in link:
        info = check_planetaloz(r, link)
        return info

    elif "linio" in link:
        info = check_linio(r, link)
        return info

    elif "paris" in link:
        info = check_paris(r, link)
        return info

def check_zmart(r, link):
    div = r.html.find("div[id = 'PriceProduct']", first=True)
    div =  div.full_text.encode("ascii", "ignore")
    div = div.decode()

    precio = [x for x in div if x.isdigit()]
    precio = "".join(precio)
    precio = int(precio)

    print(link)

    try:
        status = r.html.find("div[class = 'txTituloRef']", first=True)
        status = status.full_text.encode("ascii", "ignore")
        status = status.decode()
        if "DISPONIBLE" in status or "EARLY" in status:
            status = "Disponible"
        else:
            status = "Agotado"
    except:
        status = r.html.find("div[class = 'txTituloRef dv260px']", first=True)
        status = status.full_text.encode("ascii", "ignore")
        status = status.decode()
        if "DISPONIBLE" in status or "EARLY" in status:
            status = "Disponible"
        else:
            status = "Agotado"

    info = [precio, status]

    return info

def check_microplay(r, link):
    ''''
    checks microplay
    ''''

    precio = r.html.find('script[type="text/javascript"]')[10].full_text
    precios = precio.splitlines()
    precio = [x for x in precios if 'price' in x]
    precio = precio[0].strip().split(',')[0]
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    status = "Disponible"
    info = [precio, status]

    return info

def check_weplay(r, link):
    precio = r.html.find('span[class = "price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    status = "Disponible"
    info = [precio, status]

    return info

def check_planetaloz(r, link):

    precio = r.html.find('span[itemprop="price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    status = "Disponible"
    info = [precio, status]

    return info

def check_linio(r, link):
    nombre = r.html.find('title', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()
    nombre = nombre.split('|')[0].strip()

    precio = r.html.find('span[class = "price-main-md"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    status = "Disponible"
    info = [precio, status]

    return info


def check_paris(r, link):
    nombre = r.html.find('span[class="breadcrumb-element"]', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()

    precio = r.html.find('span[itemprop="price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    status = "Disponible"
    info = [precio, status]

    return info

def set_initial_prices(productos_totales):
    db.autosave(AsyncIOScheduler())

    precios = []
    statuses = []

    for link in productos:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))
        precio = info[0]
        status = info[1]
        precios.append(precio)
        statuses.append(status)

    precios_iterator = zip(productos_totales, precios)
    precios_dict = dict(precios_iterator)
    status_iterator = zip(productos_totales, statuses)
    statuses_dict = dict(status_iterator)


    db.multiexec("INSERT OR IGNORE INTO precio (ProductID) VALUES (?)",
				((link,) for link in productos_totales))

    for key, value in precios_dict.items():
        db.execute("UPDATE precio SET PrecioInicial = ? WHERE ProductID = ?", value, key)

    for key, value in statuses_dict.items():
        db.execute("UPDATE precio SET Status = ? WHERE ProductID = ?", value, key)

    to_remove = []

    stored_productos = db.column("SELECT ProductID FROM precio")

    for producto in stored_productos:
      if producto not in productos:
        to_remove.append(producto)

    db.multiexec("DELETE FROM precio WHERE ProductID = ?",
					 ((producto,) for producto in to_remove))

    db.commit()

def main():
    while True:
        set_initial_prices(productos)
        print("listo!")
        return

if __name__ == "__main__":
	main()
