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
    - Brug := til at tildele variabler værdier, f.eks. a := 5.

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
# --- CONFIG & CONSTANTS -------------------------------------------------
import sys
import re
import math as _math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QPushButton, QLabel, QDialog,
    QGroupBox, QRadioButton, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

import sympy as sp
from sympy import (
    symbols, Function, simplify, expand, factor, solve,
    integrate, diff, sqrt, sin, cos, tan, log, Abs,
    factorial, binomial, pi, E, I, series, limit, oo,
    Rational, Mul, Pow
)

# ---------------------------------------- MODELS & DATA LOGIC (Parser/Engine) -----------------------------------------
# ──────────────────────────────────────────────────────────────────────────────────────
#  PARSER / ENGINE
# ──────────────────────────────────────────────────────────────────────────────────────

class CalculatorParser:
    """Parser and symbolic evaluator for the CAS calculator."""

    def __init__(self):
        self.variables: dict = {} 		# Opret tom ordbog til brugerdefinerede variable (f.eks. a := 5)
        self.history: list = []			# Liste til at gemme historik over indtastede udtryk
        self.degree_mode: bool = False          # Standard vinkeltilstand: False = radianer, True = grader (fix #12)
        self.x = symbols('x')			# Symbolsk variabel 'x' bruges ofte i funktioner
        self.y = Function('y')			# Funktion 'y' til differentialligninger
        self._sympy_ns = {			# Namespace til eval() – her ligger alle SymPy-funktioner og konstanter
            "solve": solve, "sqrt": sqrt,
            "sin": sin, "cos": cos, "tan": tan,
            "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
            "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
            "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
            "log": lambda x: sp.log(x, 10),
            "ln": sp.log,
            "log2": lambda x: sp.log(x, 2),
            "log10": lambda x: sp.log(x, 10),
            "exp": sp.exp, "Abs": Abs,
            "cbrt": lambda x: sp.cbrt(x),
            "dsolve": sp.dsolve,
            "trigsimp": sp.trigsimp,
            "factorint": sp.factorint,
            "pi": pi, "E": E, "I": I, "e": E,
            "integrate": integrate, "diff": diff, "symbols": symbols,
            "expand": expand, "factor": factor, "simplify": simplify,
            "taylor": series, "series": series, "limit": limit, "oo": oo,
            "x": self.x, "y": self.y,
            "sp": sp,
        }

    # ── preprocessing ──────────────────────────────────────────

    def preprocess(self, expr: str) -> str:
        """Normalise notation: degrees, implicit multiplication, etc."""
        expr = expr.strip()

        # Degree conversion: n° → n*pi/180
        expr = re.sub(r'(\d+(?:\.\d+)?)°', r'(\1*pi/180)', expr)
        expr = expr.replace('°', '*(pi/180)')

        # Caret exponentiation
        expr = expr.replace('^', '**')

        # Tokenise (protect scientific notation)
        tokens = re.findall(
            r'\d+\.?\d*[eE][+-]?\d+|[a-zA-Z]\w*|\d+\.?\d*'
            r'|[\+\-\*/\^=,():]|\]|\[',
            expr
        )

        # Implicit multiplication: 2x → 2*x, x(... → x*(
        result = []
        for i, tok in enumerate(tokens):
            result.append(tok)
            if i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if re.match(r'.*[0-9a-zA-Zπ]$', tok) and re.match(r'^[a-zA-Zπ\(]', nxt):
                    # Don't insert * when tok is a function name followed by (
                    if not (nxt == '(' and re.match(r'^[a-zA-Z]', tok)):
                        result.append('*')
        return ''.join(result)

    # ── evaluation ─────────────────────────────────────────────

    def evaluate(self, expr: str) -> str:
        if not expr.strip():
            return ""

        self.history.append(expr)

        # Built-in commands
        cmd = expr.strip().lower()
        if cmd in ('clear', 'clr'):
            self.variables.clear()
            return "Variables cleared"
        if cmd in ('vars', 'variables'):
            if not self.variables:
                return "No variables stored"
            return "\n".join(f"{k} = {v}" for k, v in self.variables.items())
        if cmd == 'history':
            return "\n".join(str(h) for h in self.history) or "No history"
        if cmd == 'last':
            if len(self.history) >= 2:
                return self.evaluate(self.history[-2])
            return "No previous expression"

        # Variable assignment: name := expr
        if ':=' in expr:
            var_name, value_expr = expr.split(':=', 1)
            var_name = var_name.strip()
            result = self.evaluate(value_expr.strip())
            self.variables[var_name] = result
            try:
                self._sympy_ns[var_name] = sp.sympify(result)
            except Exception:
                pass
            return f"{var_name} = {result}"

        # Simple assignment: a = expr  (only single-letter or two-char names)
        if '=' in expr and not any(op in expr for op in ('==', '!=', '<=', '>=')):
            if expr.count('=') == 1:
                var_name, rest = expr.split('=', 1)
                var_name = var_name.strip()
                if var_name.isidentifier() and len(var_name) <= 2 and rest.strip():
                    result = self.evaluate(rest.strip())
                    self.variables[var_name] = result
                    try:
                        self._sympy_ns[var_name] = sp.sympify(result)
                    except Exception:
                        pass
                    return f"{var_name} = {result}"

        processed = self.preprocess(expr)

        try:
            result = eval(processed, {"__builtins__": {}}, self._sympy_ns)

            if hasattr(result, 'is_number') and result.is_number:
                if result in (sp.oo, -sp.oo, sp.zoo):
                    return "Division by Zero / Undefined"
                # 15-digit precision
                return str(result.evalf(15)).rstrip('0').rstrip('.')
            return str(result)
        except Exception as exc:
            return f"Error: {exc}"

    # ── output formatting ───────────────────────────────────────

    def format_output(self, result: str) -> str:
        """Pretty-print sympy output: fractions, radicals, Greek letters."""
        if not result:
            return ""

        s = str(result)

        # Add parentheses around base**exp before converting **→^
        if '**' in s:
            s = re.sub(r'([a-z]?\*\*\d+)/(\d+)',
                       lambda m: f'({m.group(1)})/{m.group(2)}', s)

        s = s.replace('**', '^')

        # Protect exponent-fractions from simplification
        protected: list[str] = []

        def _protect(m):
            protected.append(m.group(0))
            return f"__EP{len(protected)-1}__"

        s = re.sub(r'\^(\d+)\s*/\s*(\d+)', _protect, s)

        # Simplify plain integer fractions
        def _simplify_frac(m):
            try:
                num, den = int(m.group(1)), int(m.group(2))
                g = _math.gcd(num, den)
                num, den = num // g, den // g
                if den == 1:
                    return str(num)
                frac_map = {
                    '1/2': '½', '1/3': '⅓', '2/3': '⅔',
                    '1/4': '¼', '3/4': '¾',
                    '1/5': '⅕', '2/5': '⅖', '3/5': '⅗', '4/5': '⅘',
                    '1/6': '⅙', '1/8': '⅛', '3/8': '⅜',
                    '5/8': '⅝', '7/8': '⅞',
                }
                key = f'{num}/{den}'
                return frac_map.get(key, key)
            except Exception:
                return m.group(0)

        s = re.sub(r'\b(\d+)/(\d+)\b', _simplify_frac, s)

        for i, p in enumerate(protected):
            s = s.replace(f"__EP{i}__", p)

        # sqrt() → √
        s = re.sub(r'sqrt\((\d+)\)', r'√\1', s)
        s = re.sub(r'sqrt\(([^)]+)\)', r'√(\1)', s)

        # pi → π  (before I→i)
        s = s.replace('*pi', '·π').replace('pi', 'π')

        # Imaginary unit I → i
        s = s.replace('I*', 'i·').replace('*I', '·i')
        s = re.sub(r'\bI\b', 'i', s)

        # Euler E → e (not inside 'exp')
        s = re.sub(r'(?<!xp)\bE\b', 'e', s)

        return s

    # ── taylor series helper ────────────────────────────────────

    def taylor_fact(self, expr_str: str):
        """Evaluate and format a Taylor/series expression with n! denominators."""
        if not ('taylor' in expr_str or 'series' in expr_str):
            return None
        processed = self.preprocess(expr_str)
        try:
            result = eval(processed, {"__builtins__": {}}, self._sympy_ns)
            if hasattr(result, 'free_symbols') and result.free_symbols:
                return self._format_taylor_fact(result)
        except Exception:
            pass
        return None

    def _format_taylor_fact(self, expr) -> str:
        s = str(expr).replace('**', '^')

        def _to_fact(m):
            exp = int(m.group(1))
            den = int(m.group(2))
            expected = _math.factorial(exp)
            if den == expected:
                return f"x^{exp}/{exp}!"
            return m.group(0)

        s = re.sub(r'x\^(\d+)/(\d+)(?!!)', _to_fact, s)

        def _fix_o(m):
            exp = int(m.group(1))
            return f'O(x^{exp+1})' if exp % 2 == 0 else m.group(0)

        s = re.sub(r'O\(x\^(\d+)\)', _fix_o, s)
        return s


