import xml.etree.ElementTree as ET
import json

from collections import Counter
from datetime import datetime, date
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box


# ==================================================
# CONFIGURACIÓ
# ==================================================

CARPETA = Path(__file__).resolve().parent

ARXIU_XML = CARPETA / "incidencies.xml"
ARXIU_JSON = CARPETA / "incidencies.json"

console = Console()

BLAU = "#38A9E8"
VERD = "#16A36A"
VERMELL = "#C52B32"
TARONJA = "#D88932"
GRIS = "#9299A3"


# ==================================================
# 1. LLEGIR LES INCIDÈNCIES
# ==================================================

def llegir_incidencies():

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


# ==================================================
# 2. FILTRAR LES DADES INCORRECTES
# ==================================================

def filtrar_incidencies(incidencies):

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

        # Comprovar data

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


# ==================================================
# 3. DESAR LES INCIDÈNCIES AL JSON
# ==================================================

def desar_incidencies_json(incidencies):

    # COMPROVAR SI EXISTEIX EL JSON

    if not ARXIU_JSON.exists():

        with open(ARXIU_JSON, "w", encoding="utf-8") as fitxer:

            json.dump(
                incidencies,
                fitxer,
                indent=4,
                ensure_ascii=False
            )

        console.print(
            Panel(
                f"[bold green]Fitxer incidencies.json creat correctament![/bold green]\n\n"
                f"Incidències desades: {len(incidencies)}",
                border_style=VERD
            )
        )

        console.input("\n[dim]Prem Enter per veure l'informe...[/dim]")
        return

    # EL FITXER JA EXISTEIX

    console.print()

    console.print(
        Panel(
            "[bold white]EL FITXER JSON JA EXISTEIX[/bold white]\n\n"
            "[cyan]1.[/cyan] Sobreescriure les dades existents\n"
            "[cyan]2.[/cyan] Afegir noves incidències sense duplicats",
            title="GESTIÓ DEL FITXER JSON",
            border_style=BLAU
        )
    )

    opcio = console.input(
        "\n[bold cyan]Selecciona una opció (1/2): [/bold cyan]"
    ).strip()

    # OPCIÓ 1: SOBREEESCRIURE

    if opcio == "1":

        with open(ARXIU_JSON, "w", encoding="utf-8") as fitxer:

            json.dump(
                incidencies,
                fitxer,
                indent=4,
                ensure_ascii=False
            )

        console.print(
            Panel(
                f"[bold green]Fitxer sobreescrit correctament![/bold green]\n\n"
                f"Incidències desades: {len(incidencies)}",
                border_style=VERD
            )
        )

        console.input("\n[dim]Prem Enter per veure l'informe...[/dim]")

    # OPCIÓ 2: AFEGIR NOVES INCIDÈNCIES

    elif opcio == "2":

        try:

            with open(ARXIU_JSON, "r", encoding="utf-8") as fitxer:

                existents = json.load(fitxer)

            if not isinstance(existents, list):

                console.print(
                    "[bold red]ERROR: El JSON existent no conté una llista d'incidències.[/bold red]"
                )

                return

        except json.JSONDecodeError:

            console.print(
                "[bold red]ERROR: El fitxer JSON no té un format correcte.[/bold red]"
            )

            return
        except UnicodeDecodeError as error:

            console.print(
                f"[bold red]ERROR:[/bold red] {error}"
            )

            return

        afegides = len(incidencies)
        existents.extend(incidencies)

        # Actualitzar el JSON

        with open(ARXIU_JSON, "w", encoding="utf-8") as fitxer:

            json.dump(
                existents,
                fitxer,
                indent=4,
                ensure_ascii=False
            )

        console.print(
            Panel(
                f"[bold green]Actualització completada![/bold green]\n\n"
                f"[green]Incidències afegides:[/green] {afegides}\n"
                f"[cyan]Total al JSON:[/cyan] {len(existents)}",
                title="RESULTAT DE L'ACTUALITZACIÓ",
                border_style=VERD
            )
        )

        console.input("\n[dim]Prem Enter per veure l'informe...[/dim]")

    else:

        console.print(
            "[bold red]Opció no vàlida. No s'han modificat les dades.[/bold red]"
        )


# ==================================================
# 4. ELEMENTS VISUALS
# ==================================================

def mostrar_capcalera():

    console.clear()

    console.print()

    console.print(
        Panel(
            Text.from_markup(
                "[bold white]ORIGEN[/bold white] "
                "[#38A9E8]|[/#38A9E8] "
                "[bold white]IT DATA ANALYTICS[/bold white]\n\n"
                "[bold white]ANÀLISI D'INCIDÈNCIES[/bold white]\n"
                "[#C5D8F0]SISTEMA DE GESTIÓ I ANÀLISI DE DADES[/#C5D8F0]"
            ),
            border_style=BLAU,
            box=box.ROUNDED,
            padding=(1, 2)
        )
    )


def mostrar_titol(numero, titol):

    console.print()

    console.rule(
        f"[bold {BLAU}]{numero} · {titol}[/bold {BLAU}]",
        style=BLAU
    )

    console.print()


def mostrar_targeta(titol, valor, color):

    return Panel(
        Text.from_markup(
            f"[white]{titol}[/white]\n\n"
            f"[bold white]{valor}[/bold white]"
        ),
        border_style=color,
        style=f"on {color}",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=True
    )


