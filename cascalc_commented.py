"""
TI-89 Style CAS Calculator — Professional Edition
===================================================
Overordnet beskrivelse:
    Dette program er en avanceret lommeregner med Computer Algebra System (CAS),
    inspireret af Texas Instruments TI-89. Den kan udføre symbolsk matematik som
    differentiation, integration, ligningsløsning, Taylor-udvikling, faktorisering
    og meget mere. Programmet er bygget med PySide6 og SymPy.

Kort brugervejledning:
    - Tast direkte på tastaturet eller klik på knapperne.
    - Brug ENTER til at evaluere et udtryk.
    - F1-F6 giver genveje til funktioner (F5 skifter til 2nd-funktioner).
    - Brug APPS til at vise variabler/historie, PRGM til enhedsomregninger,
      MODE til at skifte mellem grader/radianer, CUSTOM til konstanter.
    - Skriv "vars" for at se variabler, "clear" for at rydde, "history" for historik.
    - Brug := til at tildele variable, f.eks. a := 5.

Programmets moduler/klasser:
    - CalculatorParser: Håndterer parsing, evaluering og formatering af matematik.
    - CalculatorDisplay: Det grønne display, hvor udtryk vises.
    - MainWindow: Hovedvinduet med alle knapper, menuer og dialoger.

Hovedfunktioner:
    - Symbolsk matematik via SymPy: differentiering, integration, solve, expand, ...
    - Variabelhåndtering (lokal hukommelse).
    - Historik (op/ned-pile).
    - Enhedsomregninger og fysiske konstanter.
    - To tilstande: radianer/grader (påvirker sinus, cosinus, etc.).
    - Formatering af output med pæne brøker (½, ⅓), √, π, i, e.

Datakatalog (centrale datastrukturer):
    parser.variables: dict[str, str]  # Variable navn -> værdi som string
    parser.history: list[str]         # Gemte udtryk (seneste først? faktisk append)
    parser.degree_mode: bool          # True = grader, False = radianer
    parser._sympy_ns: dict            # Namespace til eval() med SymPy funktioner
    MainWindow.expression: str        # Nuværende udtryk i displayet
    MainWindow.second_mode: bool      # True hvis 2nd-funktioner er aktive
    MainWindow._math_btns: dict       # Gemmer referencer til matematikknapper
"""

"""
DATABASISK DATABESKRIVELSE (Data Dictionary)
============================================

CalculatorParser (klasse):
    variables: dict[str, str]
        - Format: { 'a': '5', 'b': '2*x', 'result': '10' }
        - Formål: Gemmer brugerdefinerede variable og deres værdier som strings
        - Ændres af: evaluate() ved tildeling (:= eller =)
        - Bruges af: evaluate() ved substitution, _sympy_ns opdateres
        
    history: list[str]
        - Format: ['2+2', 'sin(pi/2)', 'x^2+3*x+2']
        - Formål: Gemmer alle evaluerede udtryk i rækkefølge
        - Ændres af: evaluate() tilføjer hvert udtryk
        - Bruges af: 'history' kommando, op/ned-pil navigation
        
    degree_mode: bool
        - Format: False = radianer (standard), True = grader
        - Formål: Bestemmer om trigonometriske funktioner bruger grader
        - Ændres af: MODE dialog via radioknapper
        - Bruges af: preprocess() til at konvertere ° notation
        
    x: sympy.Symbol
        - Format: Symbol('x')
        - Formål: Symbolsk variabel til matematiske udtryk
        - Ændres af: Aldrig (konstant)
        - Bruges af: differentiation, solve, etc.
        
    y: sympy.Function
        - Format: Function('y')
        - Formål: Funktion y(x) til differentialligninger
        - Ændres af: Aldrig (konstant)
        - Bruges af: dsolve() funktion
        
    _sympy_ns: dict[str, object]
        - Format: {'sin': sin-funktion, 'pi': 3.14159..., 'x': Symbol('x'), ...}
        - Formål: Namespace til eval() - kortlægger navne til SymPy objekter
        - Ændres af: evaluate() tilføjer brugerdefinerede variable
        - Bruges af: evaluate() til at udføre matematik

MainWindow (klasse):
    parser: CalculatorParser
        - Format: Reference til CalculatorParser instans
        - Formål: Adgang til al beregningslogik
        - Ændres af: Aldrig efter __init__
        - Bruges af: _evaluate(), _on_fkey(), _run_cmd()
        
    expression: str
        - Format: "2+2*sin(x)" (eller tom streng)
        - Formål: Gemmer det aktuelle udtryk i displayet
        - Ændres af: _append(), _clear_expr(), _on_btn(), _evaluate()
        - Bruges af: display synkronisering
        
    second_mode: bool
        - Format: False = normal mode, True = 2nd-funktioner aktive
        - Formål: Skifter mellem primære og sekundære matematikfunktioner
        - Ændres af: _on_fkey('F5'), _on_math()
        - Bruges af: _update_math_btns(), _on_math()
        
    _math_btns: dict[tuple[int,int], QPushButton]
        - Format: {(0,0): QPushButton-objekt, (0,1): QPushButton-objekt, ...}
        - Formål: Gemmer referencer til alle matematikknapper for hurtig opdatering
        - Ændres af: _build_ui() tilføjer knapper
        - Bruges af: _update_math_btns() til at ændre tekst/stil
        
    mode_label: QLabel
        - Format: QLabel objekt med tekst som "  AUTO  │  RAD  │  12:45"
        - Formål: Viser status (tilstand, vinkelenhed, 2nd-mode indikator)
        - Ændres af: _on_fkey(), _on_math()
        - Bruges af: Brugeren ser status
        
    display: CalculatorDisplay
        - Format: QLineEdit-afledt objekt
        - Formål: Hoveddisplay hvor brugeren skriver og ser resultater
        - Ændres af: _append(), _clear_expr(), _evaluate(), etc.
        - Bruges af: Næsten alle interaktioner
        
    second_display: QLineEdit
        - Format: QLineEdit (readonly)
        - Formål: Sekundært display der viser sidst evaluerede udtryk
        - Ændres af: _evaluate(), _on_esc()
        - Bruges af: Brugeren ser historik
        
    func_label: QLabel
        - Format: QLabel med teksten "  F1:expand  F2:diff  F3:solve  F4:( )  F5:2nd  F6:clr"
        - Formål: Brugervejledning til funktionstaster
        - Ændres af: Aldrig (konstant)
        - Bruges af: Brugeren som reference

Dialog-relaterede data (midlertidige):
    dlg: QDialog
        - Format: QDialog objekt
        - Formål: Modalt vindue til indstillinger, konstanter, etc.
        - Ændres af: _on_mode(), _on_apps(), _on_prgm(), _on_custom()
        - Bruges af: Indsamler brugerinput og lukkes
"""

# Importer systembiblioteker til kommando linje argumenter og regulære udtryk
import sys                     # giver adgang til system-specifikke parametre/funktioner
import re                      # regulære udtryk til mønstergenkendelse i tekst
import math as _math           # matematikbibliotek (gcd, factorial) - "_" indikerer privat

# Importer PySide6 GUI komponenter til grafisk brugergrænseflade
from PySide6.QtWidgets import (           # diverse widget-klasser til GUI
    QApplication, QMainWindow, QWidget,   # applikation, hovedvindue, base widget
    QVBoxLayout, QHBoxLayout,             # vertikale/horisontale layouts
    QGridLayout, QLineEdit, QPushButton,  # grid layout, tekstfelt, knap
    QLabel, QDialog,                      # tekstlabel, dialogvindue
    QGroupBox, QRadioButton, QScrollArea, # gruppeboks, radioknap, scroll område
    QSizePolicy                           # størrelsespolitik for widgets
)
from PySide6.QtCore import Qt, QTimer     # Qt konstanter og timer til forsinkede handlinger
from PySide6.QtGui import QFont, QPalette, QColor  # skrifttype, farvepalet, farve

# Importer SymPy til symbolsk matematik (CAS kernefunktionalitet)
import sympy as sp                        # SymPy bibliotek - hele CAS motoren

# Importer specifikke SymPy funktioner/konstanter for direkte adgang
from sympy import (                       # gør koden kortere ved at undgå sp. præfiks
    symbols, Function, simplify, expand, factor, solve,  # symbolske operationer
    integrate, diff, sqrt, sin, cos, tan, log, Abs,      # matematiske funktioner
    factorial, binomial, pi, E, I, series, limit, oo,    # konstanter og specialfunktioner
    Rational, Mul, Pow                     # rationelle tal, multiplikation, potens
)
# ──────────────────────────────────────────────────────────────────────────────────────
#  PARSER / ENGINE
#  Klasse: CalculatorParser
#  Beskrivelse: Håndterer al symbolsk matematik, variabelhukommelse og historik.
#               Fungerer som "hjernen" bag lommeregneren.
#  Metoder: __init__, preprocess, evaluate, format_output, taylor_fact, _format_taylor_fact
#  Data: variables, history, degree_mode, x, y, _sympy_ns
# ──────────────────────────────────────────────────────────────────────────────────────

