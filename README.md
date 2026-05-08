# ♩ LoopBeat

A music-inspired programming language built for rhythm-based applications.

LoopBeat is a fully interpreted, domain-specific language with its own lexer, parser, AST, and interpreter — all running inside a custom dark-themed IDE built with Python and tkinter.

---

## What is LoopBeat?

LoopBeat is designed around the concepts of rhythm, timing, and repetition. Variable names like `tempo`, `beat`, and `pattern` feel natural in LoopBeat programs. The language enforces strong typing and predictable execution so developers can focus on musical logic rather than debugging silent errors.

---

## Features

- **6 data types** — `int`, `float`, `string`, `bool`, `list`, `none`
- **Functions** — `func` keyword, parameters, `return`, recursion, closures
- **Control flow** — `if / else`, `while`, `for-in`, `break`
- **Operators** — `+ - * / %` and `== != < > <= >=` and `and or not`
- **Strong typing** — no silent type conversions, all errors are explicit
- **Line-number error messages** — every error tells you exactly where it happened
- **Built-in functions** — `print()`, `len()`, `str()`, `int()`, `float()`, `type()`, `append()`
- **Comments** — single-line with `#`
- **Full IDE** — editor, token viewer, AST viewer, and test suite runner

---

## Language Syntax

### Variables
```
tempo = 120
name  = "kick"
playing = true
pattern = ["kick", "snare", "hat"]
```

### Functions
```
func greet(name) {
    print("Hey " + name)
}

func factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

greet("DJ Ana")
print(factorial(5))
```

### Control Flow
```
# if / else
if tempo > 120 {
    print("Fast beat!")
} else {
    print("Chill beat.")
}

# while loop
i = 0
while i < 4 {
    print(i)
    i = i + 1
}

# for-in loop
for sound in pattern {
    print(sound)
}
```

### Beat Sequencer Example
```
func playBeat(sound, step) {
    print("Step " + str(step) + " -> " + sound)
}

func runSequence(pattern) {
    i = 0
    for b in pattern {
        playBeat(b, i)
        i = i + 1
    }
}

kicks  = ["kick", "kick", "rest", "kick"]
snares = ["rest", "snare", "rest", "snare"]

print("=== 128 BPM ===")
runSequence(kicks)
runSequence(snares)
```

---

## Error Handling

LoopBeat stops immediately on any error and prints a descriptive message with the line number.

| Error | Example | Message |
|-------|---------|---------|
| Undefined variable | `print(volume)` | `Runtime error: 'volume' is not defined` |
| Division by zero | `x = 10 / 0` | `Runtime error: Division by zero` |
| Type mismatch | `x = "beat" - 1` | `Runtime error: '-' requires integers` |
| Bad condition | `if 1 { }` | `Runtime error: if condition must be bool` |
| Illegal character | `x = 5 @ 2` | `[Line 1] Invalid character: '@'` |

---

## Project Structure

```
LoopBeats/
  lexer.py          ← Tokenizes source code into a token stream
  parser.py         ← Builds an Abstract Syntax Tree (AST)
  interpreter.py    ← Walks the AST and evaluates the program
  gui.py            ← tkinter IDE with editor, tabs, and test runner
  tests/
    valid/          ← 10 valid .lb programs
    invalid/        ← 5 invalid .lb programs (expected to error)
```

---

## How to Run

**Requirements:** Python 3.x (no external libraries needed)

```bash
# Clone the repo
git clone https://github.com/GarcaA6100/LoopBeats.git
cd LoopBeats

# Launch the IDE
python gui.py
```

You can also run `.lb` files from the command line (if you have `main.py`):
```bash
python main.py run tests/valid/valid1.lb
```

---

## Architecture

```
Source Code (.lb)
      │
      ▼
   Lexer          → converts characters into tokens
      │
      ▼
   Parser         → builds an Abstract Syntax Tree (AST)
      │
      ▼
  Interpreter     → walks the AST and evaluates each node
      │
      ▼
   Output
```

---

## IDE

The LoopBeat IDE (`gui.py`) includes:

- **Editor** — write or load `.lb` files directly
- **▶ Output tab** — see program results with color-coded success/error
- **⬡ Tokens tab** — inspect every token the lexer produces
- **⎇ AST tab** — view the full Abstract Syntax Tree
- **✓ Tests tab** — run all valid and invalid test files at once

---

## Intentionally Not Supported

- Semicolons (newlines end statements)
- Classes or inheritance (by design — LoopBeat is not OOP)
- Implicit type conversions (strong typing is a core principle)
- Fixed-size arrays (lists cover all use cases)

---

## Course

Principles of Programming Languages — Spring 2026