# ─────────────────────────────────────────────────────────────
#  DISPLAY WIDGET
# ─────────────────────────────────────────────────────────────

class CalculatorDisplay(QLineEdit):
    """Primary LCD display — dusty-green TI-89 screen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)           # Allow cursor positioning
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setFixedHeight(64)
        self.setFont(QFont("Courier New", 20, QFont.Weight.Bold))
        # Colour is set via stylesheet in MainWindow.TI_STYLE
        self.setObjectName("main_display")


# ─────────────────────────────────────────────────────────────
#  BUTTON HELPERS  (inline styles — CSS class workaround)
# ─────────────────────────────────────────────────────────────

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
    QPushButton:hover  {{ background-color: {hover}; }}
    QPushButton:pressed {{ background-color: {press}; border-bottom: 1px solid {border}; }}
"""

def _style(bg, fg, border, bot_color, hover, press, fsize=12, bot=3):
    return _BTN_BASE.format(
        bg=bg, fg=fg, border=border, bot=bot,
        bot_color=bot_color, hover=hover, press=press, fsize=fsize
    )

NUM_STYLE   = _style("#3c3c3c", "#e8e8e8", "#222", "#111", "#505050", "#282828", fsize=16)
OP_STYLE    = _style("#5a5a5a", "#ffffff", "#404040", "#2a2a2a", "#6e6e6e", "#464646", fsize=18)
FUNC_STYLE  = _style("#9a7000", "#111111", "#7a5800", "#5a3e00", "#c49a10", "#7a5800", fsize=10)
FUNC2_STYLE = _style("#3a3a7a", "#ffff55", "#2a2a5a", "#1a1a3a", "#5050aa", "#2a2a5a", fsize=10)
ENTER_STYLE = _style("#1a4a7a", "#ffffff", "#0a3060", "#061e4a", "#2a5a8a", "#0a3060", fsize=13, bot=4)
MENU_STYLE  = _style("#2e2e2e", "#cccccc", "#1a1a1a", "#0a0a0a", "#424242", "#1c1c1c", fsize=11)
VAR_STYLE   = _style("#2a4a2a", "#88ff88", "#1a3a1a", "#0e2a0e", "#3a5e3a", "#1a3a1a", fsize=13)