class CalculatorParser:
    """Parser and symbolic evaluator for the CAS calculator."""
    # Hvorfor: Adskiller beregningslogik fra GUI, så det er lettere at teste og vedligeholde
    # Funktioner: Parsing af udtryk, evaluering med SymPy, variabelhåndtering, historik

    def __init__(self):
        # Hvorfor: Initialiserer parseren med tomme datastrukturer og SymPy namespace
        # Parametre: Ingen
        # Returnerer: Intet (constructor)
        # Data påvirket: Alle instansvariable initialiseres
        
        self.variables: dict = {}          # tom ordbog til brugerdefinerede variable (a=5)
        self.history: list = []            # tom liste til historik over indtastede udtryk
        self.degree_mode: bool = False     # vinkeltilstand: False=radianer, True=grader
        self.x = symbols('x')              # symbolsk variabel 'x' til matematiske udtryk
        self.y = Function('y')             # funktion 'y' til differentialligninger (dsolve)
        
        # Namespace til eval() – alle SymPy funktioner og konstanter gøres tilgængelige
        self._sympy_ns = {                 # dict med nøgle=navn, værdi=funktion/konstant
            "solve": solve,                # løs ligninger: solve(x**2-4, x) -> [-2,2]
            "sqrt": sqrt,                  # kvadratrod: sqrt(16) -> 4
            "sin": sin,                    # sinus funktion (radianer eller grader)
            "cos": cos,                    # cosinus funktion
            "tan": tan,                    # tangens funktion
            "sinh": sp.sinh,               # hyperbolsk sinus
            "cosh": sp.cosh,               # hyperbolsk cosinus
            "tanh": sp.tanh,               # hyperbolsk tangens
            "asin": sp.asin,               # arcsin (invers sinus)
            "acos": sp.acos,               # arccos (invers cosinus)
            "atan": sp.atan,               # arctan (invers tangens)
            "asinh": sp.asinh,             # hyperbolsk arcsin
            "acosh": sp.acosh,             # hyperbolsk arccos
            "atanh": sp.atanh,             # hyperbolsk arctan
            "log": lambda x: sp.log(x, 10), # log10 med base 10 (som TI-89)
            "ln": sp.log,                  # naturlig logaritme (base e)
            "log2": lambda x: sp.log(x, 2), # logaritme med base 2
            "log10": lambda x: sp.log(x, 10), # logaritme med base 10
            "exp": sp.exp,                 # eksponentialfunktion e^x
            "Abs": Abs,                    # absolut værdi (numerisk)
            "cbrt": lambda x: sp.cbrt(x),  # kubikrod (3. rod)
            "dsolve": sp.dsolve,           # løs differentialligninger
            "trigsimp": sp.trigsimp,       # trigonometrisk simplificering
            "factorint": sp.factorint,     # primtalsfaktorisering af heltal
            "pi": pi,                      # matematisk konstant π ≈ 3.14159
            "E": E,                        # Eulers tal e ≈ 2.71828
            "I": I,                        # imaginær enhed √(-1)
            "e": E,                        # alias for E (lille e også tilladt)
            "integrate": integrate,        # symbolsk integration
            "diff": diff,                  # symbolsk differentiation
            "symbols": symbols,            # opret symbolske variable
            "expand": expand,              # udvid parenteser: (x+1)^2 -> x^2+2x+1
            "factor": factor,              # faktoriser: x^2-1 -> (x-1)(x+1)
            "simplify": simplify,          # simplificer udtryk automatisk
            "taylor": series,              # Taylor rækkeudvikling (alias)
            "series": series,              # Taylor rækkeudvikling
            "limit": limit,                # beregn grænseværdier
            "oo": oo,                      # uendelig (infinity)
            "x": self.x,                   # symbolsk variabel x
            "y": self.y,                   # funktion y (til differentialligninger)
            "sp": sp,                      # hele SymPy modulet (til avancerede brugere)
        }

    # ── preprocessing ──────────────────────────────────────────

    def preprocess(self, expr: str) -> str:
        # Hvorfor: Konverterer brugervenlig notation til SymPy-forståelig syntax
        # Funktioner: Grad-konvertering (30°→π/6), implicit multiplikation (2x→2*x)
        # Parametre: expr (string) - brugerens indtastede udtryk
        # Returnerer: String - forarbejdet udtryk klar til eval()
        # Data påvirket: Ingen (ren funktion)
        
        expr = expr.strip()                # fjern whitespace i begge ender af strengen

        # Konverter grader: "30°" → "(30*pi/180)"
        # Regex: (\d+(?:\.\d+)?)°  fanger tal (heltal eller decimal) efterfulgt af °
        # Erstat med (\1*pi/180) - \1 er det fangede tal
        expr = re.sub(r'(\d+(?:\.\d+)?)°', r'(\1*pi/180)', expr)
        expr = expr.replace('°', '*(pi/180)')   # faldback: hvis ° står alene

        # Konverter caret ^ til Python potensoperator **
        expr = expr.replace('^', '**')          # SymPy forstår **, ikke ^

        # Tokeniser (beskyt videnskabelig notation som 1.23e-5)
        # find alle: tal (med e-notation), bogstaver, tal, operatorer, parenteser
        tokens = re.findall(
            r'\d+\.?\d*[eE][+-]?\d+|[a-zA-Z]\w*|\d+\.?\d*'  # tal og ord
            r'|[\+\-\*/\^=,():]|\]|\[',                     # operatorer og tegn
            expr
        )

        # Implicit multiplikation: 2x → 2*x, x( → x*(, 2π → 2*π
        result = []                        # tom liste til at bygge resultatet
        for i, tok in enumerate(tokens):   # loop over hvert token med indeks
            result.append(tok)             # tilføj tokenet til resultat
            if i + 1 < len(tokens):        # hvis der er et næste token
                nxt = tokens[i + 1]        # gem det næste token
                # Hvis nuværende slutter med tal/bogstav/π og næste starter med bogstav/π/(
                if re.match(r'.*[0-9a-zA-Zπ]$', tok) and re.match(r'^[a-zA-Zπ\(]', nxt):
                    # Undlad * hvis nuværende er funktionsnavn efterfulgt af (
                    if not (nxt == '(' and re.match(r'^[a-zA-Z]', tok)):
                        result.append('*') # indsæt * for implicit multiplikation
        return ''.join(result)             # saml listen til én streng

    # ── evaluation ─────────────────────────────────────────────

    def evaluate(self, expr: str) -> str:
        # Hvorfor: Hovedfunktionen der evaluerer matematiske udtryk og kommandoer
        # Funktioner: Håndterer kommandoer (clear, vars, history), variabeltildeling (:=)
        # Parametre: expr (string) - brugerens indtastede udtryk eller kommando
        # Returnerer: String - resultatet som tekst (eller fejlmeddelelse)
        # Data påvirket: history (tilføjes), variables (opdateres ved := eller =)
        
        if not expr.strip():               # hvis udtrykket er tomt eller kun whitespace
            return ""                      # returner tom streng (ingen handling)

        self.history.append(expr)          # gem udtrykket i historikken

        # Håndter indbyggede kommandoer (små bogstaver for case-insensitiv match)
        cmd = expr.strip().lower()         # konverter til lowercase og fjern whitespace
        
        if cmd in ('clear', 'clr'):        # kommando: ryd alle variable
            self.variables.clear()         # tøm ordbogen over variable
            return "Variables cleared"     # bekræftelsesbesked til brugeren
            
        if cmd in ('vars', 'variables'):   # kommando: vis alle variable
            if not self.variables:         # hvis ingen variable er gemt
                return "No variables stored"  # informer brugeren
            # Returnér hver variabel på sin egen linje: "a = 5"
            return "\n".join(f"{k} = {v}" for k, v in self.variables.items())
            
        if cmd == 'history':               # kommando: vis historik
            # Returnér hver historiklinje eller "No history" hvis tom
            return "\n".join(str(h) for h in self.history) or "No history"
            
        if cmd == 'last':                  # kommando: hent sidste resultat
            if len(self.history) >= 2:     # hvis der er mindst 2 udtryk (nuværende + forrige)
                return self.evaluate(self.history[-2])  # evaluer næstsidste udtryk
            return "No previous expression"  # fejlbesked hvis ingen historik

        # Variabeltildeling med := operator (f.eks. "a := 5")
        if ':=' in expr:                   # tjek efter special-operatoren
            var_name, value_expr = expr.split(':=', 1)  # split ved første :=
            var_name = var_name.strip()    # fjern whitespace omkring variabelnavn
            result = self.evaluate(value_expr.strip())  # evaluer højresiden
            self.variables[var_name] = result          # gem i variabelordbogen
            try:
                # Forsøg at konvertere til SymPy-objekt til fremtidige beregninger
                self._sympy_ns[var_name] = sp.sympify(result)
            except Exception:              # hvis konvertering fejler (f.eks. tekst)
                pass                       # ignorér - variabel er stadig gemt som string
            return f"{var_name} = {result}"  # returnér bekræftelse

        # Simpel tildeling: "a = 5" (kun 1-2 bogstaver for at undgå ==, !=, <=, >=)
        if '=' in expr and not any(op in expr for op in ('==', '!=', '<=', '>=')):
            if expr.count('=') == 1:       # præcis ét lighedstegn (ikke sammenligning)
                var_name, rest = expr.split('=', 1)  # split ved første =
                var_name = var_name.strip()          # fjern whitespace
                # Tjek at variabelnavn er gyldigt (bogstaver) og max 2 tegn
                if var_name.isidentifier() and len(var_name) <= 2 and rest.strip():
                    result = self.evaluate(rest.strip())  # evaluer højresiden
                    self.variables[var_name] = result    # gem variabel
                    try:
                        self._sympy_ns[var_name] = sp.sympify(result)  # SymPy-version
                    except Exception:
                        pass
                    return f"{var_name} = {result}"  # returnér bekræftelse

        # Forarbejd udtrykket (gradkonvertering, implicit multiplikation)
        processed = self.preprocess(expr)

        try:
            # EVAL: Udfør det forarbejdede udtryk i SymPy namespace
            # {"__builtins__": {}} forhindrer adgang til farlige Python-funktioner
            result = eval(processed, {"__builtins__": {}}, self._sympy_ns)

            # Hvis resultatet er et tal, formater det pænt
            if hasattr(result, 'is_number') and result.is_number:
                # Tjek for division med nul (uendelig)
                if result in (sp.oo, -sp.oo, sp.zoo):
                    return "Division by Zero / Undefined"
                # 15 decimalers præcision, fjern efterfølgende nuller og punktum
                return str(result.evalf(15)).rstrip('0').rstrip('.')
            return str(result)             # returnér symbolsk resultat som string
        except Exception as exc:           # fang alle fejl (syntax, matematik, etc.)
            return f"Error: {exc}"         # returnér brugervenlig fejlmeddelelse

    # ── output formatting ───────────────────────────────────────

    def format_output(self, result: str) -> str:
        # Hvorfor: Gør SymPy-output pænere og mere læsbart for mennesker
        # Funktioner: √ symbol, π, i, brøker (½, ⅓), ^ i stedet for **
        # Parametre: result (string) - rå output fra evaluate()
        # Returnerer: String - pænt formateret output
        # Data påvirket: Ingen (ren funktion)
        
        if not result:                     # hvis resultatet er tomt
            return ""                      # returnér tomt

        s = str(result)                    # konverter til string

        # Tilføj parenteser omkring base**exp før konvertering **→^
        # Eksempel: "x**2/3" → "(x**2)/3" for at bevare betydning
        if '**' in s:                      # hvis der er potenser i udtrykket
            s = re.sub(r'([a-z]?\*\*\d+)/(\d+)',  # find mønster som x**2/3
                       lambda m: f'({m.group(1)})/{m.group(2)}', s)  # tilføj ()

        s = s.replace('**', '^')           # konverter Python potens til ^ notation

        # Beskyt eksponent-brøker mod simplificering (midlertidig placeholder)
        protected: list[str] = []          # tom liste til beskyttede strenge

        def _protect(m):                   # indre funktion til at beskytte mønstre
            protected.append(m.group(0))   # gem det fundne mønster
            return f"__EP{len(protected)-1}__"  # returnér placeholder

        # Find mønstre som "^1/2" og beskyt dem (midlertidig erstatning)
        s = re.sub(r'\^(\d+)\s*/\s*(\d+)', _protect, s)

        # Simplificer almindelige heltalsbrøker (f.eks. 2/4 → 1/2)
        def _simplify_frac(m):             # hjælpefunktion til brøk-simplificering
            try:
                num, den = int(m.group(1)), int(m.group(2))  # tæller og nævner
                g = _math.gcd(num, den)    # beregn største fælles divisor
                num, den = num // g, den // g  # divider med gcd
                if den == 1:               # hvis nævner er 1
                    return str(num)        # returnér kun tælleren (heltal)
                # Map af Unicode-brøksymboler (pænere end "1/2")
                frac_map = {
                    '1/2': '½', '1/3': '⅓', '2/3': '⅔',
                    '1/4': '¼', '3/4': '¾',
                    '1/5': '⅕', '2/5': '⅖', '3/5': '⅗', '4/5': '⅘',
                    '1/6': '⅙', '1/8': '⅛', '3/8': '⅜',
                    '5/8': '⅝', '7/8': '⅞',
                }
                key = f'{num}/{den}'       # lav nøgle som "1/2"
                return frac_map.get(key, key)  # returnér Unicode eller original
            except Exception:              # ved fejl (f.eks. ikke-tal)
                return m.group(0)          # returnér uændret

        # Find og erstat brøker som "1/2" med Unicode-symboler
        s = re.sub(r'\b(\d+)/(\d+)\b', _simplify_frac, s)

        # Gendan de beskyttede eksponent-brøker (f.eks. x^(1/2) forbliver sådan)
        for i, p in enumerate(protected):  # loop over beskyttede strenge
            s = s.replace(f"__EP{i}__", p) # erstat placeholder med original

        # Konverter sqrt(123) til √123 (pænere rodtegn)
        s = re.sub(r'sqrt\((\d+)\)', r'√\1', s)      # tal: sqrt(16) → √16
        s = re.sub(r'sqrt\(([^)]+)\)', r'√(\1)', s)   # udtryk: sqrt(x+1) → √(x+1)

        # Konverter pi til π (græsk bogstav)
        s = s.replace('*pi', '·π')         # 2*pi → 2·π (multiplikationsprik)
        s = s.replace('pi', 'π')           # pi → π

        # Konverter imaginær enhed I til i (som TI-89 bruger)
        s = s.replace('I*', 'i·')          # I*x → i·x
        s = s.replace('*I', '·i')          # x*I → x·i
        s = re.sub(r'\bI\b', 'i', s)       # fritstående I → i

        # Konverter Euler E til e (lille e), men ikke inde i 'exp'
        s = re.sub(r'(?<!xp)\bE\b', 'e', s) # negative lookbehind undgår 'exp'

        return s                           # returnér det pænt formaterede resultat

    # ── taylor series helper ────────────────────────────────────

    def taylor_fact(self, expr_str: str):
        # Hvorfor: Speciel formatering af Taylor-rækker med fakulteter (x^n/n!)
        # Funktioner: Detekterer taylor/series og formaterer med ! symbol
        # Parametre: expr_str (string) - udtrykket der skal evalueres
        # Returnerer: Formatteret string eller None hvis ikke Taylor-række
        # Data påvirket: Ingen
        
        # Tjek om udtrykket indeholder 'taylor' eller 'series'
        if not ('taylor' in expr_str or 'series' in expr_str):
            return None                    # ikke en Taylor-række, returnér None
        
        processed = self.preprocess(expr_str)  # forarbejd udtrykket
        
        try:
            # Evaluer udtrykket som normalt
            result = eval(processed, {"__builtins__": {}}, self._sympy_ns)
            # Tjek om resultatet indeholder symbolske variable (frie symboler)
            if hasattr(result, 'free_symbols') and result.free_symbols:
                return self._format_taylor_fact(result)  # formater med fakulteter
        except Exception:                  # hvis evaluering fejler
            pass                           # ignorér og returnér None
        return None                        # ikke en gyldig Taylor-række

    def _format_taylor_fact(self, expr) -> str:
        # Hvorfor: Hjælpefunktion der konverterer 1/6 til 1/3! (fakultet)
        # Funktioner: Finder mønstre som x^3/6 og erstatter med x^3/3!
        # Parametre: expr - SymPy-objekt (Taylor-række)
        # Returnerer: String - formatteret med fakultetsnotation
        # Data påvirket: Ingen
        
        s = str(expr).replace('**', '^')   # konverter potens til ^ notation

        def _to_fact(m):                   # hjælpefunktion til fakultetskonvertering
            exp = int(m.group(1))          # eksponent (f.eks. 3 i x^3)
            den = int(m.group(2))          # nævner (f.eks. 6 i /6)
            expected = _math.factorial(exp)  # beregn forventet fakultet (3! = 6)
            if den == expected:            # hvis nævner matcher fakultetet
                return f"x^{exp}/{exp}!"   # returnér med ! notation
            return m.group(0)              # ellers returnér uændret

        # Find mønstre som "x^3/6" og konverter til "x^3/3!" hvis 6 == 3!
        s = re.sub(r'x\^(\d+)/(\d+)(?!!)', _to_fact, s)

        def _fix_o(m):                     # hjælpefunktion til O-notation (restled)
            exp = int(m.group(1))          # eksponent i O(x^n)
            # Hvis eksponenten er lige, øg med 1 (standard i nogle rækker)
            return f'O(x^{exp+1})' if exp % 2 == 0 else m.group(0)

        # Fix O(x^n) notation (restled i Taylor-rækker)
        s = re.sub(r'O\(x\^(\d+)\)', _fix_o, s)
        return s                           # returnér formatteret string
