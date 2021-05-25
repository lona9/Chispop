from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from requests_html import AsyncHTMLSession

with open(os.path.join("data/products", "pilona.txt")) as f:
    productos_pilona = f.read().splitlines()

with open(os.path.join("data/products", "poli.txt")) as f:
    productos_poli = f.read().splitlines()

with open(os.path.join("data/products", "pala.txt")) as f:
    productos_pala = f.read().splitlines()

productos_totales = productos_poli + productos_pilona + productos pala

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

def check_zmart(r, link):
    div = r.html.find("div[id = 'PriceProduct']", first=True)
    div =  div.full_text.encode("ascii", "ignore")
    div = div.decode()

    precio = [x for x in div if x.isdigit()]
    precio = "".join(precio)
    precio = int(precio)

    info = precio

    return info

def check_microplay(r, link):

    precio = r.html.find('script[type="text/javascript"]')[10].full_text
    precios = precio.splitlines()
    precio = [x for x in precios if 'price' in x]
    precio = precio[0].strip().split(',')[0]
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    info = precio

    return info

def check_weplay(r, link):
    precio = r.html.find('span[class = "price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    info = precio

    return info

def check_warpig(r, link):

    precio = r.html.find('span[data-bs="product.finalPrice"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    info = precio

    return info

def check_planetaloz(r, link):

    precio = r.html.find('span[itemprop="price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    info = precio

    return info

def set_initial_prices(productos_totales):
    db.autosave(AsyncIOScheduler())

    precios = []

    for link in productos_totales:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))
        precio = info
        precios.append(precio)

    zip_iterator = zip(productos_totales, precios)
    product_dict = dict(zip_iterator)
    print(product_dict)

    db.multiexec("INSERT OR IGNORE INTO precio (ProductID) VALUES (?)",
				((link,) for link in productos_totales))

    for key, value in product_dict.items():
        db.execute("UPDATE precio SET PrecioInicial = ? WHERE ProductID = ?", value, key)

    to_remove = []

    stored_productos = db.column("SELECT ProductID FROM precio")

    for producto in stored_productos:
      if producto not in productos_totales:
        to_remove.append(producto)

    db.multiexec("DELETE FROM precio WHERE ProductID = ?",
					 ((producto,) for producto in to_remove))

    db.commit()

def main():
    while True:
        set_initial_prices(productos_totales)
        print("listo!")
        return

if __name__ == "__main__":
	main()