def _make_btn(label: str, style: str, w: int = 52, h: int = 44) -> QPushButton:
    btn = QPushButton(label)
    btn.setFixedSize(w, h)
    btn.setStyleSheet(style)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """CAS Calculator — TI-89 Professional Layout."""

    # ── function-key templates ──────────────────────────────────
    F_TEMPLATES = {
        "F1": "expand()",
        "F2": "diff(,x)",
        "F3": "solve(,x)",
        "F4": "()",
        "F6": "__CLEAR__",
    }
    F_LABELS = "  F1:expand  F2:diff  F3:solve  F4:( )  F5:2nd  F6:clr"

    # ── math button definitions: (primary, secondary) ──────────
    #   FIX #8: asin↔asinh, acos↔acosh (were swapped before)
    #   FIX #7: row 5 replaced duplicates with useful entries
    MATH_FUNCS = [
        [("sin",      "sinh"),    ("cos",     "cosh"),    ("tan",    "tanh"),   ("ln",      "log10")],
        [("asin",     "asinh"),   ("acos",    "acosh"),   ("atan",   "atanh"),  ("log",     "log2")],
        [("sqrt",     "cbrt"),    ("x²",      "1/x"),     ("x³",     "x^y"),    ("^",       "10^x")],
        [("(",        "|x|"),     (")",       "!"),        ("solve(", "dsolve("),("factor(", "factorint(")],
        [("expand(",  "simplify("),("diff(",  "taylor("), ("∫(",     "limit("), (",",        "==")],
        [("π",        "2π"),      ("e",       "e^x"),     ("ans",    "last"),   ("i",       "∞")],
    ]

    def __init__(self):
        super().__init__()
        self.parser = CalculatorParser()
        self.expression = ""
        self.second_mode = False
        self._math_btns: dict = {}      # (row, col) → QPushButton

        self.setWindowTitle("CheapCAS  ·  TI-89 CAS Calculator")
        self.setFixedSize(480, 840)
        self._apply_window_style()
        self._build_ui()

    # ── window-level stylesheet ─────────────────────────────────

    def _apply_window_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#central {
                background-color: #1c1c1c;
            }
            QLineEdit#main_display {
                background-color: #97b597;
                color: #0d1f0d;
                border: 3px solid #3a3a3a;
                border-radius: 5px;
                padding: 6px 10px;
                font-family: 'Courier New', monospace;
                font-size: 20px;
                font-weight: bold;
            }
            QLineEdit#second_display {
                background-color: #7ea07e;
                color: #0d1f0d;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 3px 8px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
        """)

    # ── UI construction ─────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setSpacing(3)
        root.setContentsMargins(6, 6, 6, 6)

        # Status bar
        self.mode_label = QLabel("  AUTO  │  RAD  │  12:45")
        self.mode_label.setStyleSheet(
            "background:#111; color:#00ee77; font-family:'Courier New';"
            "font-size:11px; padding:3px 8px; border:1px solid #333;"
        )
        root.addWidget(self.mode_label)

        # Main display
        self.display = CalculatorDisplay()
        root.addWidget(self.display)

        # Second (result) display
        self.second_display = QLineEdit()
        self.second_display.setReadOnly(True)
        self.second_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.second_display.setFixedHeight(32)
        self.second_display.setObjectName("second_display")
        root.addWidget(self.second_display)

        # ── F1–F6 row ──────────────────────────────────────────
        frow = QHBoxLayout()
        frow.setSpacing(2)
        for f in ("F1", "F2", "F3", "F4", "F5", "F6"):
            b = _make_btn(f, FUNC_STYLE, w=68, h=38)
            b.clicked.connect(lambda _, k=f: self._on_fkey(k))
            frow.addWidget(b)
        root.addLayout(frow)

        self.func_label = QLabel(self.F_LABELS)
        self.func_label.setStyleSheet(
            "color:#888; font-family:'Courier New'; font-size:9px; padding:1px 2px;"
        )
        root.addWidget(self.func_label)

        # ── Variable & constant quick-insert row ────────────────
        vrow = QHBoxLayout()
        vrow.setSpacing(2)
        for v in ("x", "y", "t", "n"):
            b = _make_btn(v, VAR_STYLE, w=44, h=36)
            b.clicked.connect(lambda _, c=v: self._append(c))
            vrow.addWidget(b)
        for v in ("°", "π"):
            b = _make_btn(v, VAR_STYLE, w=44, h=36)
            b.clicked.connect(lambda _, c=v: self._append(c))
            vrow.addWidget(b)
        vrow.addStretch()
        root.addLayout(vrow)

        # ── Main button grid ────────────────────────────────────
        # Authentic TI-89 layout:
        #
        #   Col:  0       1       2       3       4       5       6
        # Row 0:  ESC    APPS    PRGM    MODE    DEL     ▲       ▼
        # Row 1:  [2nd]   7       8       9       ÷      [CUSTOM ────]
        # Row 2:  [ ]     4       5       6       ×       ◀       ▶
        # Row 3:  [ ]     1       2       3       −      (-)     [ ]
        # Row 4:  [ ]    [0 ──────────]   .       +      [ENTER ──────]
        # Row 5:  [ ]    [ ]     [ ]     [ ]    [ ]      [ ]    [ ]

        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setContentsMargins(0, 2, 0, 2)

        # Row 0 — navigation / control
        for col, (lbl, action) in enumerate([
            ("ESC",  self._on_esc),
            ("APPS", self._on_apps),
            ("PRGM", self._on_prgm),
            ("MODE", self._on_mode),
            ("DEL",  lambda: self._on_btn("DEL")),
            ("▲",    lambda: self._on_btn("UP")),
            ("▼",    lambda: self._on_btn("DOWN")),
        ]):
            b = _make_btn(lbl, MENU_STYLE, w=56, h=38)
            b.clicked.connect(action)
            grid.addWidget(b, 0, col)

        # Row 1 — 7 8 9 ÷  CUSTOM
        for col, lbl in enumerate(("7", "8", "9"), start=1):
            b = _make_btn(lbl, NUM_STYLE)
            b.clicked.connect(lambda _, c=lbl: self._append(c))
            grid.addWidget(b, 1, col)
        b = _make_btn("÷", OP_STYLE)
        b.clicked.connect(lambda: self._append("/"))
        grid.addWidget(b, 1, 4)
        custom_b = _make_btn("CUSTOM", ENTER_STYLE, w=112, h=44)
        custom_b.clicked.connect(self._on_custom)
        grid.addWidget(custom_b, 1, 5, 1, 2)

        # Row 2 — 4 5 6 ×  ◀ ▶
        for col, lbl in enumerate(("4", "5", "6"), start=1):
            b = _make_btn(lbl, NUM_STYLE)
            b.clicked.connect(lambda _, c=lbl: self._append(c))
            grid.addWidget(b, 2, col)
        b = _make_btn("×", OP_STYLE)
        b.clicked.connect(lambda: self._append("*"))
        grid.addWidget(b, 2, 4)
        b = _make_btn("◀", MENU_STYLE)
        b.clicked.connect(lambda: self._on_btn("LEFT"))
        grid.addWidget(b, 2, 5)
        b = _make_btn("▶", MENU_STYLE)
        b.clicked.connect(lambda: self._on_btn("RIGHT"))
        grid.addWidget(b, 2, 6)

        # Row 3 — 1 2 3 −  (-)
        for col, lbl in enumerate(("1", "2", "3"), start=1):
            b = _make_btn(lbl, NUM_STYLE)
            b.clicked.connect(lambda _, c=lbl: self._append(c))
            grid.addWidget(b, 3, col)
        b = _make_btn("−", OP_STYLE)
        b.clicked.connect(lambda: self._append("-"))
        grid.addWidget(b, 3, 4)
        b = _make_btn("(-)", MENU_STYLE)
        b.clicked.connect(lambda: self._on_btn("NEG"))
        grid.addWidget(b, 3, 5)

        # Row 4 — 0(wide)  .  +  ENTER(tall)
        b = _make_btn("0", NUM_STYLE, w=160, h=44)
        b.clicked.connect(lambda: self._append("0"))
        grid.addWidget(b, 4, 1, 1, 3)
        b = _make_btn(".", NUM_STYLE)
        b.clicked.connect(lambda: self._append("."))
        grid.addWidget(b, 4, 4)
        b = _make_btn("+", OP_STYLE)
        b.clicked.connect(lambda: self._append("+"))
        grid.addWidget(b, 4, 5)
        enter_b = _make_btn("ENTER", ENTER_STYLE, w=56, h=88)
        enter_b.clicked.connect(lambda: self._on_btn("ENTER"))
        grid.addWidget(enter_b, 4, 6, 2, 1)   # spans rows 4–5

        root.addLayout(grid)

        # ── Math / CAS function buttons ─────────────────────────
        math_grid = QGridLayout()
        math_grid.setSpacing(2)
        math_grid.setContentsMargins(0, 2, 0, 0)

        for r, row in enumerate(self.MATH_FUNCS):
            for c, (primary, secondary) in enumerate(row):
                b = _make_btn(primary, FUNC_STYLE, w=108, h=40)
                b.clicked.connect(lambda _, p=primary, s=secondary: self._on_math(p, s))
                math_grid.addWidget(b, r, c)
                self._math_btns[(r, c)] = b

        root.addLayout(math_grid)

    # ── event routing ───────────────────────────────────────────

    def _append(self, text: str):
        """Append text to expression and refresh display."""
        self.expression += text
        self.display.setText(self.expression)

    def _clear_expr(self):
        self.expression = ""
        self.display.setText("")

    def _on_btn(self, text: str):
        if text == "ENTER":
            self._evaluate()
        elif text == "DEL":
            self.expression = self.expression[:-1]
            self.display.setText(self.expression)
        elif text == "NEG":
            # FIX #3: insert balanced negative sign group
            self.expression += "(-"
            self.display.setText(self.expression)
        elif text in ("UP", "DOWN"):
            # Scroll history
            if self.parser.history:
                idx = -1 if text == "UP" else -2
                try:
                    self.display.setText(self.parser.history[idx])
                except IndexError:
                    pass
        elif text in ("LEFT", "RIGHT"):
            cur = self.display.cursorPosition()
            self.display.setCursorPosition(cur + (1 if text == "RIGHT" else -1))

    def _evaluate(self):
        expr = self.display.text().strip()   # Honour any manual edits
        self.expression = expr
        if not expr:
            return
        # Taylor shortcut
        tf = self.parser.taylor_fact(expr)
        raw = tf if tf is not None else self.parser.evaluate(expr)
        formatted = self.parser.format_output(raw)
        self.second_display.setText(expr)
        self.display.setText(formatted)
        self.expression = ""

    def _on_esc(self):
        self._clear_expr()
        self.second_display.setText("Cleared")
        QTimer.singleShot(600, lambda: self.second_display.setText(""))

    # ── function keys ───────────────────────────────────────────

    def _on_fkey(self, key: str):
        if key == "F5":
            self.second_mode = not self.second_mode
            self._update_math_btns()
            suffix = "2nd" if self.second_mode else "12:45"
            self.mode_label.setText(f"  AUTO  │  RAD  │  {suffix}")
            return

        template = self.F_TEMPLATES.get(key)
        if template is None:
            return

        if template == "__CLEAR__":
            self.parser.variables.clear()
            self.second_display.setText("Variables cleared")
            self._clear_expr()
            QTimer.singleShot(800, lambda: self.second_display.setText(""))
            return

        # Insert template; position cursor before closing paren/bracket
        self.expression += template
        cursor_pos = len(self.expression) - 1  # before last char
        self.display.setText(self.expression)
        QTimer.singleShot(10, lambda p=cursor_pos: self.display.setCursorPosition(p))

    def _update_math_btns(self):
        for (r, c), btn in self._math_btns.items():
            primary, secondary = self.MATH_FUNCS[r][c]
            if self.second_mode:
                btn.setText(secondary)
                btn.setStyleSheet(FUNC2_STYLE)
            else:
                btn.setText(primary)
                btn.setStyleSheet(FUNC_STYLE)

    def _on_math(self, primary: str, secondary: str):
        text = secondary if self.second_mode else primary
        # Map display symbols to actual syntax
        sym_map = {"÷": "/", "×": "*", "−": "-", "²": "^2",
                   "∫(": "integrate(", "∞": "oo", "ans": "last"}
        insert = sym_map.get(text, text)
        self._append(insert)
        if self.second_mode:
            self.second_mode = False
            self._update_math_btns()
            self.mode_label.setText("  AUTO  │  RAD  │  12:45")

    # ── keyboard input ──────────────────────────────────────────

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        mods = event.modifiers()

        fkey_map = {
            Qt.Key_F1: "F1", Qt.Key_F2: "F2", Qt.Key_F3: "F3",
            Qt.Key_F4: "F4", Qt.Key_F5: "F5", Qt.Key_F6: "F6",
        }
        if key in fkey_map:
            self._on_fkey(fkey_map[key])
            return

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._on_btn("ENTER")
        elif key == Qt.Key_Escape:
            self._on_esc()
        elif key == Qt.Key_Backspace:
            self._on_btn("DEL")
        elif key == Qt.Key_Delete:
            self._clear_expr()
        elif key == Qt.Key_Left:
            cur = self.display.cursorPosition()
            self.display.setCursorPosition(max(0, cur - 1))
        elif key == Qt.Key_Right:
            cur = self.display.cursorPosition()
            self.display.setCursorPosition(min(len(self.expression), cur + 1))
        elif key == Qt.Key_Up:
            self._on_btn("UP")
        elif key == Qt.Key_Down:
            self._on_btn("DOWN")
        elif text:
            # FIX #15: preserve case for E, I constants; lower rest
            if text in ('E', 'I'):
                char = text          # keep uppercase for sympy constants
            elif key == Qt.Key_AsciiCircum:
                char = "^"
            else:
                char = text          # let Qt handle shift state naturally
            self._append(char)

    # ── dialogs ─────────────────────────────────────────────────

    def _dialog_base(self, title: str, w: int = 460, h: int = 580) -> QDialog:
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setFixedSize(w, h)
        dlg.setStyleSheet("""
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
        return dlg

    def _scrolled_dialog(self, dlg: QDialog) -> QVBoxLayout:
        """Return a vbox layout inside a scroll area filling the dialog."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #222; }")
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)
        scroll.setWidget(content)
        # FIX #6: use a local var, not dialog.layout (which is a method)
        dlg_layout = QVBoxLayout(dlg)
        dlg_layout.setContentsMargins(0, 0, 0, 0)
        dlg_layout.addWidget(scroll)
        return layout

    def _insert_and_close(self, dlg: QDialog, text: str):
        """Insert text into expression and close the dialog."""
        self._append(text)
        dlg.close()

    # ── MODE dialog ─────────────────────────────────────────────

    def _on_mode(self):
        dlg = self._dialog_base("Mode Settings", w=300, h=260)
        dlg_layout = QVBoxLayout(dlg)

        angle_group = QGroupBox("Angle Mode")
        ag = QVBoxLayout()
        rad_btn = QRadioButton("RAD — Radians")
        deg_btn = QRadioButton("DEG — Degrees")
        # FIX #1 + FIX #12: sync with parser state (default RAD)
        rad_btn.setChecked(not self.parser.degree_mode)
        deg_btn.setChecked(self.parser.degree_mode)
        rad_btn.toggled.connect(lambda checked: setattr(self.parser, 'degree_mode', not checked))
        ag.addWidget(rad_btn)
        ag.addWidget(deg_btn)
        angle_group.setLayout(ag)
        dlg_layout.addWidget(angle_group)

        fmt_group = QGroupBox("Display Format")
        fg = QVBoxLayout()
        auto_btn = QRadioButton("AUTO")
        approx_btn = QRadioButton("APPROX — force decimal")
        auto_btn.setChecked(True)
        fg.addWidget(auto_btn)
        fg.addWidget(approx_btn)
        fmt_group.setLayout(fg)
        dlg_layout.addWidget(fmt_group)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dlg.close)
        dlg_layout.addWidget(ok_btn)
        dlg.exec()

    # ── APPS dialog ─────────────────────────────────────────────

    def _on_apps(self):
        dlg = self._dialog_base("Applications & Utilities")
        layout = self._scrolled_dialog(dlg)

        # Math utilities
        math_grp = QGroupBox("Math Utilities")
        mg = QVBoxLayout()
        for label, insert in [
            ("factor(expr)   — Factorize",          "factor("),
            ("expand(expr)   — Expand",              "expand("),
            ("simplify(expr) — Simplify",            "simplify("),
            ("trigsimp(expr) — Trig simplify",       "trigsimp("),
            ("solve(eq,x)    — Solve equation",      "solve("),
            ("dsolve(eq)     — Diff. equation",      "dsolve("),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, t=insert, d=dlg: self._insert_and_close(d, t))
            mg.addWidget(b)
        math_grp.setLayout(mg)
        layout.addWidget(math_grp)

        # Variables & history
        var_grp = QGroupBox("Variables & History")
        vg = QVBoxLayout()
        for label, cmd in [
            ("Show all variables",   "vars"),
            ("Show history",         "history"),
            ("Recall last result",   "last"),
            ("Clear all variables",  "clear"),
        ]:
            b = QPushButton(label)
            # FIX #13: actually evaluate the command
            b.clicked.connect(lambda _, c=cmd, d=dlg: (
                self._run_cmd(c), d.close()
            ))
            vg.addWidget(b)
        var_grp.setLayout(vg)
        layout.addWidget(var_grp)

        close_b = QPushButton("Close")
        close_b.setStyleSheet("text-align: center;")
        close_b.clicked.connect(dlg.close)
        layout.addWidget(close_b)
        dlg.exec()

    def _run_cmd(self, cmd: str):
        """Evaluate a built-in command and show result on display."""
        result = self.parser.evaluate(cmd)
        self.display.setText(result)
        self.expression = ""

    # ── PRGM dialog ─────────────────────────────────────────────

    def _on_prgm(self):
        dlg = self._dialog_base("Programs & Utilities")
        layout = self._scrolled_dialog(dlg)

        conv_grp = QGroupBox("Unit Conversions")
        cg = QVBoxLayout()
        for label, expr in [
            ("km → miles      x · 0.621371",   "x*0.621371"),
            ("miles → km      x · 1.60934",    "x*1.60934"),
            ("°C → °F         x·9/5 + 32",     "x*9/5+32"),
            ("°F → °C         (x−32)·5/9",     "(x-32)*5/9"),
            ("kg → lbs        x · 2.20462",    "x*2.20462"),
            ("lbs → kg        x · 0.453592",   "x*0.453592"),
            ("m → ft          x · 3.28084",    "x*3.28084"),
            ("ft → m          x / 3.28084",    "x/3.28084"),
        ]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, t=expr, d=dlg: self._insert_and_close(d, t))
            cg.addWidget(b)
        conv_grp.setLayout(cg)
        layout.addWidget(conv_grp)

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
        dlg = self._dialog_base("Custom — Constants & Expressions")
        layout = self._scrolled_dialog(dlg)

        const_grp = QGroupBox("Physics Constants")
        cg = QVBoxLayout()
        for label, val in [
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
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    if sys.platform != "win32":
        # On Linux/macOS default to xcb/wayland; offscreen only for CI
        if "DISPLAY" not in os.environ and "WAYLAND_DISPLAY" not in os.environ:
            os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication(sys.argv)

    # Pick a sensible system font
    font = QFont()
    if sys.platform == "win32":
        font.setFamily("Segoe UI")
    elif sys.platform == "darwin":
        font.setFamily("Helvetica Neue")
    else:
        font.setFamily("Ubuntu")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