# ─────────────────────────────────────────────────────────────
#  DISPLAY WIDGET
#  Klasse: CalculatorDisplay
#  Beskrivelse: Specialiseret tekstfelt til hoveddisplayet (grøn TI-89 skærm)
#  Metoder: __init__ (constructor)
#  Data: Arver fra QLineEdit
# ─────────────────────────────────────────────────────────────

class CalculatorDisplay(QLineEdit):
    """Primary LCD display — dusty-green TI-89 screen."""
    # Hvorfor: Tilpasset display med fast højde, bestemt skrifttype og farver
    # Funktioner: Viser det aktuelle udtryk, tillader cursor-positionering
    # Parametre til metoder: parent (QWidget) - forælderwidget (MainWindow)
    # Data påvirket: Displayets udseende og indhold

    def __init__(self, parent=None):
        # Hvorfor: Initialiserer displayet med TI-89-inspireret udseende
        # Parametre: parent - forælderwidget (kan være None)
        # Returnerer: Intet (constructor)
        # Data påvirket: Displayets egenskaber (readonly, alignment, height, font)
        
        super().__init__(parent)           # kald forælderklassens constructor (QLineEdit)
        self.setReadOnly(False)            # tillad redigering (cursor og indtastning)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)  # højrejusteret som TI-89
        self.setFixedHeight(64)            # fast højde på 64 pixels
        # Courier New er monospaced (alle tegn lige brede) - godt til matematik
        self.setFont(QFont("Courier New", 20, QFont.Weight.Bold))  # fed skrift, 20pt
        # Farve sættes via stylesheet i MainWindow.TI_STYLE (grøn baggrund)
        self.setObjectName("main_display") # navn til styling via CSS

