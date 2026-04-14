# CASCalc
Do your math on the computer

# TI-89 Style CAS Calculator – Professional Edition

A fully featured Computer Algebra System (CAS) calculator built with
PySide6 and SymPy, modeled after the Texas Instruments TI-89. Supports
symbolic mathematics, variable storage, history navigation, unit
conversions, physical constants, and an interactive GUI with 2nd
function keys.

## Table of Contents

1. Overview
2. Core Features
3. Complete Function Reference
4. User Interface Guide
5. Keyboard Shortcuts
6. Command Reference
7. Installation & Requirements
8. Usage Examples
9. Code Architecture
10. Data Structures
11. Extending the Program
12. License

## 1. Overview

This program is a professional-grade CAS calculator that performs
symbolic and numeric mathematics. Unlike basic calculators, it can
manipulate algebraic expressions, solve equations analytically,
differentiate and integrate symbolically, and work with variables.
The interface mimics the TI-89 layout with a green monochrome
display, function keys (F1–F6), and a comprehensive set of math
buttons.

The core mathematical engine is SymPy, a Python library for symbolic
mathematics. The GUI is built with PySide6 (Qt6 bindings). The
program handles parsing, variable substitution, degree/radian
conversion, and pretty-printing of results (Unicode fractions, sqrt
symbols, π, i, etc.).

## 2. Core Features

### Symbolic Mathematics
- Differentiation (`diff(expr, x)`)
- Integration (`integrate(expr, x)`)
- Equation solving (`solve(eq, x)`)
- Differential equations (`dsolve(eq)`)
- Series expansion (`series(expr, x, 0, n)` or `taylor`)
- Limits (`limit(expr, x, 0)`)
- Simplification (`simplify`, `trigsimp`)
- Expansion (`expand`)
- Factorization (`factor`, `factorint`)

### Variable Management
- Store variables: `a := 5` or `a = 5`
- List variables: `vars`
- Clear all: `clear`
- Variables persist until cleared or program exits

### History System
- Every evaluated expression is stored
- Arrow up/down recalls previous expressions
- `history` command shows all entries
- `last` command recalls the previous result

### Angle Modes
- Radians (default) – standard mathematical mode
- Degrees – converts `30°` to `π/6` automatically
- Mode dialog accessible via `MODE` button

### Unit Conversions (PRGM menu)
- Kilometers ↔ miles
- Celsius ↔ Fahrenheit
- Kilograms ↔ pounds
- Meters ↔ feet
- Quadratic formula, circle area, sphere volume, kinetic energy,
  Ohm's law

### Physical Constants (CUSTOM menu)
- Speed of light (c), gravity (g), gravitational constant (G)
- Planck constant (h), electron charge (e), Avogadro number (Nₐ)
- Boltzmann constant (k), gas constant (R)
- Vacuum permittivity (ε₀), permeability (μ₀)
- Fine-structure constant (α)

### Output Formatting
- Unicode fractions: ½, ⅓, ⅔, ¼, ¾, ⅕, ⅖, ⅗, ⅘, ⅙, ⅛, ⅜, ⅝, ⅞
- Square root symbol: `√` instead of `sqrt()`
- Pi symbol: `π` instead of `pi`
- Imaginary unit: `i` instead of `I`
- Multiplication dot: `·` for `*`
- Powers: `^` instead of `**`
- Taylor series show `n!` notation

## 3. Complete Function Reference

### Basic Arithmetic
| Button | Operation | Example |
|--------|-----------|---------|
| + | Addition | `2+3` → `5` |
| − | Subtraction | `5-2` → `3` |
| × | Multiplication | `3*4` → `12` |
| ÷ | Division | `8/2` → `4` |
| ^ | Power | `2^3` → `8` |
| √ | Square root | `√16` → `4` |
| x² | Square | `5²` → `25` |
| x³ | Cube | `3³` → `27` |
| 1/x | Reciprocal | `1/4` → `0.25` |

