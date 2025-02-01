import numpy as np
import re
import json
import matplotlib.pyplot as plt
import networkx as nx
import wikipediaapi
from mpl_toolkits.mplot3d import Axes3D
import random

# Automatische Attributzuordnung
ATTRIBUTE_KEYS = ["Wer", "Was", "Wie", "Wo", "Wann"]
HONEY_POTS = {"Fortpflanzung": [], "Regeneration": [], "Energieaufnahme": []}  # Honeypots als Fokusziele
ENERGY = 100  # Startenergie der AGI
ENERGY_DECAY = 5  # Energieverbrauch pro Bewegung
ENERGY_GAIN = 10  # Energiegewinn, wenn der Honeypot erreicht wird

# Wikipedia API einrichten
USER_AGENT = "MyResearchProject/1.0 (contact@example.com)"  # Bitte eigene E-Mail-Adresse einsetzen!
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent=USER_AGENT  # Hier wird der User-Agent korrekt übergeben
)

def extract_attributes_from_sentence(sentence):
    if not sentence:
        return {key: [] for key in ATTRIBUTE_KEYS}
    words = sentence.split()
    attributes = {key: [] for key in ATTRIBUTE_KEYS}
    for i, word in enumerate(words):
        if i < len(ATTRIBUTE_KEYS):
            attributes[ATTRIBUTE_KEYS[i]].append(word)
    return attributes

# RAM-Kurzzeitspeicherung (temporäre Kontexte)
ram_memory = {
    "K1": extract_attributes_from_sentence("Der Apfel hat eine grüne Farbe"),
    "K2": extract_attributes_from_sentence("Ein Baum hat grüne Blätter"),
    "K3": extract_attributes_from_sentence("Chlorophyll verursacht grüne Farbe"),
    "K4": extract_attributes_from_sentence("Ein Baum ist im Apfel"),
}

# Langzeitspeicher (SSD)
ssd_memory = {"words": {}, "relations": {}, "scores": {}}

# Wahrhaftigkeit der Kontexte
truth_values = {"K1": 1.0, "K2": 1.0, "K3": 0.5, "K4": 0.1}

# Relationen und Häufigkeiten
relations = {"R12": ("K1", "K2", 10), "R13": ("K1", "K3", 10), "R24": ("K2", "K4", 1)}

# Jaccard-Index zur Konsistenzbewertung
def jaccard_index(attributes1, attributes2):
    set1 = set(sum(attributes1.values(), []))
    set2 = set(sum(attributes2.values(), []))
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

# Konsistenz zwischen Kontexten
consistencies = {
    ("K1", "K3"): jaccard_index(ram_memory["K1"], ram_memory["K3"]),
    ("K2", "K4"): jaccard_index(ram_memory["K2"], ram_memory["K4"]),
    ("K1", "K2"): jaccard_index(ram_memory["K1"], ram_memory["K2"]),
}

# Berechnung der Scores mit verstärkten Verbindungen
def calculate_scores():
    alpha, beta, gamma, delta, lambda_w = 50, 5, 1, 1, 5
    for relation, (kn, km, frequency) in relations.items():
        B_P = min(truth_values[kn], truth_values[km])
        H_R = frequency
        Kons_P = consistencies.get((kn, km), 0)
        Widerspruch = 1 - Kons_P
        L_P = 1
        score = (alpha * B_P) + (beta * H_R) + (gamma * Kons_P) + (delta * L_P) - (lambda_w * Widerspruch)
        ssd_memory["scores"][relation] = score
calculate_scores()

import wikipedia

# Wikipedia Input abrufen
def get_wikipedia_info(topic):
    try:
        summary = wikipedia.summary(topic, sentences=1)
        return summary
    except:
        return None

# Honeypots mit Informationen füllen
def update_honeypots():
    for honeypot in HONEY_POTS.keys():
        info = get_wikipedia_info(honeypot)
        HONEY_POTS[honeypot] = extract_attributes_from_sentence(info)
update_honeypots()

# Entscheidungslogik für Gedankenendlosimpuls mit Widerstandsberücksichtigung
def move_to_next_context():
    global ENERGY
    if ENERGY <= 0:
        print("AGI muss regenerieren!")
        return
    
    weighted_options = []
    for relation, (kn, km, _) in relations.items():
        resistance = 1 / (ssd_memory["scores"].get(relation, 1) + 1)  # Widerstand umgekehrt proportional zur Häufigkeit
        weighted_options.append((resistance, kn, km))
    
    weighted_options.sort()
    chosen_relation = weighted_options[0] if ENERGY < 20 else random.choice(weighted_options[:3])
    
    kn, km = chosen_relation[1], chosen_relation[2]
    ENERGY -= ENERGY_DECAY * chosen_relation[0]  # Energieverbrauch nach Widerstand
    print(f"AGI bewegt sich von {kn} zu {km}. Verbleibende Energie: {ENERGY}")
    
    if any(hp in km for hp in HONEY_POTS):
        ENERGY += ENERGY_GAIN
        print("Honeypot erreicht! Energie regeneriert.")

# Simulation starten
update_honeypots()
for _ in range(10):
    move_to_next_context()
