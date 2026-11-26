
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, date
from pathlib import Path

# ARXIU XML
CARPETA = Path(__file__).resolve().parent
ARXIU_XML = CARPETA / "incidencies.xml"


# COLORS PER A LA TERMINAL
BLAU = "\033[96m"
VERD = "\033[92m"
TARONJA = "\033[93m"
VERMELL = "\033[91m"
BLANC = "\033[97m"
GRIS = "\033[90m"
RESET = "\033[0m"


# 1. LLEGIR LES INCIDÈNCIES

def llegir_incidencies():
    """Llegeix les incidències del fitxer XML."""

    arbre = ET.parse(ARXIU_XML)
    arrel = arbre.getroot()

    incidencies = []

    for incidencia in arrel.findall("incidencia"):

        dades = {}

        for camp in incidencia.findall("camp"):
            nom = camp.get("nom")
            valor = (camp.text or "").strip()

            dades[nom] = valor

        incidencies.append(dades)

    return incidencies


# 2. FILTRAR LES DADES INCORRECTES

def filtrar_incidencies(incidencies):
    """Elimina els registres incorrectes o incomplets."""

    valides = []
    descartades = 0

    camps_obligatoris = [
        "Data de la incidència",
        "Tipus d'incidència",
        "Nivell d'urgència",
        "Ubicació (aula, laboratori, despatx, biblioteca…)",
        "Descripció detallada de la incidència"
    ]

    urgencies_valides = ["Baix", "Mitjà", "Alt"]

    for incidencia in incidencies:

        # Comprovar camps buits
        if any(not incidencia.get(camp, "")
               for camp in camps_obligatoris):

            descartades += 1
            continue

        # Comprovar que la data sigui correcta
        try:
            data = datetime.strptime(
                incidencia["Data de la incidència"],
                "%d/%m/%Y"
            ).date()

        except ValueError:
            descartades += 1
            continue

        # Descartar dates futures
        if data > date.today():
            descartades += 1
            continue

        # Comprovar urgència
        if incidencia["Nivell d'urgència"] not in urgencies_valides:
            descartades += 1
            continue

        valides.append(incidencia)

    return valides, descartades


# 3. MOSTRAR ESTADÍSTIQUES

def mostrar_estadistiques(incidencies, descartades, total):

    print("\n" + BLAU + "=" * 55 + RESET)
    print(BLANC + "             INFORME D'INCIDÈNCIES" + RESET)
    print(BLAU + "=" * 55 + RESET)

    print(f"\nTotal de registres: {total}")
    print(f"Incidències vàlides: {len(incidencies)}")
    print(f"Registres descartats: {descartades}")

    if total > 0:
        percentatge = descartades / total * 100
        print(f"Percentatge descartat: {percentatge:.2f}%")

    if not incidencies:
        print("\nNo hi ha incidències vàlides per analitzar.")
        return

    # 1. Incidències per tipus

    print("\n--- INCIDÈNCIES PER TIPUS ---")

    tipus = Counter(
        i["Tipus d'incidència"] for i in incidencies
    )

    for nom, quantitat in tipus.most_common():
        print(f"{nom:<45} {quantitat:>4}")

    # 2. Incidències per urgència

    print("\n--- INCIDÈNCIES PER URGÈNCIA ---")

    urgencies = Counter(
        i["Nivell d'urgència"] for i in incidencies
    )

    for nivell in ["Alt", "Mitjà", "Baix"]:
        print(f"{nivell:<15} {urgencies[nivell]:>4}")

    # 3. Incidències per ubicació

    print("\n--- INCIDÈNCIES PER UBICACIÓ ---")

    ubicacions = Counter(
        i["Ubicació (aula, laboratori, despatx, biblioteca…)"]
        for i in incidencies
    )

    for lloc, quantitat in ubicacions.most_common():
        print(f"{lloc:<35} {quantitat:>4}")

    # 4. Incidències per curs o departament

    print("\n--- INCIDÈNCIES PER CURS O DEPARTAMENT ---")

    grups = Counter(
        i["Curs i grup (alumnat) / Departament o àrea (personal)"]
        for i in incidencies
        if i.get(
            "Curs i grup (alumnat) / Departament o àrea (personal)"
        )
    )

    for grup, quantitat in grups.most_common():
        print(f"{grup:<35} {quantitat:>4}")

    # 5. Afectació de l'activitat

    print("\n--- AFECTACIÓ DE L'ACTIVITAT ---")

    camp = (
        "La incidència us impedeix desenvolupar la vostra activitat?"
    )

    afectacio = Counter(
        i[camp] for i in incidencies
        if i.get(camp)
    )

    for resposta, quantitat in afectacio.most_common():
        print(f"{resposta:<25} {quantitat:>4}")

    print("\n" + BLAU + "=" * 55 + RESET)
    print(BLANC + "                FI DE L'INFORME" + RESET)
    print(BLAU + "=" * 55 + RESET)


