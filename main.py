from lib.db import db
import smtplib
import os
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open(os.path.join("data/products", "pilona.txt")) as f:
    productos_pilona = f.read().splitlines()

with open(os.path.join("data/products", "poli.txt")) as f:
    productos_poli = f.read().splitlines()

def check_prices():
    pass

def send_email_poli():
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

def send_email_pilona():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('pilar.vasquez.h@gmail.com', 'rmighwhbizgtfvpv')

    subject = "Prueba Pilona"
    body = "lalala"
    msg = f"Subject:{subject}\n\n{body}"

    server.sendmail('pilar.vasquez.h@gmail.com', 'pilar.vasquez.h@gmail.com', msg)

    server.quit()

def main():
    while True:
        check_prices()
        time.sleep(60)

if __name__ == "__main__":
	main()