# ─────────────────────────────────────────────────────────────
#  BUTTON HELPERS (inline styles — CSS class workaround)
#  Funktioner: Hjælpefunktioner til at lave knapper med ensartet styling
#  Data: _BTN_BASE (string) - CSS skabelon til knapper
# ─────────────────────────────────────────────────────────────

# CSS (Cascading Style Sheets) skabelon til knapper
# {bg}=baggrund, {fg}=forgrundsfarve, {border}=kant, {bot}=bundtykkelse
_BTN_BASE = """
    QPushButton {{
        background-color: {bg};
        color: {fg};
        border: 1px solid {border};
        border-bottom: {bot}px solid {bot_color};
        border-radius: 4px;
        font-family: 'Arial', sans-serif;
        font-size: {fsize}px;
        font-weight: bold;
        padding: 2px;
    }}
    QPushButton:hover  {{ background-color: {hover}; }}   # når musen er over
    QPushButton:pressed {{ background-color: {press}; border-bottom: 1px solid {border}; }}  # når der klikkes
"""

def _style(bg, fg, border, bot_color, hover, press, fsize=12, bot=3):
    # Hvorfor: Genererer CSS string til en knap med givne farver og dimensioner
    # Parametre: bg, fg, border, bot_color, hover, press, fsize, bot
    # Returnerer: String med formatteret CSS
    # Data påvirket: Ingen (ren funktion)
    
    return _BTN_BASE.format(               # udfyld skabelonen med værdier
        bg=bg, fg=fg, border=border, bot=bot,
        bot_color=bot_color, hover=hover, press=press, fsize=fsize
    )

# Foruddefinerede stilarter til forskellige knaptyper
NUM_STYLE   = _style("#3c3c3c", "#e8e8e8", "#222", "#111", "#505050", "#282828", fsize=16)   # tal-knapper (mørkegrå)
OP_STYLE    = _style("#5a5a5a", "#ffffff", "#404040", "#2a2a2a", "#6e6e6e", "#464646", fsize=18)  # operatorer (+ - × ÷)
FUNC_STYLE  = _style("#9a7000", "#111111", "#7a5800", "#5a3e00", "#c49a10", "#7a5800", fsize=10)  # matematikfunktioner (guld)
FUNC2_STYLE = _style("#3a3a7a", "#ffff55", "#2a2a5a", "#1a1a3a", "#5050aa", "#2a2a5a", fsize=10)  # 2nd funktioner (blå)
ENTER_STYLE = _style("#1a4a7a", "#ffffff", "#0a3060", "#061e4a", "#2a5a8a", "#0a3060", fsize=13, bot=4)  # ENTER-knap (blå)
MENU_STYLE  = _style("#2e2e2e", "#cccccc", "#1a1a1a", "#0a0a0a", "#424242", "#1c1c1c", fsize=11)  # menu-knapper (mørke)
VAR_STYLE   = _style("#2a4a2a", "#88ff88", "#1a3a1a", "#0e2a0e", "#3a5e3a", "#1a3a1a", fsize=13)  # variable-knapper (grønne)

def _make_btn(label: str, style: str, w: int = 52, h: int = 44) -> QPushButton:
    # Hvorfor: Fabriksfunktion til at oprette standardiserede knapper
    # Funktioner: Opretter QPushButton med given tekst, stil og størrelse
    # Parametre: label - knappens tekst, style - CSS stil, w - bredde, h - højde
    # Returnerer: QPushButton objekt, klar til at blive tilføjet til GUI
    # Data påvirket: Opretter ny knap (ingen eksisterende data ændres)
    
    btn = QPushButton(label)               # opret knap med given tekst
    btn.setFixedSize(w, h)                 # sæt fast bredde og højde
    btn.setStyleSheet(style)               # anvend CSS styling
    btn.setCursor(Qt.CursorShape.PointingHandCursor)  # hånd-cursor når musen er over
    return btn                             # returnér den færdige knap
# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
#  Klasse: MainWindow
#  Beskrivelse: Hovedvinduet med alle knapper, display, menuer og dialoger
#  Metoder: __init__, _apply_window_style, _build_ui, _append, _clear_expr,
#           _on_btn, _evaluate, _on_esc, _on_fkey, _update_math_btns,
#           _on_math, keyPressEvent, _dialog_base, _scrolled_dialog,
#           _insert_and_close, _on_mode, _on_apps, _run_cmd, _on_prgm, _on_custom
#  Data: parser, expression, second_mode, _math_btns, mode_label, display,
#        second_display, func_label
# ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """CAS Calculator — TI-89 Professional Layout."""

    # ── function-key templates ──────────────────────────────────
    # Skabeloner til F1-F6 funktionstaster (hvad der indsættes i displayet)
    F_TEMPLATES = {
        "F1": "expand()",          # udvid parenteser
        "F2": "diff(,x)",          # differentier mht. x
        "F3": "solve(,x)",         # løs ligning mht. x
        "F4": "()",                # parenteser
        "F6": "__CLEAR__",         # specialværdi: ryd alle variable
    }
    # Label der vises under F-tasterne (brugervejledning)
    F_LABELS = "  F1:expand  F2:diff  F3:solve  F4:( )  F5:2nd  F6:clr"

    # ── math button definitions: (primary, secondary) ──────────
    # Definition af matematikknapper: (primær funktion, sekundær funktion ved 2nd)
    # Række 0-5, hver med 4-6 knapper (primær, sekundær)
    MATH_FUNCS = [
        [("sin",      "sinh"),    ("cos",     "cosh"),    ("tan",    "tanh"),   ("ln",      "log10")],
        [("asin",     "asinh"),   ("acos",    "acosh"),   ("atan",   "atanh"),  ("log",     "log2")],
        [("sqrt",     "cbrt"),    ("x²",      "1/x"),     ("x³",     "x^y"),    ("^",       "10^x")],
        [("(",        "|x|"),     (")",       "!"),       ("solve(", "dsolve("),("factor(", "factorint(")],
        [("expand(",  "simplify("),("diff(",  "taylor("), ("∫(",     "limit("), (",",        "==")],
        [("π",        "2π"),      ("e",       "e^x"),     ("ans",    "last"),   ("i",       "∞")],
    ]

    def __init__(self):
        # Hvorfor: Initialiserer hele lommeregnerens brugergrænseflade og tilstand
        # Parametre: Ingen (selv refererer til instansen)
        # Returnerer: Intet (constructor)
        # Data påvirket: Alle instansvariable initialiseres, GUI bygges
        
        super().__init__()                 # kald QMainWindow constructor
        self.parser = CalculatorParser()   # opret parser-objekt til matematik
        self.expression = ""               # nuværende udtryk i displayet (tomt start)
        self.second_mode = False           # False = normal mode, True = 2nd-funktioner
        self._math_btns: dict = {}         # ordbog til at gemme matematikknapper (row,col) -> knap

        self.setWindowTitle("CheapCAS  ·  TI-89 CAS Calculator")  # vinduestitel
        self.setFixedSize(480, 840)        # fast størrelse: 480 bred, 840 høj (pixels)
        self._apply_window_style()         # anvend global styling på vinduet
        self._build_ui()                   # byg hele brugergrænsefladen

    # ── window-level stylesheet ─────────────────────────────────

    def _apply_window_style(self):
        # Hvorfor: Anvender global CSS-styling på hele vinduet og dets widgets
        # Funktioner: Sætter baggrundsfarver, display-farver (grøn TI-89 skærm)
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Vinduets udseende via Qt stylesheets
        
        self.setStyleSheet("""
            QMainWindow, QWidget#central {    # hovedvindue og central widget
                background-color: #1c1c1c;    # mørkegrå baggrund (som TI-89)
            }
            QLineEdit#main_display {          # hoveddisplay (grøn skærm)
                background-color: #97b597;    # støvet grøn baggrund (TI-89 look)
                color: #0d1f0d;               # mørkegrøn tekst
                border: 3px solid #3a3a3a;    # mørkegrå kant
                border-radius: 5px;           # afrundede hjørner
                padding: 6px 10px;            # indvendig afstand
                font-family: 'Courier New', monospace;  # monospaced skrift
                font-size: 20px;              # stor skriftstørrelse
                font-weight: bold;            # fed skrift
            }
            QLineEdit#second_display {        # sekundært display (resultater)
                background-color: #7ea07e;    # lidt mørkere grøn
                color: #0d1f0d;               # mørkegrøn tekst
                border: 1px solid #3a3a3a;    # tynd kant
                border-radius: 3px;           # svagt afrundede hjørner
                padding: 3px 8px;             # mindre indvendig afstand
                font-family: 'Courier New', monospace;
                font-size: 13px;              # mindre skrift
            }
        """)

    # ── UI construction ─────────────────────────────────────────

    def _build_ui(self):
        # Hvorfor: Bygger hele brugergrænsefladen fra bunden
        # Funktioner: Opretter display, knapperækker, funktionstaster, matematikknapper
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Opretter alle GUI-elementer og tilføjer dem til vinduet
        
        central = QWidget()                # central widget (beholder til alt indhold)
        central.setObjectName("central")   # navn til styling
        self.setCentralWidget(central)     # gør den til hovedvinduets centrale widget

        root = QVBoxLayout(central)        # vertikal hoved-layout (stablet oppefra og ned)
        root.setSpacing(3)                 # 3 pixels mellemrum mellem elementer
        root.setContentsMargins(6, 6, 6, 6)  # margen på 6 pixels på alle sider

        # Status bar (viser tilstand: AUTO, RAD, tid)
        self.mode_label = QLabel("  AUTO  │  RAD  │  12:45")  # tekst i statuslinje
        self.mode_label.setStyleSheet(      # styling af statuslinje
            "background:#111; color:#00ee77; font-family:'Courier New';"
            "font-size:11px; padding:3px 8px; border:1px solid #333;"
        )
        root.addWidget(self.mode_label)    # tilføj statuslinje til layout

        # Main display (hvor brugeren skriver)
        self.display = CalculatorDisplay() # opret det grønne display
        root.addWidget(self.display)       # tilføj display til layout

        # Second (result) display (viser resultatet af sidste beregning)
        self.second_display = QLineEdit()  # almindeligt tekstfelt
        self.second_display.setReadOnly(True)  # skrivebeskyttet (kun output)
        self.second_display.setAlignment(Qt.AlignmentFlag.AlignRight)  # højrejusteret
        self.second_display.setFixedHeight(32)  # lavere end hoveddisplay
        self.second_display.setObjectName("second_display")  # navn til styling
        root.addWidget(self.second_display)  # tilføj til layout

        # ── F1–F6 row ──────────────────────────────────────────
        frow = QHBoxLayout()               # horisontal layout til funktionstaster
        frow.setSpacing(2)                 # 2 pixels mellem knapper
        
        # Loop over F1 til F6 og opret en knap for hver
        for f in ("F1", "F2", "F3", "F4", "F5", "F6"):
            b = _make_btn(f, FUNC_STYLE, w=68, h=38)  # opret knap med funktionsstil
            # Forbind klik-signal til _on_fkey med knappens navn som argument
            b.clicked.connect(lambda _, k=f: self._on_fkey(k))
            frow.addWidget(b)              # tilføj knap til layout
        
        root.addLayout(frow)               # tilføj funktionsknap-rækken til hovedlayout

        # Label der viser hvad F-tasterne gør (brugervejledning)
        self.func_label = QLabel(self.F_LABELS)  # tekst fra klasseskabelon
        self.func_label.setStyleSheet(      # styling
            "color:#888; font-family:'Courier New'; font-size:9px; padding:1px 2px;"
        )
        root.addWidget(self.func_label)    # tilføj label til layout

        # ── Variable & constant quick-insert row ────────────────
        vrow = QHBoxLayout()               # horisontal layout til variable
        vrow.setSpacing(2)                 # 2 pixels mellemrum
        
        # Opret knapper til almindelige variable (x, y, t, n)
        for v in ("x", "y", "t", "n"):
            b = _make_btn(v, VAR_STYLE, w=44, h=36)  # opret variabel-knap
            b.clicked.connect(lambda _, c=v: self._append(c))  # indsæt variabel
            vrow.addWidget(b)              # tilføj knap
        
        # Opret knapper til gradtegn og pi
        for v in ("°", "π"):
            b = _make_btn(v, VAR_STYLE, w=44, h=36)  # opret knap
            b.clicked.connect(lambda _, c=v: self._append(c))  # indsæt tegn
            vrow.addWidget(b)              # tilføj knap
        
        vrow.addStretch()                  # skub alle knapper til venstre (tom plads til højre)
        root.addLayout(vrow)               # tilføj variabel-rækken til hovedlayout

        # ── Main button grid ────────────────────────────────────
        # Grid layout med 5 rækker og 7 kolonner (efter TI-89 layout)
        grid = QGridLayout()               # grid (tabel) layout
        grid.setSpacing(3)                 # 3 pixels mellemrum mellem celler
        grid.setContentsMargins(0, 2, 0, 2)  # margen: venstre, top, højre, bund

        # Row 0 — navigation / control (ESC, APPS, PRGM, MODE, DEL, PIL OP, PIL NED)
        # Liste af tuples: (knaptekst, funktion der kaldes)
        for col, (lbl, action) in enumerate([
            ("ESC",  self._on_esc),        # ESC: ryd display
            ("APPS", self._on_apps),       # APPS: vis variable/historie dialog
            ("PRGM", self._on_prgm),       # PRGM: enhedsomregninger
            ("MODE", self._on_mode),       # MODE: radianer/grader indstilling
            ("DEL",  lambda: self._on_btn("DEL")),   # DEL: slet sidste tegn
            ("▲",    lambda: self._on_btn("UP")),    # UP: historik op
            ("▼",    lambda: self._on_btn("DOWN")),  # DOWN: historik ned
        ]):
            b = _make_btn(lbl, MENU_STYLE, w=56, h=38)  # opret menu-knap
            b.clicked.connect(action)      # forbind til den specificerede funktion
            grid.addWidget(b, 0, col)      # tilføj til grid (række 0, kolonne col)

        # Row 1 — tal 7,8,9, division, CUSTOM (bred knap)
        for col, lbl in enumerate(("7", "8", "9"), start=1):  # kolonne 1,2,3
            b = _make_btn(lbl, NUM_STYLE)  # opret tal-knap
            b.clicked.connect(lambda _, c=lbl: self._append(c))  # indsæt tal
            grid.addWidget(b, 1, col)      # tilføj til grid (række 1)
        
        b = _make_btn("÷", OP_STYLE)       # divisionsknap
        b.clicked.connect(lambda: self._append("/"))  # indsæt / tegn
        grid.addWidget(b, 1, 4)            # tilføj til grid (række 1, kolonne 4)
        
        custom_b = _make_btn("CUSTOM", ENTER_STYLE, w=112, h=44)  # bred CUSTOM knap
        custom_b.clicked.connect(self._on_custom)  # vis konstant-dialog
        grid.addWidget(custom_b, 1, 5, 1, 2)  # span over 2 kolonner (5-6)

        # Row 2 — tal 4,5,6, gange, venstre pil, højre pil
        for col, lbl in enumerate(("4", "5", "6"), start=1):  # kolonne 1,2,3
            b = _make_btn(lbl, NUM_STYLE)  # opret tal-knap
            b.clicked.connect(lambda _, c=lbl: self._append(c))
            grid.addWidget(b, 2, col)
        
        b = _make_btn("×", OP_STYLE)       # gangeknap
        b.clicked.connect(lambda: self._append("*"))  # indsæt * tegn
        grid.addWidget(b, 2, 4)
        
        b = _make_btn("◀", MENU_STYLE)     # venstre pil (cursor)
        b.clicked.connect(lambda: self._on_btn("LEFT"))
        grid.addWidget(b, 2, 5)
        
        b = _make_btn("▶", MENU_STYLE)     # højre pil (cursor)
        b.clicked.connect(lambda: self._on_btn("RIGHT"))
        grid.addWidget(b, 2, 6)

        # Row 3 — tal 1,2,3, minus, negativ
        for col, lbl in enumerate(("1", "2", "3"), start=1):  # kolonne 1,2,3
            b = _make_btn(lbl, NUM_STYLE)
            b.clicked.connect(lambda _, c=lbl: self._append(c))
            grid.addWidget(b, 3, col)
        
        b = _make_btn("−", OP_STYLE)       # minusknap
        b.clicked.connect(lambda: self._append("-"))
        grid.addWidget(b, 3, 4)
        
        b = _make_btn("(-)", MENU_STYLE)   # negativ parentes-knap
        b.clicked.connect(lambda: self._on_btn("NEG"))
        grid.addWidget(b, 3, 5)

        # Row 4 — 0 (bred), punktum, plus, ENTER (høj)
        b = _make_btn("0", NUM_STYLE, w=160, h=44)  # bred 0-knap (3 kolonner bred)
        b.clicked.connect(lambda: self._append("0"))
        grid.addWidget(b, 4, 1, 1, 3)      # span over 3 kolonner (1-3)
        
        b = _make_btn(".", NUM_STYLE)      # decimalpunktum
        b.clicked.connect(lambda: self._append("."))
        grid.addWidget(b, 4, 4)
        
        b = _make_btn("+", OP_STYLE)       # plusknap
        b.clicked.connect(lambda: self._append("+"))
        grid.addWidget(b, 4, 5)
        
        enter_b = _make_btn("ENTER", ENTER_STYLE, w=56, h=88)  # høj ENTER-knap
        enter_b.clicked.connect(lambda: self._on_btn("ENTER"))  # evaluer udtryk
        grid.addWidget(enter_b, 4, 6, 2, 1)   # span over 2 rækker (4-5)

        root.addLayout(grid)               # tilføj grid til hovedlayout

        # ── Math / CAS function buttons ─────────────────────────
        math_grid = QGridLayout()          # grid til matematikknapper
        math_grid.setSpacing(2)            # 2 pixels mellemrum
        math_grid.setContentsMargins(0, 2, 0, 0)  # lille topmargen

        # Loop over rækker og kolonner i MATH_FUNCS definitionen
        for r, row in enumerate(self.MATH_FUNCS):  # r = rækkeindeks (0-5)
            for c, (primary, secondary) in enumerate(row):  # c = kolonneindeks
                b = _make_btn(primary, FUNC_STYLE, w=108, h=40)  # opret knap
                # Forbind til _on_math med primær og sekundær funktion
                b.clicked.connect(lambda _, p=primary, s=secondary: self._on_math(p, s))
                math_grid.addWidget(b, r, c)  # tilføj til grid
                self._math_btns[(r, c)] = b   # gem reference til knappen

        root.addLayout(math_grid)          # tilføj matematik-grid til hovedlayout

    # ── event routing ───────────────────────────────────────────

    def _append(self, text: str):
        # Hvorfor: Tilføjer tekst til det aktuelle udtryk og opdaterer displayet
        # Funktioner: Indsætter tegn i slutningen af udtrykket
        # Parametre: text (string) - teksten der skal tilføjes (f.eks. "sin")
        # Returnerer: Intet
        # Data påvirket: self.expression og displayets tekst
        
        self.expression += text            # tilføj tekst til udtrykket
        self.display.setText(self.expression)  # opdater display

    def _clear_expr(self):
        # Hvorfor: Rydder det aktuelle udtryk fra displayet
        # Funktioner: Nulstiller udtryks-strengen og tømmer display
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: self.expression og displayets tekst
        
        self.expression = ""               # sæt udtryk til tom streng
        self.display.setText("")           # ryd displayet

    def _on_btn(self, text: str):
        # Hvorfor: Håndterer tryk på specialknapper (ENTER, DEL, NEG, piletaster)
        # Funktioner: Udfører handlinger baseret på hvilken knap der blev trykket
        # Parametre: text (string) - knappens identifikator ("ENTER", "DEL", etc.)
        # Returnerer: Intet
        # Data påvirket: self.expression, display, parser.history
        
        if text == "ENTER":                # hvis ENTER blev trykket
            self._evaluate()               # evaluer udtrykket
        
        elif text == "DEL":                # hvis DELETE blev trykket
            self.expression = self.expression[:-1]  # fjern sidste tegn
            self.display.setText(self.expression)   # opdater display
        
        elif text == "NEG":                # hvis negativ parentes-knap
            self.expression += "(-"        # tilføj "(-" (åben parentes med minus)
            self.display.setText(self.expression)  # opdater display
        
        elif text in ("UP", "DOWN"):       # hvis op- eller ned-pil (historik)
            if self.parser.history:        # hvis der er gemt historik
                # UP: seneste udtryk (indeks -1), DOWN: næstseneste (indeks -2)
                idx = -1 if text == "UP" else -2
                try:
                    # Hent historik-element og sæt det i displayet
                    self.display.setText(self.parser.history[idx])
                except IndexError:         # hvis indekset er uden for rækkevidde
                    pass                   # ignorér (gør ingenting)
        
        elif text in ("LEFT", "RIGHT"):    # venstre/højre pil (cursor)
            cur = self.display.cursorPosition()  # få nuværende cursorposition
            # Flyt cursor: +1 til højre, -1 til venstre
            self.display.setCursorPosition(cur + (1 if text == "RIGHT" else -1))

    def _evaluate(self):
        # Hvorfor: Hovedfunktion til at evaluere det aktuelle matematiske udtryk
        # Funktioner: Henter udtryk fra display, evaluerer med parser, viser resultat
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: self.expression, self.second_display, self.display
        
        expr = self.display.text().strip() # hent udtryk fra display (fjern whitespace)
        self.expression = expr             # gem i instansvariabel
        
        if not expr:                       # hvis udtrykket er tomt
            return                         # gør ingenting
        
        # Tjek om det er en Taylor-række (speciel formatering)
        tf = self.parser.taylor_fact(expr) # forsøg Taylor-formatering
        raw = tf if tf is not None else self.parser.evaluate(expr)  # evaluer
        
        formatted = self.parser.format_output(raw)  # pæn formatering af resultat
        self.second_display.setText(expr)   # vis originalt udtryk i sekundært display
        self.display.setText(formatted)     # vis resultat i hoveddisplay
        self.expression = ""                # ryd gemt udtryk (klar til næste)

    def _on_esc(self):
        # Hvorfor: ESC-knap: rydder display og viser "Cleared" midlertidigt
        # Funktioner: Rydder udtryk, viser bekræftelse i 600 ms
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: display, second_display, expression
        
        self._clear_expr()                 # ryd hoveddisplay og udtryk
        self.second_display.setText("Cleared")  # vis "Cleared" i sekundært display
        # Timer: efter 600 millisekunder, ryd sekundært display
        QTimer.singleShot(600, lambda: self.second_display.setText(""))

    # ── function keys ───────────────────────────────────────────

    def _on_fkey(self, key: str):
        # Hvorfor: Håndterer F1-F6 funktionstaster
        # Funktioner: F5 skifter mellem normal og 2nd-mode, andre indsætter skabeloner
        # Parametre: key (string) - "F1", "F2", ..., "F6"
        # Returnerer: Intet
        # Data påvirket: second_mode, mode_label, expression, display, parser.variables
        
        if key == "F5":                    # F5 = 2nd mode toggle
            self.second_mode = not self.second_mode  # skift mellem True/False
            self._update_math_btns()       # opdater matematikknapperne (skift tekst)
            suffix = "2nd" if self.second_mode else "12:45"  # vis status
            self.mode_label.setText(f"  AUTO  │  RAD  │  {suffix}")  # opdater status
            return                         # afslut (F5 gør ikke andet)

        template = self.F_TEMPLATES.get(key)  # hent skabelon for denne F-tast
        if template is None:               # hvis ingen skabelon (burde ikke ske)
            return                         # afslut

        if template == "__CLEAR__":        # specialværdi: ryd alle variable
            self.parser.variables.clear()  # tøm parserens variabelordbog
            self.second_display.setText("Variables cleared")  # bekræft
            self._clear_expr()             # ryd display
            # Efter 800 ms, ryd bekræftelsesbeskeden
            QTimer.singleShot(800, lambda: self.second_display.setText(""))
            return

        # Indsæt skabelon i udtrykket (f.eks. "expand(")
        self.expression += template
        cursor_pos = len(self.expression) - 1  # position før sidste tegn
        self.display.setText(self.expression)  # opdater display
        # Flyt cursor til den smarte position (før lukkeparentes)
        QTimer.singleShot(10, lambda p=cursor_pos: self.display.setCursorPosition(p))

    def _update_math_btns(self):
        # Hvorfor: Opdaterer alle matematikknapper når 2nd-mode aktiveres/deaktiveres
        # Funktioner: Skifter tekst og styling på alle matematikknapper
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Hver knaps tekst og styling i _math_btns
        
        for (r, c), btn in self._math_btns.items():  # loop over alle matematikknapper
            primary, secondary = self.MATH_FUNCS[r][c]  # hent primær/sekundær tekst
            if self.second_mode:             # hvis 2nd-mode er aktiv
                btn.setText(secondary)       # sæt knappens tekst til sekundær funktion
                btn.setStyleSheet(FUNC2_STYLE)  # anvend blå 2nd-stil
            else:                            # normal mode
                btn.setText(primary)         # sæt knappens tekst til primær funktion
                btn.setStyleSheet(FUNC_STYLE)  # anvend guld normal-stil

    def _on_math(self, primary: str, secondary: str):
        # Hvorfor: Håndterer tryk på matematikknapper (sin, cos, sqrt, etc.)
        # Funktioner: Indsætter den aktuelle funktion (primær eller sekundær) i displayet
        # Parametre: primary (string) - primær funktion, secondary (string) - sekundær
        # Returnerer: Intet
        # Data påvirket: expression, display, second_mode (deaktiveres efter brug)
        
        text = secondary if self.second_mode else primary  # vælg primær eller sekundær
        
        # Map visningssymboler til faktisk syntax
        sym_map = {"÷": "/", "×": "*", "−": "-", "²": "^2",
                   "∫(": "integrate(", "∞": "oo", "ans": "last"}
        insert = sym_map.get(text, text)   # konverter eller behold original
        
        self._append(insert)               # indsæt i displayet
        
        if self.second_mode:               # hvis 2nd-mode var aktiv
            self.second_mode = False       # deaktiver 2nd-mode (kun ét tryk)
            self._update_math_btns()       # opdater knapper tilbage til normal
            self.mode_label.setText("  AUTO  │  RAD  │  12:45")  # opdater status

    # ── keyboard input ──────────────────────────────────────────

    def keyPressEvent(self, event):
        # Hvorfor: Håndterer tastaturinput (overrider QMainWindow's metode)
        # Funktioner: Oversætter tastetryk til handlinger (F1-F6, Enter, piletaster)
        # Parametre: event (QKeyEvent) - tastaturhændelse med information om tastetryk
        # Returnerer: Intet
        # Data påvirket: expression, display (via _append, _on_btn, etc.)
        
        key = event.key()                  # hent tastens Qt-nøgle (f.eks. Qt.Key_F1)
        text = event.text()                # hent den faktiske tekst (f.eks. "a")
        mods = event.modifiers()           # hent modifier-taster (Shift, Ctrl, Alt)

        # Map Qt F1-F6 konstanter til vores F-key navne
        fkey_map = {
            Qt.Key_F1: "F1", Qt.Key_F2: "F2", Qt.Key_F3: "F3",
            Qt.Key_F4: "F4", Qt.Key_F5: "F5", Qt.Key_F6: "F6",
        }
        if key in fkey_map:                # hvis det er en F-tast
            self._on_fkey(fkey_map[key])   # kald F-key handler
            return                         # afslut (yderligere behandling unødvendig)

        # Håndter Enter/Return taster
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._on_btn("ENTER")          # evaluer udtryk
        
        elif key == Qt.Key_Escape:         # Escape tast
            self._on_esc()                 # ryd display
        
        elif key == Qt.Key_Backspace:      # Backspace tast
            self._on_btn("DEL")            # slet sidste tegn
        
        elif key == Qt.Key_Delete:         # Delete tast
            self._clear_expr()             # ryd hele displayet
        
        elif key == Qt.Key_Left:           # venstre pil
            cur = self.display.cursorPosition()  # få nuværende cursorposition
            self.display.setCursorPosition(max(0, cur - 1))  # flyt en venstre
        
        elif key == Qt.Key_Right:          # højre pil
            cur = self.display.cursorPosition()
            self.display.setCursorPosition(min(len(self.expression), cur + 1))
        
        elif key == Qt.Key_Up:             # op pil
            self._on_btn("UP")             # historik op
        
        elif key == Qt.Key_Down:           # ned pil
            self._on_btn("DOWN")           # historik ned
        
        elif text:                         # hvis der er almindelig tekst (bogstav/tal)
            # Bevar store bogstaver for E og I (SymPy konstanter), ellers som de er
            if text in ('E', 'I'):         # Eulers tal og imaginær enhed
                char = text                # behold som uppercase
            elif key == Qt.Key_AsciiCircum:  # ^ tegn (potens)
                char = "^"                 # brug ^ direkte
            else:
                char = text                # brug teksten som den er (Qt håndterer Shift)
            self._append(char)             # indsæt tegnet i displayet

    # ── dialogs ─────────────────────────────────────────────────

    def _dialog_base(self, title: str, w: int = 460, h: int = 580) -> QDialog:
        # Hvorfor: Opretter en standarddialog med fælles styling og størrelse
        # Funktioner: Returnerer en QDialog klar til at blive udfyldt med indhold
        # Parametre: title (string) - dialogvinduets titel, w/h - bredde/højde
        # Returnerer: QDialog objekt
        # Data påvirket: Opretter nyt dialogvindue (ingen eksisterende data)
        
        dlg = QDialog(self)                # opret dialog med MainWindow som forælder
        dlg.setWindowTitle(title)          # sæt titel
        dlg.setFixedSize(w, h)             # sæt fast størrelse
        dlg.setStyleSheet("""              # anvend CSS styling
            QDialog { background-color: #222; }
            QLabel  { color: #ddd; font-size: 13px; }
            QGroupBox {
                color: #c8a000; font-size: 13px; font-weight: bold;
                border: 2px solid #9a7000; border-radius: 5px;
                margin-top: 14px; padding: 12px 8px 8px 8px;
            }
            QGroupBox::title {
                color: #c8a000;
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 4px;
            }
            QPushButton {
                background-color: #383838; color: #eee;
                border: 1px solid #555; border-radius: 3px;
                padding: 9px 12px; text-align: left; font-size: 12px;
            }
            QPushButton:hover  { background-color: #505050; }
            QPushButton:pressed { background-color: #282828; }
            QRadioButton { color: #ddd; }
        """)
        return dlg                         # returnér den færdige dialog

    def _scrolled_dialog(self, dlg: QDialog) -> QVBoxLayout:
        # Hvorfor: Tilføjer scrollbar til en dialog (når der er meget indhold)
        # Funktioner: Indkapsler dialogens indhold i et scroll-område
        # Parametre: dlg (QDialog) - dialogen der skal have scroll
        # Returnerer: QVBoxLayout - layout inde i scrollområdet (til at tilføje widgets)
        # Data påvirket: Dialogens layout ændres
        
        scroll = QScrollArea()             # opret scroll-område
        scroll.setWidgetResizable(True)    # tillad at indhold ændrer størrelse
        scroll.setStyleSheet("QScrollArea { border: none; background: #222; }")
        content = QWidget()                # widget der holder indholdet
        layout = QVBoxLayout(content)      # vertikalt layout til indhold
        layout.setSpacing(8)               # 8 pixels mellem elementer
        scroll.setWidget(content)          # sæt content som scrollområdets widget
        
        # FIX #6: brug en lokal variabel, ikke dlg.layout (som er en metode)
        dlg_layout = QVBoxLayout(dlg)      # opret nyt layout til dialogen
        dlg_layout.setContentsMargins(0, 0, 0, 0)  # ingen margen
        dlg_layout.addWidget(scroll)       # tilføj scrollområde til dialog
        
        return layout                      # returnér layout (til at tilføje widgets)

    def _insert_and_close(self, dlg: QDialog, text: str):
        # Hvorfor: Indsætter tekst i displayet og lukker en dialog
        # Funktioner: Hjælpefunktion til dialogknapper (én handling)
        # Parametre: dlg (QDialog) - dialogen der skal lukkes, text (string) - tekst der indsættes
        # Returnerer: Intet
        # Data påvirket: expression, display (via _append), dialog lukkes
        
        self._append(text)                 # indsæt tekst i displayet
        dlg.close()                        # luk dialogen

    # ── MODE dialog ─────────────────────────────────────────────

    def _on_mode(self):
        # Hvorfor: Viser Mode-dialog hvor brugeren kan vælge radianer/grader
        # Funktioner: Opretter dialog med radioknapper for vinkeltilstand
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: parser.degree_mode (opdateres når brugeren vælger)
        
        dlg = self._dialog_base("Mode Settings", w=300, h=260)  # mindre dialog
        dlg_layout = QVBoxLayout(dlg)      # vertikalt layout til dialogen

        # Gruppe til vinkelindstillinger
        angle_group = QGroupBox("Angle Mode")  # gruppeboks med titel
        ag = QVBoxLayout()                 # vertikalt layout i gruppen
        rad_btn = QRadioButton("RAD — Radians")  # radioknap til radianer
        deg_btn = QRadioButton("DEG — Degrees")  # radioknap til grader
        
        # FIX #1 + FIX #12: synkroniser med parserens tilstand (standard RAD)
        rad_btn.setChecked(not self.parser.degree_mode)  # True hvis radianer
        deg_btn.setChecked(self.parser.degree_mode)      # True hvis grader
        
        # Forbind toggled signal: når rad_btn ændres, opdater parser.degree_mode
        rad_btn.toggled.connect(lambda checked: setattr(self.parser, 'degree_mode', not checked))
        
        ag.addWidget(rad_btn)              # tilføj radian-knap til layout
        ag.addWidget(deg_btn)              # tilføj grad-knap til layout
        angle_group.setLayout(ag)          # sæt layout i gruppen
        dlg_layout.addWidget(angle_group)  # tilføj gruppe til dialog

        # Gruppe til display-format (AUTO/APPROX) - fremtidig funktionalitet
        fmt_group = QGroupBox("Display Format")
        fg = QVBoxLayout()
        auto_btn = QRadioButton("AUTO")
        approx_btn = QRadioButton("APPROX — force decimal")
        auto_btn.setChecked(True)          # AUTO som standard
        fg.addWidget(auto_btn)
        fg.addWidget(approx_btn)
        fmt_group.setLayout(fg)
        dlg_layout.addWidget(fmt_group)

        ok_btn = QPushButton("OK")         # OK knap til at lukke
        ok_btn.clicked.connect(dlg.close)  # luk dialog når der klikkes
        dlg_layout.addWidget(ok_btn)
        
        dlg.exec()                         # vis dialog (modal - blokerer indtil lukket)

    # ── APPS dialog ─────────────────────────────────────────────

    def _on_apps(self):
        # Hvorfor: Viser Applications-dialog med matematikværktøjer og variabelhåndtering
        # Funktioner: Opretter dialog med knapper til factor, expand, solve, etc.
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Kan ændre variable via _run_cmd, eller indsætte funktioner
        
        dlg = self._dialog_base("Applications & Utilities")  # opret dialog
        layout = self._scrolled_dialog(dlg)  # scrollbart layout

        # Math utilities gruppe
        math_grp = QGroupBox("Math Utilities")
        mg = QVBoxLayout()
        for label, insert in [              # liste af (visningsnavn, indsæt-tekst)
            ("factor(expr)   — Factorize",          "factor("),
            ("expand(expr)   — Expand",              "expand("),
            ("simplify(expr) — Simplify",            "simplify("),
            ("trigsimp(expr) — Trig simplify",       "trigsimp("),
            ("solve(eq,x)    — Solve equation",      "solve("),
            ("dsolve(eq)     — Diff. equation",      "dsolve("),
        ]:
            b = QPushButton(label)          # opret knap med label
            # Forbind til _insert_and_close (indsæt og luk dialog)
            b.clicked.connect(lambda _, t=insert, d=dlg: self._insert_and_close(d, t))
            mg.addWidget(b)                 # tilføj knap til layout
        
        math_grp.setLayout(mg)              # sæt layout i gruppen
        layout.addWidget(math_grp)          # tilføj gruppe til hovedlayout

        # Variables & history gruppe
        var_grp = QGroupBox("Variables & History")
        vg = QVBoxLayout()
        for label, cmd in [                 # liste af (visningsnavn, kommando)
            ("Show all variables",   "vars"),
            ("Show history",         "history"),
            ("Recall last result",   "last"),
            ("Clear all variables",  "clear"),
        ]:
            b = QPushButton(label)          # opret knap
            # FIX #13: evaluer kommandoen og luk dialog
            b.clicked.connect(lambda _, c=cmd, d=dlg: (
                self._run_cmd(c), d.close()  # udfør kommando, luk dialog
            ))
            vg.addWidget(b)                 # tilføj knap
        
        var_grp.setLayout(vg)               # sæt layout
        layout.addWidget(var_grp)           # tilføj gruppe

        close_b = QPushButton("Close")      # luk-knap
        close_b.setStyleSheet("text-align: center;")  # centrer tekst
        close_b.clicked.connect(dlg.close)  # luk dialog
        layout.addWidget(close_b)           # tilføj knap
        
        dlg.exec()                          # vis dialog

    def _run_cmd(self, cmd: str):
        # Hvorfor: Udfører en indbygget kommando (vars, history, last, clear)
        # Funktioner: Evaluerer kommandoen via parser og viser resultatet
        # Parametre: cmd (string) - kommandoen der skal udføres
        # Returnerer: Intet
        # Data påvirket: display, expression, parser (via evaluate)
        
        result = self.parser.evaluate(cmd)  # evaluer kommandoen
        self.display.setText(result)        # vis resultat i hoveddisplay
        self.expression = ""                # ryd gemt udtryk

    # ── PRGM dialog ─────────────────────────────────────────────

    def _on_prgm(self):
        # Hvorfor: Viser Programs-dialog med enhedsomregninger og formler
        # Funktioner: Opretter dialog med konverteringer (km→miles, °C→°F, etc.)
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Indsætter konverteringsudtryk i displayet
        
        dlg = self._dialog_base("Programs & Utilities")
        layout = self._scrolled_dialog(dlg)

        # Unit Conversions gruppe
        conv_grp = QGroupBox("Unit Conversions")
        cg = QVBoxLayout()
        for label, expr in [                # liste af (visningsnavn, udtryk)
            ("km → miles      x · 0.621371",   "x*0.621371"),
            ("miles → km      x · 1.60934",    "x*1.60934"),
            ("°C → °F         x·9/5 + 32",     "x*9/5+32"),
            ("°F → °C         (x−32)·5/9",     "(x-32)*5/9"),
            ("kg → lbs        x · 2.20462",    "x*2.20462"),
            ("lbs → kg        x · 0.453592",   "x*0.453592"),
            ("m → ft          x · 3.28084",    "x*3.28084"),
            ("ft → m          x / 3.28084",    "x/3.28084"),
        ]:
            b = QPushButton(label)          # opret knap
            b.clicked.connect(lambda _, t=expr, d=dlg: self._insert_and_close(d, t))
            cg.addWidget(b)
        
        conv_grp.setLayout(cg)
        layout.addWidget(conv_grp)

        # Quick Formulas gruppe
        formula_grp = QGroupBox("Quick Formulas")
        fg = QVBoxLayout()
        for label, expr in [
            ("Quadratic roots   solve(a·x²+b·x+c,x)", "solve(a*x**2+b*x+c,x)"),
            ("Hypotenuse        sqrt(a²+b²)",           "sqrt(a**2+b**2)"),
            ("Circle area       π·r²",                  "pi*r**2"),
            ("Sphere volume     4/3·π·r³",              "4/3*pi*r**3"),
            ("Kinetic energy    ½·m·v²",                "1/2*m*v**2"),
            ("Ohm's law         V/R",                   "V/R"),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, t=expr, d=dlg: self._insert_and_close(d, t))
            fg.addWidget(b)
        
        formula_grp.setLayout(fg)
        layout.addWidget(formula_grp)

        close_b = QPushButton("Close")
        close_b.setStyleSheet("text-align: center;")
        close_b.clicked.connect(dlg.close)
        layout.addWidget(close_b)
        
        dlg.exec()

    # ── CUSTOM dialog ───────────────────────────────────────────

    def _on_custom(self):
        # Hvorfor: Viser Custom-dialog med fysiske konstanter og udtryk
        # Funktioner: Opretter dialog med naturkonstanter (c, g, h, etc.) og formler
        # Parametre: Ingen (self)
        # Returnerer: Intet
        # Data påvirket: Indsætter konstantværdier eller udtryk i displayet
        
        dlg = self._dialog_base("Custom — Constants & Expressions")
        layout = self._scrolled_dialog(dlg)

        # Physics Constants gruppe
        const_grp = QGroupBox("Physics Constants")
        cg = QVBoxLayout()
        for label, val in [                 # liste af (visningsnavn, værdi)
            ("c  = speed of light  (m/s)",          "299792458"),
            ("g  = gravity         (m/s²)",          "9.80665"),
            ("G  = gravitational constant",           "6.67430e-11"),
            ("h  = Planck constant (J·s)",           "6.62607015e-34"),
            ("e  = electron charge (C)",             "1.602176634e-19"),
            ("Nₐ = Avogadro number",                 "6.02214076e23"),
            ("k  = Boltzmann       (J/K)",           "1.380649e-23"),
            ("R  = gas constant    (J/mol·K)",       "8.314462618"),
            ("ε₀ = vacuum permittivity (F/m)",       "8.854187817e-12"),
            ("μ₀ = vacuum permeability (H/m)",       "1.256637061e-6"),
            ("α  = fine structure constant",          "7.2973525693e-3"),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, v=val, d=dlg: self._insert_and_close(d, v))
            cg.addWidget(b)
        
        const_grp.setLayout(cg)
        layout.addWidget(const_grp)

        # Quick Expressions gruppe
        expr_grp = QGroupBox("Quick Expressions")
        eg = QVBoxLayout()
        for label, expr in [
            ("Quadratic formula  (−b±√(b²−4ac))/2a", "(-b+sqrt(b**2-4*a*c))/(2*a)"),
            ("Circle area        π·r²",               "pi*r**2"),
            ("Sphere volume      4/3·π·r³",           "4/3*pi*r**3"),
            ("Pythagorean c      sqrt(a²+b²)",        "sqrt(a**2+b**2)"),
            ("Compound interest  P·(1+r)ⁿ",          "P*(1+r)**n"),
            ("Normal dist.       exp(−x²/2)/√(2π)",  "exp(-x**2/2)/sqrt(2*pi)"),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, t=expr, d=dlg: self._insert_and_close(d, t))
            eg.addWidget(b)
        
        expr_grp.setLayout(eg)
        layout.addWidget(expr_grp)

        close_b = QPushButton("Close")
        close_b.setStyleSheet("text-align: center;")
        close_b.clicked.connect(dlg.close)
        layout.addWidget(close_b)
        
        dlg.exec()
# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
#  Programstart: Opretter QApplication og MainWindow, starter event-loop
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Hvorfor: Sikrer at koden kun kører når filen køres direkte (ikke importeres)
    # Funktioner: Initialiserer Qt applikation, håndterer platform-specifikke indstillinger
    
    import os                           # importer operativsystem-modul til miljøvariable

    # Håndter Linux/macOS uden grafisk skærm (f.eks. CI/CD miljøer)
    if sys.platform != "win32":         # hvis ikke Windows
        # Tjek om DISPLAY eller WAYLAND_DISPLAY er sat (indikerer grafisk miljø)
        if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
            # Hvis ingen skærm, brug "offscreen" platform (headless mode)
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    # Opret Qt applikation (skal ske før nogen GUI-widgets oprettes)
    app = QApplication(sys.argv)        # sys.argv giver kommandolinjeargumenter videre

    # Vælg en passende system-skrifttype baseret på platform
    font = QFont()                      # standard skrifttype-objekt
    if sys.platform == "win32":         # Windows
        font.setFamily("Segoe UI")      # Windows standard skrift
    elif sys.platform == "darwin":      # macOS (darwin er kernel-navnet)
        font.setFamily("Helvetica Neue")  # macOS standard skrift
    else:                               # Linux og andre
        font.setFamily("Ubuntu")        # populær Linux skrift
    font.setPointSize(10)               # skriftstørrelse 10 punkter
    app.setFont(font)                   # anvend som applikations standard skrift

    # Opret hovedvinduet (MainWindow instans)
    window = MainWindow()               # konstruktøren bygger hele GUI'en
    window.show()                       # gør vinduet synligt på skærmen

    # Start Qt event-loop (programmet kører her indtil vinduet lukkes)
    sys.exit(app.exec())                # app.exec() starter event-loop, sys.exit() returnerer exit-kode
