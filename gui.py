"""
LoopBeat IDE — Full Version
============================
Run: python gui.py
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import os, sys

from lexer       import Lexer,  LexerError
from parser      import Parser, ParseError
from interpreter import Interpreter

DARK   = "#1e1e2e"
PANEL  = "#181825"
LINE   = "#24243a"
FG     = "#cdd6f4"
MUTED  = "#6c7086"
ACCENT = "#cba6f7"
GREEN  = "#a6e3a1"
RED    = "#f38ba8"
TEAL   = "#94e2d5"
YELLOW = "#f9e2af"
MONO   = ("Consolas", 12)
UI     = ("Segoe UI", 10)

SAMPLES = {
    "1. Hello World": '# Hello World\nprint("Hello, LoopBeat!")',

    "2. Data Types": (
        '# All data types\n'
        'myInt    = 42\n'
        'myFloat  = 3.14\n'
        'myString = "kick"\n'
        'myBool   = true\n'
        'myNone   = none\n'
        'myList   = [1, 2, 3]\n'
        'print(myInt)\n'
        'print(myFloat)\n'
        'print(myString)\n'
        'print(myBool)\n'
        'print(myNone)\n'
        'print(myList)'
    ),

    "3. Arithmetic & Modulo": (
        'tempo = 120\n'
        'beat  = tempo + 10\n'
        'half  = tempo / 2\n'
        'mod   = tempo % 7\n'
        'print(beat)\n'
        'print(half)\n'
        'print(mod)'
    ),

    "4. String Operations": (
        'name    = "Loop"\n'
        'name2   = "Beat"\n'
        'full    = name + name2\n'
        'print(full)\n'
        'print(len(full))\n'
        'print(type(full))'
    ),

    "5. If / Else": (
        'tempo = 140\n'
        'if tempo > 120 {\n'
        '    print("Fast beat!")\n'
        '} else {\n'
        '    print("Chill beat.")\n'
        '}'
    ),

    "6. While Loop": (
        'i = 1\n'
        'while i <= 4 {\n'
        '    print(i)\n'
        '    i = i + 1\n'
        '}'
    ),

    "7. For Loop + List": (
        'pattern = ["kick", "snare", "hat", "clap"]\n'
        'for sound in pattern {\n'
        '    print(sound)\n'
        '}'
    ),

    "8. Functions": (
        'func greet(name) {\n'
        '    print("Hey " + name)\n'
        '}\n\n'
        'func add(a, b) {\n'
        '    return a + b\n'
        '}\n\n'
        'greet("DJ Ana")\n'
        'result = add(40, 2)\n'
        'print(result)'
    ),

    "9. Recursion": (
        'func factorial(n) {\n'
        '    if n <= 1 {\n'
        '        return 1\n'
        '    }\n'
        '    return n * factorial(n - 1)\n'
        '}\n\n'
        'print(factorial(5))\n'
        'print(factorial(6))'
    ),

    "10. Beat Sequencer": (
        '# LoopBeat Sequencer\n'
        'func playBeat(sound, step) {\n'
        '    print("Step " + str(step) + " -> " + sound)\n'
        '}\n\n'
        'func runSequence(pattern) {\n'
        '    i = 0\n'
        '    for sound in pattern {\n'
        '        playBeat(sound, i)\n'
        '        i = i + 1\n'
        '    }\n'
        '}\n\n'
        'kicks  = ["kick",  "kick",  "rest", "kick"]\n'
        'snares = ["rest",  "snare", "rest", "snare"]\n'
        'print("=== 128 BPM ===")\n'
        'runSequence(kicks)\n'
        'runSequence(snares)'
    ),

    "11. Error: Undefined Var": 'print(volume)',
    "12. Error: Div by Zero":   'x = 10 / 0',
    "13. Error: Type Mismatch": 'x = "beat" - 1',
    "14. Error: Bad Condition": 'if 1 { print("bad") }',
    "15. Error: Illegal Char":  'x = 5 @ 2',
}


class LoopBeatIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LoopBeat IDE  ♩  — Full Version")
        self.geometry("1100x720")
        self.configure(bg=DARK)
        self.resizable(True, True)
        self.interp = Interpreter()
        self._build_ui()
        self._load_sample("1. Hello World")

    def _build_ui(self):
        # top bar
        bar = tk.Frame(self, bg=PANEL, pady=6)
        bar.pack(fill="x")

        tk.Label(bar, text="  ♩ LoopBeat IDE", bg=PANEL,
                 fg=ACCENT, font=("Segoe UI", 13, "bold")).pack(side="left")

        self.sample_var = tk.StringVar(value="1. Hello World")
        om = tk.OptionMenu(bar, self.sample_var, *SAMPLES, command=self._load_sample)
        om.config(bg=LINE, fg=FG, activebackground=ACCENT, activeforeground=DARK,
                  highlightthickness=0, font=UI, bd=0, relief="flat")
        om["menu"].config(bg=LINE, fg=FG, font=UI,
                          activebackground=ACCENT, activeforeground=DARK)
        om.pack(side="left", padx=(16,4))
        tk.Label(bar, text="Samples", bg=PANEL, fg=MUTED, font=UI).pack(side="left")

        tk.Button(bar, text="Open .lb", bg=LINE, fg=MUTED, font=UI,
                  relief="flat", bd=0, padx=10, pady=4,
                  cursor="hand2", command=self._open_file).pack(side="left", padx=8)

        tk.Button(bar, text="Run Tests", bg=LINE, fg=YELLOW, font=UI,
                  relief="flat", bd=0, padx=10, pady=4,
                  cursor="hand2", command=self._run_tests).pack(side="right", padx=4)

        tk.Button(bar, text="▶  Run", bg=ACCENT, fg=DARK,
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", bd=0, padx=16, pady=4,
                  cursor="hand2", command=self._run).pack(side="right", padx=12)

        # paned
        pane = tk.PanedWindow(self, orient="horizontal", bg=DARK, sashwidth=4)
        pane.pack(fill="both", expand=True)

        # LEFT: editor
        left = tk.Frame(pane, bg=DARK)
        pane.add(left, width=500)
        tk.Label(left, text="  Editor  (.lb)", bg=PANEL, fg=MUTED,
                 font=UI, anchor="w").pack(fill="x")
        self.editor = scrolledtext.ScrolledText(
            left, bg=PANEL, fg=FG, insertbackground=ACCENT,
            font=MONO, relief="flat", bd=0,
            selectbackground=ACCENT, selectforeground=DARK,
            wrap="none", undo=True, padx=12, pady=8)
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<Tab>",
            lambda e: (self.editor.insert("insert","    "),"break")[1])
        self.editor.bind("<KeyRelease>", self._update_status)
        self.status_var = tk.StringVar(value="Ln 1  Col 1")
        tk.Label(left, textvariable=self.status_var, bg=DARK, fg=MUTED,
                 font=("Segoe UI",9), anchor="w", padx=8).pack(fill="x")

        # RIGHT: notebook
        right = tk.Frame(pane, bg=DARK)
        pane.add(right, width=580)
        style = ttk.Style(); style.theme_use("default")
        style.configure("TNotebook",     background=PANEL, borderwidth=0)
        style.configure("TNotebook.Tab", background=LINE, foreground=MUTED,
                        padding=[12,4],  font=UI)
        style.map("TNotebook.Tab",
                  background=[("selected",DARK)], foreground=[("selected",FG)])
        nb = ttk.Notebook(right); nb.pack(fill="both", expand=True)
        self.out_tab  = self._make_tab(nb, "▶ Output",  GREEN)
        self.tok_tab  = self._make_tab(nb, "⬡ Tokens",  TEAL)
        self.ast_tab  = self._make_tab(nb, "⎇ AST",     YELLOW)
        self.test_tab = self._make_tab(nb, "✓ Tests",   MUTED)

        # bottom reference bar
        ref = tk.Frame(self, bg=PANEL); ref.pack(fill="x", side="bottom")
        tk.Label(ref,
            text=("  Types: int  float  string  bool  list  none"
                  "  │  func name(params) { }  return"
                  "  │  if { } else { }  while { }  for x in list { }"
                  "  │  Built-ins: print()  len()  str()  int()  float()  type()  append()"),
            bg=PANEL, fg=MUTED, font=("Consolas",9),
            anchor="w", padx=6, pady=3).pack(fill="x")

    def _make_tab(self, nb, label, color):
        frame = tk.Frame(nb, bg=PANEL); nb.add(frame, text=label)
        box = scrolledtext.ScrolledText(frame, bg=PANEL, fg=color, font=MONO,
            relief="flat", bd=0, state="disabled", wrap="word", padx=12, pady=8)
        box.pack(fill="both", expand=True)
        for tag, fg in [("ok",GREEN),("err",RED),("info",TEAL),
                        ("warn",YELLOW),("sep",MUTED),("label",ACCENT)]:
            box.tag_config(tag, foreground=fg)
        return box

    def _update_status(self, _=None):
        ln, col = self.editor.index("insert").split(".")
        self.status_var.set(f"Ln {ln}  Col {int(col)+1}")

    def _write(self, box, text, tag="ok"):
        box.config(state="normal"); box.insert("end", text, tag)
        box.see("end"); box.config(state="disabled")

    def _clear(self, *boxes):
        for b in boxes:
            b.config(state="normal"); b.delete("1.0","end"); b.config(state="disabled")

    def _load_sample(self, name):
        self.editor.delete("1.0","end")
        self.editor.insert("1.0", SAMPLES.get(name,""))
        self._clear(self.out_tab, self.tok_tab, self.ast_tab, self.test_tab)

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("LoopBeat","*.lb"),("All","*.*")])
        if path:
            with open(path) as f: code = f.read()
            self.editor.delete("1.0","end"); self.editor.insert("1.0", code)
            self._clear(self.out_tab, self.tok_tab, self.ast_tab, self.test_tab)

    def _run(self):
        source = self.editor.get("1.0","end").strip()
        self._clear(self.out_tab, self.tok_tab, self.ast_tab)

        # tokens
        try: toks = "\n".join(repr(t) for t in Lexer(source).get_tokens())
        except LexerError as e: toks = str(e)
        self._write(self.tok_tab, toks+"\n")

        # AST
        try: ast_str = Parser(Lexer(source).get_tokens()).parse().pretty()
        except Exception as e: ast_str = str(e)
        self._write(self.ast_tab, ast_str+"\n")

        # output
        self._write(self.out_tab, "─"*46+"\n", "sep")
        output, err = self.interp.run(source)
        for line in output: self._write(self.out_tab, line+"\n", "ok")
        if err:
            self._write(self.out_tab, "\n"+err+"\n", "err")
            self._write(self.out_tab, "\n✗  Error\n", "err")
        else:
            self._write(self.out_tab, "\n✓  Done\n", "info")
        self._write(self.out_tab, "─"*46+"\n", "sep")

    def _run_tests(self):
        self._clear(self.test_tab)
        self._write(self.test_tab, "═"*46+"\n", "sep")
        self._write(self.test_tab, "  LoopBeat Test Suite\n", "label")
        self._write(self.test_tab, "═"*46+"\n\n", "sep")
        base = os.path.dirname(os.path.abspath(__file__))
        passed = failed = 0

        for folder, expect_err, label, tag in [
            ("tests/valid",   False, "── Valid programs ──\n",                "info"),
            ("tests/invalid", True,  "\n── Invalid programs (expect errors) ──\n","warn"),
        ]:
            self._write(self.test_tab, label, tag)
            d = os.path.join(base, folder)
            if not os.path.isdir(d):
                self._write(self.test_tab, f"  ('{folder}' not found)\n","warn"); continue
            for fname in sorted(os.listdir(d)):
                if not fname.endswith(".lb"): continue
                with open(os.path.join(d,fname)) as f: src=f.read()
                output, err = self.interp.run(src)
                ok = (err is None) if not expect_err else (err is not None)
                if expect_err: detail = f"caught: {err}" if ok else "SHOULD have errored"
                else:          detail = ", ".join(output) if ok else f"ERROR: {err}"
                self._write(self.test_tab,
                    f"  {'✓' if ok else '✗'}  {fname:<22} → {detail}\n",
                    "ok" if ok else "err")
                if ok: passed+=1
                else:  failed+=1

        total = passed+failed
        self._write(self.test_tab, "\n"+"═"*46+"\n","sep")
        self._write(self.test_tab, f"  {passed}/{total} passed\n",
                    "ok" if failed==0 else "err")
        self._write(self.test_tab, "═"*46+"\n","sep")

if __name__ == "__main__":
    LoopBeatIDE().mainloop()
