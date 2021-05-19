from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from requests_html import AsyncHTMLSession
import asyncio

with open(os.path.join("data/products", "pilona.txt"), encoding='utf-8') as f:
    productos_pilona = f.read().splitlines()
    print(productos_pilona)

with open(os.path.join("data/products", "poli.txt"), encoding='utf-8') as f:
    productos_poli = f.read().splitlines()

async def session(link):
    asession = AsyncHTMLSession()
    r = await asession.get(link)

    ## zmart
    if "zmart" in link:
        div = r.html.find("div[id = 'PriceProduct']", first=True)
        div =  div.full_text.encode("ascii", "ignore")
        div = div.decode()

        precio = [x for x in div if x.isdigit()]
        precio = "".join(precio)
        precio = int(precio)

        nombre = r.html.find("title", first=True)
        nombre = nombre.full_text.encode("ascii", "ignore")
        nombre = nombre.decode()

        info = [nombre, precio]
        print(nombre, precio)
        print(type(nombre), type(precio))

    return info

def check_prices():
    for link in productos_pilona:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))

        nombre = info[0]
        precio = info[1]

        precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

        if precio_inicial[0] < 40000:
            send_email_pilona(nombre, precio)
        else:
            send_email_pilona("han pasado 12 horas", "12 horas")

    for link in productos_poli:
        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(session(link))

        nombre = info[0]
        precio = info[1]

        precio_inicial = db.record("SELECT PrecioInicial FROM precio WHERE ProductID = ?", link)

        if precio_inicial[0] < 40000:
            send_email_poli(nombre, precio)
        else:
            send_email_poli("poli 12 horas", "12 horas")

def send_email_poli(nombre, precio):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('pilar.vasquez.h@gmail.com', 'rmighwhbizgtfvpv')

    subject = "Prueba Poli"
    body = "lalala"
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('pilar.vasquez.h@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    server.quit()

def send_email_pilona(nombre, precio):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('pilar.vasquez.h@gmail.com', 'rmighwhbizgtfvpv')

    subject = nombre
    body = f"El producto {nombre} cuesta ${precio} actualmente."
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('pilar.vasquez.h@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    server.quit()

def main():
    while True:
        check_prices()
        time.sleep(43200)

if __name__ == "__main__":
	main()