### Trigonometric Functions (mode dependent)
| Primary | Secondary (2nd) | Description |
|---------|----------------|-------------|
| sin | sinh | Sine / hyperbolic sine |
| cos | cosh | Cosine / hyperbolic cosine |
| tan | tanh | Tangent / hyperbolic tangent |
| asin | asinh | Arcsin / inverse hyperbolic |
| acos | acosh | Arccos / inverse hyperbolic |
| atan | atanh | Arctan / inverse hyperbolic |

### Logarithmic & Exponential
| Function | Description |
|----------|-------------|
| ln | Natural logarithm (base e) |
| log | Base-10 logarithm |
| log2 | Base-2 logarithm |
| log10 | Base-10 logarithm (alias) |
| exp | Exponential function e^x |
| e^x | Same as exp (2nd function) |
| 10^x | Power of 10 (2nd function) |

### Algebraic Operations
| Function | Description | Example |
|----------|-------------|---------|
| expand() | Expand products/powers | `expand((x+1)^2)` → `x^2+2x+1` |
| factor() | Factor polynomials | `factor(x^2-1)` → `(x-1)(x+1)` |
| simplify() | Simplify expression | `simplify(x+x)` → `2x` |
| trigsimp() | Trigonometric simplification | `trigsimp(sin(x)^2+cos(x)^2)` → `1` |

### Calculus
| Function | Description | Example |
|----------|-------------|---------|
| diff(expr, x) | Differentiate | `diff(x^2, x)` → `2x` |
| integrate(expr, x) | Integrate | `integrate(x^2, x)` → `x^3/3` |
| limit(expr, x, 0) | Limit | `limit(1/x, x, oo)` → `0` |
| series(expr, x, 0, n) | Taylor series | `series(sin(x), x, 0, 5)` |
| taylor() | Alias for series | Same as above |
| dsolve(eq) | Diff equation | `dsolve(y(x).diff(x)-y(x))` |

### Equation Solving
| Function | Description | Example |
|----------|-------------|---------|
| solve(eq, x) | Solve equation | `solve(x^2-4, x)` → `[-2, 2]` |
| solve([eq1,eq2], [x,y]) | System of equations | `solve([x+y=2, x-y=0], [x,y])` |

### Constants
| Symbol | Value | Description |
|--------|-------|-------------|
| π (pi) | 3.14159... | Pi, circle constant |
| e (E) | 2.71828... | Euler's number |
| i (I) | √(-1) | Imaginary unit |
| ∞ (oo) | Infinity | Infinite value |

### Special Commands
| Command | Description |
|---------|-------------|
| vars | List all stored variables |
| history | Show evaluation history |
| last | Recall the previous result |
| clear | Delete all variables |

## 4. User Interface Guide

### Main Display (Green Screen)
- Shows the current expression being entered
- Right-aligned text like a classic TI-89
- Read/write – you can type directly or use buttons
- Monospace font (Courier New) for proper alignment

### Secondary Display (Result Area)
- Shows the last evaluated expression (input)
- Read-only – displays what was just computed
- Below the main display, smaller font

### Mode Indicator Bar
- Displays `AUTO` – automatic evaluation mode
- `RAD` or `DEG` – current angle unit
- Time or `2nd` indicator when second functions are active

### Function Keys (F1–F6)

| Key | Normal Mode | 2nd Mode (F5 toggles) |
|-----|-------------|----------------------|
| F1 | `expand()` | (same) |
| F2 | `diff(,x)` | (same) |
| F3 | `solve(,x)` | (same) |
| F4 | `()` | (same) |
| F5 | Toggle 2nd mode | Return to normal |
| F6 | Clear all variables | (same) |

### Button Groups

**Navigation Row (Row 0)**
- `ESC` – Clear display, show "Cleared"
- `APPS` – Open applications dialog (math utilities, variables)
- `PRGM` – Open programs dialog (unit conversions, formulas)
- `MODE` – Open mode settings (radians/degrees)
- `DEL` – Delete last character
- `▲` – Recall previous history entry (up arrow)
- `▼` – Recall next history entry (down arrow)

