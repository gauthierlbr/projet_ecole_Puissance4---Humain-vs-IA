"""
Puissance 4 (12 colonnes) — Moteur + IA (alpha-bêta)

Projet pour école : objectif = apprendre un peu d'IA “classique” (minimax/alpha-bêta)
et faire un jeu jouable.

Convention:
- IA =  1
- Humain = -1
- Vide =  0
"""

from __future__ import annotations
from typing import List, Optional, Tuple

LIGNES = 6
COLONNES = 12
PROFONDEUR_MAX = 5

INF = 10**9

# On teste d'abord les colonnes centrales (souvent meilleur au Puissance 4)
ORDRE_COLONNES = sorted(range(COLONNES), key=lambda c: abs(c - (COLONNES - 1) / 2))

Grille = List[List[int]]
DernierCoup = Optional[Tuple[int, int, int]]  # (ligne, colonne, joueur)


def actions(grille: Grille) -> List[int]:
    return [c for c in ORDRE_COLONNES if grille[0][c] == 0]


def jouer(grille: Grille, col: int, joueur: int) -> Optional[int]:
    """
    Joue un pion dans la colonne 'col' et retourne la ligne où il atterrit.
    Retourne None si colonne pleine (normalement filtré par actions()).
    """
    for lig in range(LIGNES - 1, -1, -1):
        if grille[lig][col] == 0:
            grille[lig][col] = joueur
            return lig
    return None


def annuler(grille: Grille, lig: int, col: int) -> None:
    """Annule un coup (utile pour l'exploration alpha-bêta)."""
    grille[lig][col] = 0


def victoire_depuis(grille: Grille, lig: int, col: int, joueur: int) -> bool:
    """Vérifie une victoire en partant du dernier coup (lig, col)."""

    def compte(dl: int, dc: int) -> int:
        r, c = lig + dl, col + dc
        n = 0
        while 0 <= r < LIGNES and 0 <= c < COLONNES and grille[r][c] == joueur:
            n += 1
            r += dl
            c += dc
        return n

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dl, dc in directions:
        total = 1 + compte(dl, dc) + compte(-dl, -dc)
        if total >= 4:
            return True
    return False


def terminal(grille: Grille, dernier_coup: DernierCoup) -> bool:
    """Fin de partie si victoire ou plus aucun coup possible."""
    if dernier_coup is not None:
        lig, col, joueur = dernier_coup
        if victoire_depuis(grille, lig, col, joueur):
            return True
    return len(actions(grille)) == 0


def score_fenetre(fenetre: List[int], joueur: int) -> int:
    """Score d'une fenêtre de 4 cases. Simple mais efficace."""
    adv = -joueur
    c_j = fenetre.count(joueur)
    c_a = fenetre.count(adv)
    c_v = fenetre.count(0)

    if c_j > 0 and c_a > 0:
        return 0

    if c_j == 4:
        return 100000
    if c_j == 3 and c_v == 1:
        return 200
    if c_j == 2 and c_v == 2:
        return 30
    if c_j == 1 and c_v == 3:
        return 5

    if c_a == 3 and c_v == 1:
        return -220
    if c_a == 2 and c_v == 2:
        return -35

    return 0


def heuristique(grille: Grille) -> int:
    """Évalue la position pour l'IA (joueur = 1)."""
    joueur = 1
    score = 0

    centres = [COLONNES // 2 - 1, COLONNES // 2] if COLONNES % 2 == 0 else [COLONNES // 2]
    for r in range(LIGNES):
        for c in centres:
            if grille[r][c] == joueur:
                score += 6
            elif grille[r][c] == -joueur:
                score -= 6

    for r in range(LIGNES):
        for c in range(COLONNES - 3):
            fen = [grille[r][c + i] for i in range(4)]
            score += score_fenetre(fen, joueur)

    for r in range(LIGNES - 3):
        for c in range(COLONNES):
            fen = [grille[r + i][c] for i in range(4)]
            score += score_fenetre(fen, joueur)

    for r in range(LIGNES - 3):
        for c in range(COLONNES - 3):
            fen = [grille[r + i][c + i] for i in range(4)]
            score += score_fenetre(fen, joueur)

    for r in range(3, LIGNES):
        for c in range(COLONNES - 3):
            fen = [grille[r - i][c + i] for i in range(4)]
            score += score_fenetre(fen, joueur)

    return score


def alphabeta(
    grille: Grille,
    profondeur: int,
    alpha: int,
    beta: int,
    maximise: bool,
    dernier_coup: DernierCoup,
) -> int:
    """Minimax + élagage alpha-bêta."""
    if profondeur == 0 or terminal(grille, dernier_coup):
        if dernier_coup is not None:
            lig, col, j = dernier_coup
            if victoire_depuis(grille, lig, col, j):
                return 1000000 if j == 1 else -1000000
        return heuristique(grille)

    if maximise:
        best = -INF
        for col in actions(grille):
            lig = jouer(grille, col, 1)
            assert lig is not None
            score = alphabeta(grille, profondeur - 1, alpha, beta, False, (lig, col, 1))
            annuler(grille, lig, col)

            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best

    best = INF
    for col in actions(grille):
        lig = jouer(grille, col, -1)
        assert lig is not None
        score = alphabeta(grille, profondeur - 1, alpha, beta, True, (lig, col, -1))
        annuler(grille, lig, col)

        if score < best:
            best = score
        if best < beta:
            beta = best
        if alpha >= beta:
            break
    return best


def IA_Decision(grille: Grille) -> int:
    """Choisit la meilleure colonne pour l'IA."""
    coups = actions(grille)
    if not coups:
        return 0

    best_score = -INF
    best_col = coups[0]
    alpha, beta = -INF, INF

    for col in coups:
        lig = jouer(grille, col, 1)
        if lig is None:
            continue

        # si coup gagnant direct, on ne se complique pas la vie
        if victoire_depuis(grille, lig, col, 1):
            annuler(grille, lig, col)
            return col

        score = alphabeta(grille, PROFONDEUR_MAX - 1, alpha, beta, False, (lig, col, 1))
        annuler(grille, lig, col)

        if score > best_score:
            best_score = score
            best_col = col
        if best_score > alpha:
            alpha = best_score

    return best_col


def afficher(grille: Grille) -> None:
    """Affichage console (utile si tu veux tester sans UI)."""
    print("\n " + " ".join([f"{i:2d}" for i in range(COLONNES)]))
    for ligne in grille:
        print(" " + " ".join(" ." if v == 0 else (" O" if v == 1 else " X") for v in ligne))


if __name__ == "__main__":
    # Petite version console pour test rapide
    grille: Grille = [[0] * COLONNES for _ in range(LIGNES)]
    joueur = 1
    dernier: DernierCoup = None

    while not terminal(grille, dernier):
        afficher(grille)

        if joueur == 1:
            print("\nL'IA joue...")
            col = IA_Decision(grille)
            lig = jouer(grille, col, 1)
            assert lig is not None
            print(f"L'IA joue colonne {col}")
            dernier = (lig, col, 1)
            joueur = -1
        else:
            col = -1
            coups = actions(grille)
            while col not in coups:
                try:
                    col = int(input(f"\nTon tour (0-{COLONNES-1}): "))
                except Exception:
                    col = -1
            lig = jouer(grille, col, -1)
            assert lig is not None
            dernier = (lig, col, -1)
            joueur = 1

    afficher(grille)
    if dernier is not None and victoire_depuis(grille, dernier[0], dernier[1], dernier[2]):
        print("\nL'IA gagne !" if dernier[2] == 1 else "\nTu gagnes !")
    else:
        print("\nMatch nul !")
