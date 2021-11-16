from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from requests_html import AsyncHTMLSession
import asyncio

with open(os.path.join("data/products", "pokemon.txt"), encoding='utf-8') as f:
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

    nombre = r.html.find("title", first=True)
    nombre = nombre.full_text.encode("ascii", "ignore")
    nombre = nombre.decode()
    nombre = nombre[:-11]

    tienda = "Zmart.cl"

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
    print(status)

    info = [nombre, precio, tienda, status]

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

    status = "Disponible"

    info = [nombre, precio, tienda, status]

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
    status = "Disponible"

    info = [nombre, precio, tienda, status]

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
    status = "Disponible"

    info = [nombre, precio, tienda, status]

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
    status = "Disponible"

    info = [nombre, precio, tienda, status]

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
    status = "Disponible"

    info = [nombre, precio, tienda, status]

    return info

def check_prices():
    for link in productos:
        try:
            loop = asyncio.get_event_loop()
            info = loop.run_until_complete(session(link))
            print(link)

            nombre = info[0]
            precio = info[1]
            tienda = info[2]
            status = info[3]

            precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

            status_inicial = db.record("SELECT Status FROM precio WHERE ProductID = ?", link)

            if precio_inicial[0] > precio:
                send_email(nombre, precio_inicial[0], precio, tienda, link)
                db.execute("UPDATE precio SET PrecioInicial = ? WHERE ProductID = ?", precio, link)
                db.commit()
            else:
                pass

            if status_inicial[0] != status:
                print("distintos!")
                db.execute("UPDATE precio SET Status = ? WHERE ProductID = ?", status, link)
                db.commit()

                if status == "Disponible":
                    send_email_stock(nombre, precio, tienda, link)

            else:
                pass

        except:
            pass


def send_email(nombre, precio_inicial, precio, tienda, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('chispopalertas@gmail.com', 'ysooqeblypsipibh')

    subject = f"Pilona: El precio de {nombre} en {tienda} ha cambiado"
    body = f"El precio de {nombre} en {tienda} ha cambiado de ${precio_inicial} a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"
    server.sendmail('chispopalertas@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    subject = f"Nico: {nombre} en {tienda} de nuevo en stock!"
    body = f"{nombre} en {tienda} se encuentra de nuevo en stock a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"
    server.sendmail('chispopalertas@gmail.com', 'nicolascarrillovergara@gmail.com', msg)

    server.quit()

def send_email_stock(nombre, precio, tienda, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('chispopalertas@gmail.com', 'ysooqeblypsipibh')

    subject = f"Pilona: {nombre} en {tienda} de nuevo en stock!"
    body = f"{nombre} en {tienda} se encuentra de nuevo en stock a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"
    server.sendmail('chispopalertas@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    subject = f"Nico: {nombre} en {tienda} de nuevo en stock!"
    body = f"{nombre} en {tienda} se encuentra de nuevo en stock a ${precio}.\nRevisa en {link}"
    msg = f"Subject:{subject}\n\n{body}"
    server.sendmail('chispopalertas@gmail.com', 'nicolascarrillovergara@gmail.com', msg)

    server.quit()

def main():
    while True:
        check_prices()
        time.sleep(10800)

if __name__ == "__main__":
	main()
