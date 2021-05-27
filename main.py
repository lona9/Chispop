from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from requests_html import AsyncHTMLSession
import asyncio

with open(os.path.join("data/products", "pilona.txt"), encoding='utf-8') as f:
    productos_pilona = f.read().splitlines()

with open(os.path.join("data/products", "poli.txt"), encoding='utf-8') as f:
    productos_poli = f.read().splitlines()

with open(os.path.join("data/products", "pala.txt"), encoding='utf-8') as f:
    productos_pala = f.read().splitlines()

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

    nombre = r.html.find("title", first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()
    nombre = nombre[:-11]

    tienda = "Zmart.cl"

    info = [nombre, precio, tienda]

    return info

def check_microplay(r, link):
    nombre = r.html.find("h1", first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()
    nombre = nombre.strip()

    precio = r.html.find('script[type="text/javascript"]')[10].full_text
    precios = precio.splitlines()
    precio = [x for x in precios if 'price' in x]
    precio = precio[0].strip().split(',')[0]
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    tienda = "Microplay"

    info = [nombre, precio, tienda]

    return info

def check_weplay(r, link):
    nombre = r.html.find('title', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()

    precio = r.html.find('span[class = "price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    tienda = "WePlay"

    info = [nombre, precio, tienda]

    return info

def check_warpig(r, link):
    nombre = r.html.find('title', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()
    nombre = nombre[:-15]

    precio = r.html.find('span[data-bs="product.finalPrice"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    tienda = "Warpig Games"

    info = [nombre, precio, tienda]

    return info

def check_planetaloz(r, link):
    nombre = r.html.find('title', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()

    precio = r.html.find('span[itemprop="price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    tienda = "Planeta LoZ"

    info = [nombre, precio, tienda]

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

    tienda = "Linio"

    info = [nombre, precio, tienda]

    return info

def check_paris(r, link):
    nombre = r.html.find('span[class="breadcrumb-element"]', first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()

    precio = r.html.find('span[itemprop="price"]', first=True)
    precio = precio.full_text
    precio = [x for x in precio if x.isdigit()]
    precio = int("".join(precio))

    tienda = "Paris"

    info = [nombre, precio, tienda]

    return info

def check_prices():
    for link in productos_pilona:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))

        nombre = info[0]
        precio = info[1]
        tienda = info[2]

        precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

        if precio_inicial[0] > precio:
            send_email_pilona(nombre, precio_inicial[0], precio, tienda, link)
        else:
            pass

    for link in productos_poli:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))

        nombre = info[0]
        precio = info[1]
        tienda = info[2]

        precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

        if precio_inicial[0] > precio:
            send_email_poli(nombre, precio_inicial[0], precio, tienda, link)
        else:
            pass

    for link in productos_pali:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))

        nombre = info[0]
        precio = info[1]
        tienda = info[2]

        precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

        if precio_inicial[0] > precio:
            send_email_pala(nombre, precio_inicial[0], precio, tienda, link)
        else:
            pass

def send_email_poli(nombre, precio_inicial, precio, tienda, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('chispopalertas@gmail.com', 'ysooqeblypsipibh')

    subject = f"Poli: El precio de {nombre} en {tienda} ha cambiado"
    body = f"El precio de {nombre} en {tienda} ha cambiado de ${precio_inicial} a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('chispopalertas@gmail.com', 'poliarriagadac@gmail.com', msg)

    server.quit()

def send_email_pilona(nombre, precio_inicial, precio, tienda, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('chispopalertas@gmail.com', 'ysooqeblypsipibh')

    subject = f"Pilona: El precio de {nombre} en {tienda} ha cambiado"
    body = f"El precio de {nombre} en {tienda} ha cambiado de ${precio_inicial} a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('chispopalertas@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    server.quit()

def send_email_pala(nombre, precio_inicial, precio, tienda, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('chispopalertas@gmail.com', 'ysooqeblypsipibh')

    subject = f"Paula: El precio de {nombre} en {tienda} ha cambiado"
    body = f"El precio de {nombre} en {tienda} ha cambiado de ${precio_inicial} a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('chispopalertas@gmail.com', 'paula.vash@gmail.com', msg)

    server.quit()

def main():
    while True:
        check_prices()
        time.sleep(43200)

if __name__ == "__main__":
	main()