**Number Pad (Rows 1–4)**
- Digits 0–9, decimal point
- Basic operators +, −, ×, ÷
- Negation button `(-)` inserts `(-` for negative expressions

**Cursor Controls**
- `◀` – Move cursor left
- `▶` – Move cursor right

**ENTER Button**
- Tall blue button on the right
- Evaluates the current expression
- Shows result in main display, input in secondary display

**Variable Quick-Insert Row**
- `x`, `y`, `t`, `n` – Common symbolic variables
- `°` – Degree symbol (converts to `*(pi/180)`)
- `π` – Pi constant

**Math Function Grid (6 rows × 4–6 columns)**
- Normal mode: primary functions (gold buttons)
- 2nd mode: secondary functions (blue buttons)
- Pressing a 2nd-mode button automatically disables 2nd mode
- Functions include sin, cos, tan, ln, log, sqrt, x², x³, ^,
  parentheses, solve, factor, expand, diff, ∫, limit, π, e, ans, i

### Dialog Windows

**APPS Dialog** – Scrollable window with:
- Math utilities: factor, expand, simplify, trigsimp, solve, dsolve
- Variables & history: show variables, show history, recall last,
  clear all variables

**PRGM Dialog** – Unit conversions and formulas:
- Length: km↔miles, m↔ft
- Temperature: °C↔°F
- Mass: kg↔lbs
- Geometry: quadratic roots, hypotenuse, circle area, sphere volume
- Physics: kinetic energy, Ohm's law

**MODE Dialog** – Settings:
- Angle mode: RAD (radians) or DEG (degrees)
- Display format: AUTO (symbolic) or APPROX (decimal)
- OK button to close

**CUSTOM Dialog** – Constants and expressions:
- Physics constants (15 values)
- Quick expressions: quadratic formula, circle area, sphere volume,
  Pythagorean theorem, compound interest, normal distribution

## 5. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F1–F6 | Function keys (expand, diff, solve, (), 2nd, clear) |
| Enter / Return | Evaluate expression |
| Escape (Esc) | Clear display, show "Cleared" |
| Backspace | Delete last character |
| Delete | Clear entire display |
| Left Arrow | Move cursor left |
| Right Arrow | Move cursor right |
| Up Arrow | Recall previous history entry |
| Down Arrow | Recall next history entry |
| 0–9, ., +, -, *, / | Direct typing |
| ^ | Power operator (caret) |
| ( ) | Parentheses |
| E, I | Uppercase constants (Euler, Imaginary) |

## 6. Command Reference

All commands are case-insensitive (typed in lowercase).

### Variable Assignment

a := 5
Assigns value 5 to variable a. The `:=` operator is preferred for
explicit assignment. Simple `=` also works for short variable names
(1–2 letters) but avoid confusion with comparison operators.

b := 2*x
Stores the symbolic expression `2*x` in variable b.

result := integrate(x^2, x)
Stores the result of symbolic integration.

### Variable Display

vars: Lists all stored variables in the format `a = 5`, `b = 2*x`.
history :Shows all previously evaluated expressions in order.
last: Recalls and re-evaluates the previous expression (second-to-last
      history entry). 

### Clearing
clear: Deletes all user-defined variables. The `clr` alias also works.
F6 button: Same as `clear` command.

## 7. Installation & Requirements

### System Requirements
- Python 3.8 or higher
- Operating system: Windows, macOS, Linux
- Graphics environment (X11 on Linux, native on Windows/macOS)
- Headless mode supported via `QT_QPA_PLATFORM=offscreen`

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | 6.x | Qt6 bindings for GUI |
| SymPy | 1.9+ | Symbolic mathematics engine |
| Python standard libs | – | re, math, sys, os |

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ti89-cas-calculator.git
   cd ti89-cas-calculator
2. Install required packages:
   pip install pyside6 sympy
3. Run the calculator:
   python cascalc_commented.py

Linux Headless Mode
For servers or environments without a display:
export QT_QPA_PLATFORM=offscreen
python cascalc_commented.py

The program will run but no GUI will appear (useful for testing).

