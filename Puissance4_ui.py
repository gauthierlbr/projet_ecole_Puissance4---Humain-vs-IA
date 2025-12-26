"""
Puissance 4 (12 colonnes) — Interface Tkinter

- Clic n'importe où dans une colonne pour jouer
- Humain (jaune) vs IA (rouge)
- Boutons arrondis (Canvas) + hover
"""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

import Puissance4_moteur as M


COULEUR_HUMAIN = "yellow"     # humain
COULEUR_IA = "red"          # IA
COULEUR_VIDE = "white"

BARRE_HAUT_BG = "#F1F5F9"
BTN_NEW_BG = "#7DD3FC"      # bleu clair
BTN_NEW_HOVER = "#38BDF8"
BTN_QUIT_BG = "#FCA5A5"     # rouge clair
BTN_QUIT_HOVER = "#F87171"


class RoundedButton:

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        w: int,
        h: int,
        r: int,
        text: str,
        bg: str,
        bg_hover: str,
        command,
        font=("Arial", 12, "bold"),
    ):
        self.canvas = canvas
        self.command = command
        self.bg = bg
        self.bg_hover = bg_hover
        self.items = []
        self.items.append(canvas.create_rectangle(x + r, y, x + w - r, y + h, fill=bg, outline=""))
        self.items.append(canvas.create_rectangle(x, y + r, x + w, y + h - r, fill=bg, outline=""))
        self.items.append(canvas.create_oval(x, y, x + 2 * r, y + 2 * r, fill=bg, outline=""))
        self.items.append(canvas.create_oval(x + w - 2 * r, y, x + w, y + 2 * r, fill=bg, outline=""))
        self.items.append(canvas.create_oval(x, y + h - 2 * r, x + 2 * r, y + h, fill=bg, outline=""))
        self.items.append(
            canvas.create_oval(x + w - 2 * r, y + h - 2 * r, x + w, y + h, fill=bg, outline="")
        )

        self.items.append(
            canvas.create_text(x + w / 2, y + h / 2, text=text, font=font, fill="black")
        )

        for item in self.items:
            canvas.tag_bind(item, "<Button-1>", lambda e: self.command())
            canvas.tag_bind(item, "<Enter>", self.on_enter)
            canvas.tag_bind(item, "<Leave>", self.on_leave)
            canvas.tag_bind(item, "<Motion>", lambda e: None)  # rend le hover plus stable
        canvas.config(cursor="arrow")

    def on_enter(self, _):
        for i in self.items[:-1]:  # sauf le texte
            self.canvas.itemconfig(i, fill=self.bg_hover)
        self.canvas.config(cursor="hand2")

    def on_leave(self, _):
        for i in self.items[:-1]:
            self.canvas.itemconfig(i, fill=self.bg)
        self.canvas.config(cursor="arrow")


