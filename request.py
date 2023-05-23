import os
import requests
import datetime
import time
import sys
import feedparser
from bs4 import BeautifulSoup
import concurrent.futures


while True:
    print("Actualizando...")

    def descarga_medios(url):
        try: 
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                
                nombre_archivo = url.split('/')[-1]
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh-%Mm") 
                ruta_con_timestamp = f"result/{timestamp}/"

                if not os.path.exists(ruta_con_timestamp):
                    os.makedirs(ruta_con_timestamp)

                ruta_archivo = os.path.join(f"result/{timestamp}/", nombre_archivo)
                with open(ruta_archivo, 'wb') as file:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            progress = int((downloaded_size/total_size) * 50)
                            sys.stdout.write("\r")
                            sys.stdout.write("[{}{}] {}%".format('=' * progress, ' ' * (50 - progress), progress * 2))
                            sys.stdout.flush()
                sys.stdout.write("\nArchivo descargado: {} bytes:{}\n".format(nombre_archivo,total_size))                 
            else:
                sys.stdout.write("\nError en la descarga de: {}\n".format(url))

        except Exception as e:
            print("Error inesperado", str(e))


    def busca_reciente(url_dir):
        try:
            response = requests.get(url_dir)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                lista_archivos = []
                for enlace in soup.find_all('a'):
                    if enlace.name == 'a':
                        href = enlace.get('href')
                        lista_archivos.append(href)
                if lista_archivos:
                    archivo_mas_reciente = max(lista_archivos)
                    url_archivo = url_dir + archivo_mas_reciente
                    descarga_medios(url_archivo)
                else:
                    print("No se pudo obtener el archivo mas reciente")
            else:
                print(f"La peticion termino con error {response.status_code} ")
        except Exception as e:
            print("Error inesperado", str(e))
    
    def sasmex_feed():
        try:
            response = requests.get("https://sasmex.net/rss/sasmex.xml")
            if response.status_code == 200:
                xml_content = response.content.decode('utf-8')
                feed = feedparser.parse(xml_content)
                sys.stdout.write("\n {} \n Actualizado: {} \n".format(
                    feed.feed.subtitle,
                    feed.feed.updated
                    ))
                for entry in feed.entries:
                    sys.stdout.write(
                    "\n id: {} \n Actualizado: {} \n Titulo: {} \n Summary: {} \n"
                    .format(
                    entry.id,
                    entry.updated,
                    entry.title,
                    entry.summary
                    ))
            else:
                print(f"Error al obtener el feed{response.status_code}")
        except Exception as e:
            print("Error inesperado", str(e))



    url_directorios = [
        ("https://www.cenapred.unam.mx/es/RegistrosVolcanPopo/helibanda/Tetexcaloc/"),
        ("https://www.cenapred.unam.mx/es/RegistrosVolcanPopo/helibanda/Atlixco/")
    ]
    url_medios = [
        ("http://www.ssn.unam.mx/recursos/imagenes/sismogramas/sismogramaPP.gif"),
        ("https://www.cenapred.unam.mx/images/imgVolcanPopocatepetl-Juncos.jpg"),
        ("https://www.cenapred.unam.mx/volcan/popocatepetl/imagenes/hd/imgVolcanPopocatepetl-AltzomoniHD.jpg"),
        ("https://www.cenapred.unam.mx/volcan/popocatepetl/imagenes/hd/imgVolcanPopocatepetl-TlamacasHD.jpg"),
        ("https://www.cenapred.unam.mx/volcan/popocatepetl/imagenes/hd/imgVolcanPopocatepetl-TianguismanalcoHD.jpg"),
    ]   
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for url_dir in url_directorios:
            executor.map(busca_reciente(url_dir))
        for url in url_medios:
            executor.map(descarga_medios(url))    

    sasmex_feed()
    sys.stdout.write("\nCompleto!, Esperando 5 minutos.\n")
    time.sleep(300)  # 5 minutos

#Fuera de servicio
#https://sasmex.net/rss/sasmex.xml