8. Usage Examples
Basic Arithmetic
Input: 2+3*4
Output: 14 (multiplication before addition)

Input: (2+3)*4
Output: 20

Variables
Input: a := 5
Output: a = 5

Input: b := 2*a
Output: b = 10

Input: vars
Output:
a = 5
b = 10
Trigonometry (Radians)
Input: sin(pi/2)
Output: 1

Trigonometry (Degrees)
Press MODE, select DEG, click OK

Input: sin(30°)
Output: 0.5

Differentiation
Input: diff(x^3, x)
Output: 3*x^2

Input: diff(sin(x), x)
Output: cos(x)

Integration
Input: integrate(x^2, x)
Output: x^3/3

Input: integrate(sin(x), x)
Output: -cos(x)

Definite Integration
Input: integrate(x^2, (x, 0, 1))
Output: 1/3 (displayed as ⅓)

Equation Solving
Input: solve(x^2 - 4, x)
Output: [-2, 2]

Input: solve(x^2 + 2*x + 1, x)
Output: [-1]

System of Equations
Input: solve([x+y=2, x-y=0], [x,y])
Output: {x:1, y:1}

Differential Equations
Input: dsolve(y(x).diff(x) - y(x))
Output: Eq(y(x), C1*exp(x))

Taylor Series
Input: series(sin(x), x, 0, 5)
Output: x - x^3/6 + O(x^5)
Then formatted as: x - x^3/3! + O(x^5)

Limits
Input: limit(1/x, x, oo)
Output: 0

Input: limit(sin(x)/x, x, 0)
Output: 1

Factorials
Input: factorial(5)
Output: 120

Binomial Coefficients
Input: binomial(5, 2)
Output: 10

Unit Conversion (via PRGM)
Click PRGM, then "km → miles". The expression x*0.621371 is
inserted. Replace x with a number: 100*0.621371 → 62.1371.

Physical Constants (via CUSTOM)
Click CUSTOM, then "c = speed of light". The value 299792458
is inserted. Use in calculations: 299792458 * 2 → 599584916.

Complex Numbers
Input: sqrt(-1)
Output: i

Input: (2 + 3*i) * (1 - i)
Output: 5 + i

Output Formatting Examples
1/2 → ½

2/4 → ½ (automatic simplification)

sqrt(16) → √16

pi → π

x**2 → x^2

2*pi → 2·π

3*I → 3·i

9. Code Architecture
Module Overview
cascalc_commented.py
├── Imports (PySide6, SymPy, sys, re, math)
├── CalculatorParser class
│   ├── __init__ – initialize variables, history, SymPy namespace
│   ├── preprocess – convert °, implicit multiplication, ^ to **
│   ├── evaluate – evaluate expressions, handle commands, assignments
│   ├── format_output – Unicode formatting (√, π, i, fractions)
│   ├── taylor_fact – detect Taylor series
│   └── _format_taylor_fact – convert 1/6 to 1/3!
├── CalculatorDisplay class (QLineEdit subclass)
│   └── __init__ – set green TI-89 style, monospace font
├── Button helper functions
│   ├── _style – generate CSS for buttons
│   ├── _make_btn – factory for standardized buttons
│   └── Predefined styles (NUM_STYLE, OP_STYLE, FUNC_STYLE, etc.)
└── MainWindow class (QMainWindow subclass)
    ├── __init__ – initialize parser, expression, second_mode
    ├── _apply_window_style – global CSS styling
    ├── _build_ui – construct entire interface
    ├── _append – add text to display
    ├── _clear_expr – clear expression
    ├── _on_btn – handle ENTER, DEL, NEG, arrows
    ├── _evaluate – evaluate current expression
    ├── _on_esc – clear display with feedback
    ├── _on_fkey – handle F1–F6 (expand, diff, solve, 2nd, clear)
    ├── _update_math_btns – toggle primary/secondary math buttons
    ├── _on_math – handle math button clicks (sin, cos, etc.)
    ├── keyPressEvent – keyboard input handler
    ├── _dialog_base – create standard dialog
    ├── _scrolled_dialog – add scroll area to dialog
    ├── _insert_and_close – insert text and close dialog
    ├── _on_mode – mode dialog (radians/degrees)
    ├── _on_apps – applications dialog (math utilities)
    ├── _run_cmd – execute built-in commands
    ├── _on_prgm – programs dialog (unit conversions)
    └── _on_custom – custom dialog (constants & expressions)