# 4. GENERAR GRÀFICS A LA TERMINAL

def generar_grafics(incidencies):

    def mostrar_barres(titol, dades, color):

        print("\n" + BLANC + "=" * 65 + RESET)
        print(BLAU + f"  {titol}" + RESET)
        print(GRIS + "-" * 65 + RESET)

        if not dades:
            print("  No hi ha dades disponibles.")
            return

        max_valor = max(valor for _, valor in dades)

        for nom, valor in dades:

            longitud = int((valor / max_valor) * 30)

            barra = "█" * longitud

            print(f"\n  {nom[:30]:<30}")

            print(
                f"  {color}{barra}{RESET} "
                f"{BLANC}{valor}{RESET}"
            )

        print()

    if not incidencies:
        print("No hi ha dades per representar.")
        return

    print("\n")
    print(BLAU + "=" * 65 + RESET)
    print(BLANC + "          INFORME VISUAL D'INCIDÈNCIES" + RESET)
    print(BLAU + "=" * 65 + RESET)

    # 1. INCIDÈNCIES PER TIPUS

    tipus = Counter(
        i["Tipus d'incidència"] for i in incidencies
    )

    mostrar_barres(
        "1. INCIDÈNCIES PER TIPUS (TOP 10)",
        tipus.most_common(10),
        BLAU
    )

    # 2. DISTRIBUCIÓ PER URGÈNCIA

    urgencies = Counter(
        i["Nivell d'urgència"] for i in incidencies
    )

    dades_urgencia = [
        ("Urgència alta", urgencies["Alt"]),
        ("Urgència mitjana", urgencies["Mitjà"]),
        ("Urgència baixa", urgencies["Baix"])
    ]

    mostrar_barres(
        "2. DISTRIBUCIÓ PER URGÈNCIA",
        dades_urgencia,
        VERMELL
    )

    # 3. EVOLUCIÓ MENSUAL

    mesos = Counter()

    for i in incidencies:

        try:
            data = datetime.strptime(
                i["Data de la incidència"],
                "%d/%m/%Y"
            )

            mes = data.strftime("%m/%Y")
            mesos[mes] += 1

        except (ValueError, KeyError):
            continue

    ordre = sorted(
        mesos,
        key=lambda m: datetime.strptime(m, "%m/%Y")
    )

    dades_mensuals = [
        (mes, mesos[mes]) for mes in ordre
    ]

    mostrar_barres(
        "3. EVOLUCIÓ MENSUAL",
        dades_mensuals,
        VERD
    )

    # 4. UBICACIONS AMB MÉS INCIDÈNCIES

    ubicacions = Counter(
        i["Ubicació (aula, laboratori, despatx, biblioteca…)"]
        for i in incidencies
    )

    mostrar_barres(
        "4. UBICACIONS AMB MÉS INCIDÈNCIES (TOP 8)",
        ubicacions.most_common(8),
        BLAU
    )

    # 5. AFECTACIÓ DE L'ACTIVITAT

    camp = (
        "La incidència us impedeix desenvolupar la vostra activitat?"
    )

    afectacio = Counter(
        i[camp] for i in incidencies
        if i.get(camp)
    )

    mostrar_barres(
        "5. AFECTACIÓ DE L'ACTIVITAT",
        afectacio.most_common(),
        TARONJA
    )

    print(BLAU + "=" * 65 + RESET)
    print(BLANC + "          FI DE L'INFORME VISUAL" + RESET)
    print(BLAU + "=" * 65 + RESET)


# 5. PROGRAMA PRINCIPAL

def main():

    try:
        incidencies = llegir_incidencies()

        valides, descartades = filtrar_incidencies(incidencies)

        mostrar_estadistiques(
            valides,
            descartades,
            len(incidencies)
        )

        generar_grafics(valides)

    except FileNotFoundError:
        print(VERMELL + "ERROR: No s'ha trobat incidencies.xml." + RESET)

    except ET.ParseError:
        print(VERMELL + "ERROR: El fitxer XML no té un format correcte." + RESET)

    except OSError as error:
        print(VERMELL + "ERROR: " + str(error) + RESET)


if __name__ == "__main__":
    main()
