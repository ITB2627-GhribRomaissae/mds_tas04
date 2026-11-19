
# ==========================================
# CONVERSOR CSV A XML
# Ejercicio 2 - TA04_XML
# ==========================================

import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import os
import sys

# Obtener automáticamente la carpeta donde está este programa
CARPETA = Path(__file__).resolve().parent

# Nombre del archivo XML de salida
ARCHIVO_XML = CARPETA / "incidencies.xml"

# Mostrar información inicial
print("=" * 50)
print("       CONVERSOR DE CSV A XML")
print("=" * 50)
print("Carpeta de trabajo:", CARPETA)
print()
def limpiar_xml(texto):
    """Elimina caracteres no permitidos en XML 1.0."""

    texto = str(texto)

    return "".join(
        caracter for caracter in texto
        if (
            caracter in "\t\n\r"
            or 0x20 <= ord(caracter) <= 0xD7FF
            or 0xE000 <= ord(caracter) <= 0xFFFD
            or 0x10000 <= ord(caracter) <= 0x10FFFF
        )
    )
def buscar_archivo_csv():
    """Busca archivos CSV en la carpeta del programa."""

    archivos = list(CARPETA.glob("*.csv"))

    if not archivos:
        print("ERROR: No se ha encontrado ningún archivo CSV.")
        return None

    if len(archivos) == 1:
        return archivos[0]

    print("Se han encontrado varios archivos CSV:")
    
    for numero, archivo in enumerate(archivos, start=1):
        print(f"{numero}. {archivo.name}")

    while True:
        opcion = input("Selecciona el número del archivo: ")

        try:
            numero = int(opcion)

            if 1 <= numero <= len(archivos):
                return archivos[numero - 1]

            print("ERROR: Número fuera de rango.")

        except ValueError:
            print("ERROR: Introduce un número válido.")

def leer_csv(archivo_csv):
    """Lee el CSV detectando codificacion y separador."""

    codificaciones = ["utf-8-sig", "cp1252", "latin-1"]

    for codificacion in codificaciones:

        try:
            with open(
                archivo_csv,
                "r",
                encoding=codificacion,
                newline=""
            ) as archivo:

                muestra = archivo.read(8192)

                if not muestra.strip():
                    print("ERROR: El archivo CSV esta vacio.")
                    return None

                archivo.seek(0)

                try:
                    dialecto = csv.Sniffer().sniff(
                        muestra,
                        delimiters=",;\t|"
                    )
                except csv.Error:
                    print("AVISO: No se detecto el separador.")
                    dialecto = csv.excel
                    dialecto.delimiter = ","

                lector = csv.reader(archivo, dialecto)

                encabezados = next(lector, None)

                if not encabezados:
                    print("ERROR: No hay encabezados.")
                    return None

                encabezados = [
                    campo.strip() for campo in encabezados
                ]

                if any(not campo for campo in encabezados):
                    print("ERROR: Hay encabezados vacios.")
                    return None

                if len(encabezados) != len(set(encabezados)):
                    print("ERROR: Hay encabezados duplicados.")
                    return None

                filas = []

                for numero, fila in enumerate(lector, start=2):

                    if not any(valor.strip() for valor in fila):
                        continue

                    if len(fila) != len(encabezados):
                        print(
                            f"AVISO: Fila {numero} incorrecta. "
                            "Se omitira."
                        )
                        continue

                    filas.append(fila)

                if not filas:
                    print("ERROR: No hay registros validos.")
                    return None

                return encabezados, filas

        except UnicodeDecodeError:
            continue

        except OSError as error:
            print("ERROR al leer el archivo:", error)
            return None

    print("ERROR: No se reconoce la codificacion del archivo.")
    return None


def convertir_csv_xml():
    """Convierte un archivo CSV en XML de forma segura."""

    print("=" * 55)
    print("          CONVERSOR DE CSV A XML")
    print("=" * 55)

    temporal = None

    try:
        # 1. Buscar el archivo CSV
        archivo_csv = buscar_archivo_csv()

        if archivo_csv is None:
            print("ERROR: No se ha seleccionado ningún CSV.")
            return

        # 2. Leer y validar el contenido
        resultado = leer_csv(archivo_csv)

        if resultado is None:
            print("ERROR: No se ha podido leer el CSV.")
            return

        encabezados, filas = resultado

        if not encabezados or not filas:
            print("ERROR: El CSV no contiene datos válidos.")
            return

        # 3. Crear la estructura XML
        raiz = ET.Element("incidencies")

        for numero, fila in enumerate(filas, start=1):

            incidencia = ET.SubElement(raiz, "incidencia")

            for campo, valor in zip(encabezados, fila):

                elemento = ET.SubElement(
                    incidencia, "camp"
                )

                elemento.set("nom", limpiar_xml(campo))
                elemento.text = limpiar_xml(valor)

        # 4. Formatear el XML
        arbol = ET.ElementTree(raiz)
        ET.indent(arbol, space="  ")

        # 5. Crear archivo temporal en la misma carpeta
        with tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            dir=CARPETA,
            suffix=".tmp"
        ) as archivo_temporal:

            temporal = Path(archivo_temporal.name)

        # 6. Guardar el XML temporal
        arbol.write(
            temporal,
            encoding="utf-8",
            xml_declaration=True
        )

        # 7. Comprobar que el XML es válido
        ET.parse(temporal)

        # 8. Sustituir el XML anterior de forma segura
        os.replace(temporal, ARCHIVO_XML)

        temporal = None

        print("\nCONVERSION CORRECTA")
        print("Archivo utilizado:", archivo_csv.name)
        print("Incidencias convertidas:", len(filas))
        print("Archivo generado:", ARCHIVO_XML.name)

    except (OSError, ET.ParseError, ValueError) as error:
        print("ERROR:", error)
        print("No se ha podido completar la conversión.")

    except Exception as error:
        print("ERROR INESPERADO:", type(error).__name__)
        print(error)

    finally:
        # 9. Limpiar archivo temporal si quedó pendiente
        if temporal is not None:
            try:
                temporal.unlink(missing_ok=True)
            except OSError:
                print("AVISO: No se pudo eliminar el temporal.")


if __name__ == "__main__":
    convertir_csv_xml()