Data Flow
User input (keyboard or button) → _append() or _on_btn()

Expression stored in MainWindow.expression

Press ENTER → _evaluate() called

Expression sent to CalculatorParser.evaluate()

preprocess() converts ° to *(pi/180), adds implicit *

eval() executed in SymPy namespace

Result formatted with format_output() or taylor_fact()

Formatted result displayed in main display

Original expression shown in secondary display

Expression added to parser.history

10. Data Structures
CalculatorParser.variables
Type: dict[str, str]

Example: {'a': '5', 'b': '2*x', 'result': '10'}

Stores user-defined variables as strings

CalculatorParser.history
Type: list[str]

Example: ['2+2', 'sin(pi/2)', 'x^2+3*x+2']

Stores all evaluated expressions in order

CalculatorParser.degree_mode
Type: bool

False = radians (default), True = degrees

CalculatorParser._sympy_ns
Type: dict[str, object]

Maps names to SymPy functions/constants: {'sin': sin, 'pi': pi, ...}

MainWindow.expression
Type: str

Current expression in the display

MainWindow.second_mode
Type: bool

False = normal mode, True = 2nd functions active

MainWindow._math_btns
Type: dict[tuple[int,int], QPushButton]

Maps grid positions to math function buttons

MATH_FUNCS (class constant)
Type: list[list[tuple[str,str]]]

6 rows × 4–6 columns of (primary, secondary) function names

F_TEMPLATES (class constant)
Type: dict[str, str]

Maps F1–F6 to template strings or "__CLEAR__" sentinel

11. Extending the Program
Adding New Math Functions
1. Add the function to CalculatorParser._sympy_ns in __init__:
   self._sympy_ns["newfunc"] = sp.newfunc
2. Add a button in MainWindow.MATH_FUNCS:
   [("newfunc", "newfunc2"), ...]
3. The button will appear automatically in the math grid.

Adding New Constants
1. Add to _on_custom dialog in the Physics Constants list:
   ("new constant name", "value"),
2. Or add directly to _sympy_ns for symbolic constants:
   self._sympy_ns["newconst"] = sp.Symbol('newconst')

Adding Unit Conversions
Add to _on_prgm dialog in the Unit Conversions list:
("unit1 → unit2    formula", "expression_with_x"),

Changing Output Formatting
Modify CalculatorParser.format_output():

Add new regex substitutions for special symbols

Extend the frac_map dictionary for more Unicode fractions

Add new replacements for sqrt, pi, I, etc.

Adding New Commands
Add to CalculatorParser.evaluate():
if cmd == 'mycommand':
    # perform action
    return "result"
Changing Button Styles
Modify the _style() function or the predefined style constants:

NUM_STYLE – number buttons (dark gray)

OP_STYLE – operators (lighter gray)

FUNC_STYLE – math functions (gold)

FUNC2_STYLE – 2nd functions (blue)

ENTER_STYLE – ENTER button (blue)

MENU_STYLE – menu buttons (dark)

VAR_STYLE – variable buttons (green)

Adding New Dialog Windows
Use the _dialog_base() method to create a standard dialog:
def _on_mydialog(self):
    dlg = self._dialog_base("My Dialog", w=400, h=300)
    layout = self._scrolled_dialog(dlg)  # if scroll needed
    # Add widgets to layout
    dlg.exec()

12. License
This program is open source and provided for educational purposes.
You may use, modify, and distribute it freely. The code includes
detailed comments in Danish and English to facilitate learning.

No warranty is provided. The author is not responsible for any
calculation errors or bugs.

Credits
Built with Qt6 (PySide6) – GUI framework

SymPy – Symbolic mathematics engine

Inspired by Texas Instruments TI-89 graphing calculator
