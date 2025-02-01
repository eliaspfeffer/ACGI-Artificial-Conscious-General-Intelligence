import numpy as np

# Globale Gewichtungen
LAMBDA_WERT = 5
BEWERTUNGEN = [1.5, 0.5]
RELATIONEN = [10, 10]
HAEUFIGKEIT = [10, 10]
PFADLAENGE = 1

def berechne_konsistenz(kontext1, kontext2):
    """
    Berechnet die Konsistenz zwischen zwei Kontexten mit dem Jaccard-Index.
    """
    set1 = set(kontext1)
    set2 = set(kontext2)
    schnittmenge = len(set1.intersection(set2))
    vereinigungsmenge = len(set1.union(set2))
    return schnittmenge / vereinigungsmenge if vereinigungsmenge != 0 else 0

def berechne_wahrhaftigkeit(kontexte, bewertungen):
    """
    Berechnet die Wahrhaftigkeit eines Pfades mit Minimum, Widerspruchsprüfung und Multiplikation.
    """
    B_min = min(bewertungen)  # Minimum der Wahrhaftigkeit
    konsistenz = berechne_konsistenz(kontexte[0], kontexte[1])
    widerspruch = 1 - konsistenz
    B_widerspruch = B_min - LAMBDA_WERT * widerspruch
    B_multiplikativ = np.prod(bewertungen)
    return max(0, B_min * B_widerspruch * B_multiplikativ)  # Wahrhaftigkeit kann nicht negativ sein

def berechne_score(kontexte, relationen, haeufigkeit, pfadlaenge, konsistenz):
    """
    Berechnet den Score für einen gegebenen Pfad anhand der mathematischen Formel.
    """
    return sum([
        berechne_wahrhaftigkeit(kontexte, BEWERTUNGEN),  # Beispielhafte Bewertungen
        sum(relationen),
        sum(haeufigkeit),
        pfadlaenge,
        konsistenz
    ])

def getScoreBetweenContexts(kontext1, kontext2):
    """
    Berechnet den Score zwischen zwei Kontexten basierend auf gegebenen Kriterien.
    """
    # Split sentences into words
    words1 = kontext1.split()
    words2 = kontext2.split()
    konsistenz = berechne_konsistenz(words1, words2)
    return berechne_score([words1, words2], RELATIONEN, HAEUFIGKEIT, PFADLAENGE, konsistenz)

# Beispielhafte Verwendung:
kontext1 = "Der Apfel ist grün"
kontext2 = "Chlorophyll verursacht grüne Farbe"

score = getScoreBetweenContexts(kontext1, kontext2)
print(f"Score zwischen den Kontexten: {score}")