def mostrar_barres(titol, dades, color, limit=None):

    mostrar_titol("", titol)

    if not dades:

        console.print(
            Panel(
                "[dim]No hi ha dades disponibles.[/dim]",
                border_style=GRIS
            )
        )

        return

    if limit:

        dades = dades[:limit]

    max_valor = max(valor for _, valor in dades)

    taula = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1)
    )

    taula.add_column("CATEGORIA", ratio=2)
    taula.add_column("DISTRIBUCIÓ", ratio=4)
    taula.add_column(
        "TOTAL",
        justify="right",
        style="bold white"
    )

    for nom, valor in dades:

        longitud = int((valor / max_valor) * 30) if max_valor else 0

        barra = Text("█" * longitud, style=color)

        taula.add_row(
            nom,
            barra,
            str(valor)
        )

    console.print(taula)


# ==================================================
# 5. INFORME GENERAL
# ==================================================

def mostrar_informe(incidencies, descartades, total):

    valides = len(incidencies)

    urgencies = Counter(
        i["Nivell d'urgència"] for i in incidencies
    )

    # CAPÇALERA

    mostrar_capcalera()

    # 01. RESUM GENERAL

    mostrar_titol("01", "RESUM GENERAL")

    targetes = [

        mostrar_targeta(
            "TOTAL INCIDÈNCIES",
            total,
            BLAU
        ),

        mostrar_targeta(
            "INCIDÈNCIES VÀLIDES",
            valides,
            VERD
        ),

        mostrar_targeta(
            "URGÈNCIA ALTA",
            urgencies["Alt"],
            VERMELL
        ),

        mostrar_targeta(
            "REGISTRES DESCARTATS",
            descartades,
            TARONJA
        )

    ]

    console.print(
        Columns(targetes, equal=True, expand=True)
    )

    if total > 0:

        percentatge = descartades / total * 100

        console.print()

        console.print(
            f"[dim]Percentatge de registres descartats:[/dim] "
            f"[bold {TARONJA}]{percentatge:.2f}%[/bold {TARONJA}]"
        )

    if not incidencies:

        console.print(
            Panel(
                "[yellow]No hi ha incidències vàlides per analitzar.[/yellow]",
                border_style=TARONJA
            )
        )

        return

    # 02. INCIDÈNCIES PER TIPUS

    tipus = Counter(
        i["Tipus d'incidència"] for i in incidencies
    )

    mostrar_barres(
        "02 · INCIDÈNCIES PER TIPUS",
        tipus.most_common(10),
        BLAU
    )

    # 03. DISTRIBUCIÓ PER URGÈNCIA

    dades_urgencia = [

        ("Alta", urgencies["Alt"]),
        ("Mitjana", urgencies["Mitjà"]),
        ("Baixa", urgencies["Baix"])

    ]

    mostrar_barres(
        "03 · DISTRIBUCIÓ PER URGÈNCIA",
        dades_urgencia,
        VERMELL
    )

    # 04. INCIDÈNCIES PER UBICACIÓ

    ubicacions = Counter(
        i["Ubicació (aula, laboratori, despatx, biblioteca…)"]
        for i in incidencies
    )

    mostrar_barres(
        "04 · INCIDÈNCIES PER UBICACIÓ",
        ubicacions.most_common(8),
        BLAU
    )

    # 05. INCIDÈNCIES PER CURS O DEPARTAMENT

    grups = Counter(

        i.get(
            "Curs i grup (alumnat) / Departament o àrea (personal)",
            ""
        )

        for i in incidencies

        if i.get(
            "Curs i grup (alumnat) / Departament o àrea (personal)"
        )

    )

    mostrar_barres(
        "05 · INCIDÈNCIES PER CURS O DEPARTAMENT",
        grups.most_common(),
        TARONJA
    )

    # 06. AFECTACIÓ DE L'ACTIVITAT

    camp = (
        "La incidència us impedeix desenvolupar la vostra activitat?"
    )

    afectacio = Counter(

        i[camp] for i in incidencies

        if i.get(camp)

    )

    mostrar_barres(
        "06 · AFECTACIÓ DE L'ACTIVITAT",
        afectacio.most_common(),
        VERD
    )

    # 07. EVOLUCIÓ MENSUAL

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

        (mes, mesos[mes])

        for mes in ordre

    ]

    mostrar_barres(
        "07 · EVOLUCIÓ MENSUAL",
        dades_mensuals,
        BLAU
    )

    # FINAL

    console.print()

    console.print(
        Panel(
            Text.from_markup(
                "[bold white]FI DE L'INFORME[/bold white]\n"
                "[#C5D8F0]ORIGEN | IT DATA ANALYTICS[/#C5D8F0]"
            ),
            border_style=BLAU,
            box=box.DOUBLE,
            padding=(1, 2),
            expand=True
        )
    )


# ==================================================
# 6. PROGRAMA PRINCIPAL
# ==================================================

def main():

    try:

        # Llegir incidències XML

        incidencies = llegir_incidencies()

        # Filtrar registres incorrectes

        valides, descartades = filtrar_incidencies(
            incidencies
        )

        # Desar les dades al JSON

        desar_incidencies_json(valides)

        # Mostrar informe visual

        mostrar_informe(
            valides,
            descartades,
            len(incidencies)
        )

    except FileNotFoundError:

        console.print(
            "[bold red]ERROR:[/bold red] "
            "No s'ha trobat el fitxer XML."
        )

    except ET.ParseError:

        console.print(
            "[bold red]ERROR:[/bold red] "
            "El fitxer XML no té un format correcte."
        )

    except OSError as error:

        console.print(
            f"[bold red]ERROR:[/bold red] {error}"
        )
    except UnicodeEncodeError as error:

        console.print(
            f"[bold red]ERROR:[/bold red] {error}"
        )


if __name__ == "__main__":

    main()