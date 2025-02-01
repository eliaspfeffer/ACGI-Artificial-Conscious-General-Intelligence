import numpy as np
import re

# Automatische Attributzuordnung
ATTRIBUTE_KEYS = ["Wer", "Was", "Wie", "Wo", "Wann"]

def extract_attributes_from_sentence(sentence):
    words = sentence.split()
    attributes = {key: None for key in ATTRIBUTE_KEYS}
    for i, word in enumerate(words):
        if i < len(ATTRIBUTE_KEYS):
            attributes[ATTRIBUTE_KEYS[i]] = word
    return attributes

# Definition der Kontexte und automatische Attributzuordnung
context_sentences = {
    "K1": "Der Apfel ist grün",
    "K2": "Ein Baum hat grüne Blätter",
    "K3": "Chlorophyll verursacht grüne Farbe",
    "K4": "Ein Baum ist im Apfel",
}

contexts = {key: extract_attributes_from_sentence(sentence) for key, sentence in context_sentences.items()}

# Wahrhaftigkeit der Kontexte
truth_values = {
    "K1": 1.0,  # Mit eigenen Sinnen wahrgenommen
    "K2": 1.0,  # Mit eigenen Sinnen wahrgenommen
    "K3": 0.5,  # Gelesen
    "K4": 0.1,  # Gelesen
}

# Relationen und Häufigkeiten
relations = {
    "R12": ("K1", "K2", 10),
    "R13": ("K1", "K3", 10),
    "R24": ("K2", "K4", 1),
}

# Jaccard-Index zur Konsistenzbewertung
def jaccard_index(attributes1, attributes2):
    set1 = set(filter(None, attributes1.values()))
    set2 = set(filter(None, attributes2.values()))
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

# Konsistenz zwischen Kontexten
consistencies = {
    ("K1", "K3"): jaccard_index(contexts["K1"], contexts["K3"]),
    ("K2", "K4"): jaccard_index(contexts["K2"], contexts["K4"]),
    ("K1", "K2"): jaccard_index(contexts["K1"], contexts["K2"]),
}

# Pfade
paths = {
    "P1": ["R13"],
    "P2": ["R13", "R24"],
    "P3": ["R12", "R24"],
}

# Gewichtungsfaktoren
alpha = 50  # Gewicht für Wahrhaftigkeit
beta = 5   # Gewicht für Relation-Häufigkeit
gamma = 1  # Gewicht für Konsistenz
delta = 1  # Gewicht für Pfadlänge
lambda_w = 5  # Strafe für Widersprüche

def calculate_path_score(path):
    path_truth = []
    path_consistency = []
    relation_frequency = []

    for relation in path:
        kn, km, frequency = relations[relation]
        path_truth.append(min(truth_values[kn], truth_values[km]))
        path_consistency.append(consistencies.get((kn, km), 0))
        relation_frequency.append(frequency)

    # Berechnung der Komponenten
    B_P = min(path_truth)  # Minimum der Wahrhaftigkeit
    H_R = sum(relation_frequency)  # Summe der Häufigkeiten
    Kons_P = np.mean(path_consistency)  # Durchschnittliche Konsistenz
    Widerspruch = 1 - Kons_P  # Widerspruch basierend auf Konsistenz
    L_P = len(path)  # Länge des Pfades (Anzahl der Relationen)

    # Score-Berechnung
    score = (alpha * B_P) + (beta * H_R) + (gamma * Kons_P) + (delta * L_P) - (lambda_w * Widerspruch)
    return score

# Berechnung der Scores für alle Pfade
path_scores = {path_name: calculate_path_score(path) for path_name, path in paths.items()}

# Ergebnisse anzeigen
for path_name, score in path_scores.items():
    print(f"Score für {path_name}: {score:.2f}")