class Puissance4UI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Puissance 4 (12 colonnes) — Humain vs IA")

        self.grille = [[0] * M.COLONNES for _ in range(M.LIGNES)]
        self.dernier = None
        self.finie = False
        self.cell = 70
        self.pad = 12
        self.w = self.pad * 2 + M.COLONNES * self.cell
        self.h = self.pad * 2 + (M.LIGNES + 1) * self.cell  # +1 bandeau numéro colonnes

        self.info = tk.StringVar()
        self.info.set("À toi ! Clique dans une colonne pour jouer.")

        self.top = tk.Canvas(root, height=64, bg=BARRE_HAUT_BG, highlightthickness=0)
        self.top.pack(fill="x", padx=10, pady=8)

        self.top_text = self.top.create_text(
            12, 32,
            anchor="w",
            text=self.info.get(),
            font=("Arial", 11),
            fill="black",
        )

        self.info.trace_add("write", lambda *_: self.top.itemconfig(self.top_text, text=self.info.get()))

        self.btn_new = None
        self.btn_quit = None
        self.root.bind("<Configure>", self._layout_top)

        self.canvas = tk.Canvas(root, width=self.w, height=self.h, highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 10))

        self.canvas.bind("<Button-1>", self.on_click)

        self._layout_top()
        self.redraw()

    def _layout_top(self, _event=None):
        self.top.delete("btn")
        self.top.itemconfig(self.top_text, text=self.info.get())

        width = max(self.top.winfo_width(), 600)

        x_quit = width - 12 - 100
        y = 14
        self.btn_quit = RoundedButton(
            self.top, x=x_quit, y=y, w=100, h=36, r=18,
            text="Quitter",
            bg=BTN_QUIT_BG, bg_hover=BTN_QUIT_HOVER,
            command=self.root.destroy
        )
        for it in self.btn_quit.items:
            self.top.addtag_withtag("btn", it)

        x_new = x_quit - 12 - 170
        self.btn_new = RoundedButton(
            self.top, x=x_new, y=y, w=170, h=36, r=18,
            text="Nouvelle partie",
            bg=BTN_NEW_BG, bg_hover=BTN_NEW_HOVER,
            command=self.reset
        )
        for it in self.btn_new.items:
            self.top.addtag_withtag("btn", it)

    def reset(self):
        self.grille = [[0] * M.COLONNES for _ in range(M.LIGNES)]
        self.dernier = None
        self.finie = False
        self.info.set("Nouvelle partie ! Clique dans une colonne pour jouer.")
        self.redraw()

    def col_from_x(self, x: int) -> int:
        x0 = x - self.pad
        if x0 < 0:
            return -1
        col = x0 // self.cell
        if 0 <= col < M.COLONNES:
            return int(col)
        return -1

    def on_click(self, event):
        if self.finie:
            return

        col = self.col_from_x(event.x)
        if col == -1:
            return

        coups_possibles = M.actions(self.grille)
        if col not in coups_possibles:
            self.flash_column()
            return

        lig = M.jouer(self.grille, col, -1)
        if lig is None:
            self.flash_column()
            return

        self.dernier = (lig, col, -1)
        self.redraw()

        if self.check_end():
            return

        self.info.set("Je réfléchis…")
        self.root.after(120, self.ia_play)

    def ia_play(self):
        if self.finie:
            return

        col = M.IA_Decision(self.grille)
        lig = M.jouer(self.grille, col, 1)
        if lig is None:
            self.info.set("Oups, coup IA impossible.")
            return

        self.dernier = (lig, col, 1)
        self.redraw()

        if self.check_end():
            return

        self.info.set("À toi ! Clique dans une colonne.")

    def check_end(self) -> bool:
        if M.terminal(self.grille, self.dernier):
            self.finie = True

            if self.dernier is not None and M.victoire_depuis(self.grille, self.dernier[0], self.dernier[1], self.dernier[2]):
                if self.dernier[2] == 1:
                    self.info.set("Fin : l’IA gagne.")
                    messagebox.showinfo("Terminé", "L’IA gagne !")
                else:
                    self.info.set("Fin : tu gagnes !")
                    messagebox.showinfo("Terminé", "Bravo, tu gagnes !")
            else:
                self.info.set("Fin : match nul.")
                messagebox.showinfo("Terminé", "Match nul !")

            return True
        return False

    def flash_column(self):
        self.info.set("Colonne pleine. Essaie une autre colonne.")
        self.root.after(900, lambda: (not self.finie) and self.info.set("À toi ! Clique dans une colonne."))

    def redraw(self):
        self.canvas.delete("all")

        self.canvas.create_rectangle(
            self.pad, self.pad,
            self.pad + M.COLONNES * self.cell, self.pad + self.cell,
            outline=""
        )
        for c in range(M.COLONNES):
            cx = self.pad + c * self.cell + self.cell / 2
            cy = self.pad + self.cell / 2
            self.canvas.create_text(cx, cy, text=str(c), font=("Arial", 14, "bold"))

        for r in range(M.LIGNES):
            for c in range(M.COLONNES):
                x1 = self.pad + c * self.cell
                y1 = self.pad + (r + 1) * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell

                self.canvas.create_rectangle(x1, y1, x2, y2)

                v = self.grille[r][c]
                if v == 0:
                    fill = COULEUR_VIDE
                elif v == 1:
                    fill = COULEUR_IA
                else:
                    fill = COULEUR_HUMAIN

                m = 10
                self.canvas.create_oval(x1 + m, y1 + m, x2 - m, y2 - m, fill=fill, outline="")

        if self.dernier is not None:
            r, c, _ = self.dernier
            x1 = self.pad + c * self.cell
            y1 = self.pad + (r + 1) * self.cell
            x2 = x1 + self.cell
            y2 = y1 + self.cell
            m = 6
            self.canvas.create_oval(x1 + m, y1 + m, x2 - m, y2 - m, outline="black", width=3)


if __name__ == "__main__":
    root = tk.Tk()
    app = Puissance4UI(root)
    root.mainloop()
