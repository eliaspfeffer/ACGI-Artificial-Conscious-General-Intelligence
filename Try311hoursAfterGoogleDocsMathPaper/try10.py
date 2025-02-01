import numpy as np
import re
import json
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D

# Automatische Attributzuordnung
ATTRIBUTE_KEYS = ["Wer", "Was", "Wie", "Wo", "Wann"]

def extract_attributes_from_sentence(sentence):
    words = sentence.split()
    attributes = {key: [] for key in ATTRIBUTE_KEYS}
    for i, word in enumerate(words):
        if i < len(ATTRIBUTE_KEYS):
            attributes[ATTRIBUTE_KEYS[i]].append(word)
    return attributes

# Definition der RAM-Kurzzeitspeicherung (temporäre Kontexte)
ram_memory = {
    "K1": extract_attributes_from_sentence("Der Apfel hat eine grüne Farbe"),
    "K2": extract_attributes_from_sentence("Ein Baum hat grüne Blätter"),
    "K3": extract_attributes_from_sentence("Chlorophyll verursacht grüne Farbe"),
    "K4": extract_attributes_from_sentence("Ein Baum ist im Apfel"),
}

# Definition des Langzeitspeichers (SSD) als Dictionary mit Wort-Positionen
ssd_memory = {
    "words": {},  # Wörter als Schlüssel, Positionen als Listen von Kontexten
    "relations": {},  # Relationen zwischen Kontexten
    "scores": {},  # Speichert die Verbindungsstärke
}

# Wahrhaftigkeit der Kontexte
truth_values = {
    "K1": 1.0,
    "K2": 1.0,
    "K3": 0.5,
    "K4": 0.1,
}

# Relationen und Häufigkeiten
relations = {
    "R12": ("K1", "K2", 10),
    "R13": ("K1", "K3", 10),
    "R24": ("K2", "K4", 1),
}

# Jaccard-Index zur Konsistenzbewertung
def jaccard_index(attributes1, attributes2):
    set1 = set(sum(attributes1.values(), []))  # Flatten list
    set2 = set(sum(attributes2.values(), []))  # Flatten list
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

# Konsistenz zwischen Kontexten
consistencies = {
    ("K1", "K3"): jaccard_index(ram_memory["K1"], ram_memory["K3"]),
    ("K2", "K4"): jaccard_index(ram_memory["K2"], ram_memory["K4"]),
    ("K1", "K2"): jaccard_index(ram_memory["K1"], ram_memory["K2"]),
}

# Funktion zur Berechnung der Scores
def calculate_scores():
    alpha = 50  # Gewicht für Wahrhaftigkeit
    beta = 5    # Gewicht für Relation-Häufigkeit
    gamma = 1    # Gewicht für Konsistenz
    delta = 1    # Gewicht für Pfadlänge
    lambda_w = 5 # Strafe für Widersprüche
    
    for relation, (kn, km, frequency) in relations.items():
        B_P = min(truth_values[kn], truth_values[km])  # Minimum der Wahrhaftigkeit
        H_R = frequency  # Häufigkeit der Relation
        Kons_P = consistencies.get((kn, km), 0)  # Konsistenz aus vorher berechneten Werten
        Widerspruch = 1 - Kons_P  # Widerspruch basierend auf Konsistenz
        L_P = 1  # Jede Relation ist eine direkte Verbindung
        
        score = (alpha * B_P) + (beta * H_R) + (gamma * Kons_P) + (delta * L_P) - (lambda_w * Widerspruch)
        ssd_memory["scores"][relation] = score

calculate_scores()

# Funktion zur Visualisierung des SSD-Wissensgraphen in 3D
def plot_knowledge_graph_3d():
    G = nx.Graph()
    
    # Knoten für Kontexte hinzufügen
    for context in ram_memory:
        G.add_node(context, color='blue')
        for key, words in ram_memory[context].items():
            for word in words:
                G.add_node(word, color='green')
                G.add_edge(context, word, weight=1)  # Verbindungsstärke immer 1
    
    # Knoten aus Kontexten und deren Verbindungen mit gewichteten Kanten
    for relation, score in ssd_memory["scores"].items():
        kn, km, _ = relations[relation]
        G.add_node(kn, color='red')
        G.add_node(km, color='red')
        G.add_edge(kn, km, weight=score)
    
    # 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    pos = nx.spring_layout(G, dim=3)
    
    for node, (x, y, z) in pos.items():
        ax.scatter(x, y, z, color='red' if node in truth_values else 'blue' if node in ram_memory else 'green')
        ax.text(x, y, z, node, fontsize=10, ha='center')
    
    for edge in G.edges(data=True):
        x_vals = [pos[edge[0]][0], pos[edge[1]][0]]
        y_vals = [pos[edge[0]][1], pos[edge[1]][1]]
        z_vals = [pos[edge[0]][2], pos[edge[1]][2]]
        ax.plot(x_vals, y_vals, z_vals, color='gray', alpha=0.7, linewidth=edge[2]['weight'] / 10)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("Wissensgraph der AGI in 3D")
    plt.show()

# Dynamische Eingabe von neuen Kontexten
def add_new_context():
    while True:
        new_context = input("Gib einen neuen Kontext ein (oder 'exit' zum Beenden): ")
        if new_context.lower() == 'exit':
            break
        context_id = f"K{len(ram_memory) + 1}"
        ram_memory[context_id] = extract_attributes_from_sentence(new_context)
        plot_knowledge_graph_3d()

# Plot initial ausführen
add_new_context()
# plot_knowledge_graph_3d()

# Benutzer kann neue Kontexte hinzufügen