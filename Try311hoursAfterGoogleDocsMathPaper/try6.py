import numpy as np
import re
import json
import matplotlib.pyplot as plt
import networkx as nx

# Automatische Attributzuordnung
ATTRIBUTE_KEYS = ["Wer", "Was", "Wie", "Wo", "Wann"]

def extract_attributes_from_sentence(sentence):
    words = sentence.split()
    attributes = {key: None for key in ATTRIBUTE_KEYS}
    for i, word in enumerate(words):
        if i < len(ATTRIBUTE_KEYS):
            attributes[ATTRIBUTE_KEYS[i]] = word
    return attributes

# Definition der RAM-Kurzzeitspeicherung (temporäre Kontexte)
ram_memory = {}

# Definition des Langzeitspeichers (SSD) als Dictionary mit Wort-Positionen
ssd_memory = {
    "words": {},  # Wörter als Schlüssel, Positionen als Listen von Kontexten
    "relations": {},  # Relationen zwischen Kontexten
    "scores": {},  # Speichert die Verbindungsstärke
}

# Funktion zum Speichern in den RAM (Kurzzeitspeicher)
def store_in_ram(context_id, sentence):
    ram_memory[context_id] = extract_attributes_from_sentence(sentence)

# Funktion zum Übertragen von RAM in SSD mit platzsparender Speicherung
def transfer_to_ssd():
    global ssd_memory
    
    for context_id, attributes in ram_memory.items():
        for key, value in attributes.items():
            if value:
                # Falls Wort bereits in SSD existiert, nur Position hinzufügen
                if value not in ssd_memory["words"]:
                    ssd_memory["words"][value] = []
                ssd_memory["words"][value].append(context_id)
        
        # Relationen speichern (hier noch simpel, könnte ausgebaut werden)
        ssd_memory["relations"][context_id] = list(attributes.values())
    
    # RAM leeren nach Speicherung
    ram_memory.clear()

# Funktion zum Speichern des SSD-Speichers als JSON-Datei
def save_ssd_to_disk(filename="ssd_memory.json"):
    with open(filename, "w") as f:
        json.dump(ssd_memory, f, indent=4)

# Funktion zum Laden des SSD-Speichers aus JSON-Datei
def load_ssd_from_disk(filename="ssd_memory.json"):
    global ssd_memory
    try:
        with open(filename, "r") as f:
            ssd_memory = json.load(f)
    except FileNotFoundError:
        print("Keine bestehende SSD-Datei gefunden. Erstelle neuen Speicher.")

# Beispiel-Kontexte ins RAM speichern
store_in_ram("K1", "Der Apfel hat eine grüne Farbe")
store_in_ram("K2", "Ein Baum hat grüne Blätter")
store_in_ram("K3", "Chlorophyll verursacht grüne Farbe")
store_in_ram("K4", "Ein Baum ist im Apfel")

# Transfer vom RAM zur SSD
transfer_to_ssd()

# SSD auf die Festplatte speichern
save_ssd_to_disk()

# SSD aus der Festplatte laden (Testzweck)
load_ssd_from_disk()

# SSD-Inhalt anzeigen
print(json.dumps(ssd_memory, indent=4))

# Berechnung der Verbindungsstärken basierend auf Scores
def calculate_scores():
    for context, words in ssd_memory["relations"].items():
        for word in words:
            score = np.random.uniform(1, 10)  # Hier könnte eine echte Berechnung stehen
            ssd_memory["scores"][(context, word)] = score

calculate_scores()

# Visualisierung des SSD-Wissensgraphen
def plot_knowledge_graph():
    G = nx.Graph()
    
    # Knoten aus Wörtern hinzufügen
    for word in ssd_memory["words"]:
        G.add_node(word, color='green')
    
    # Knoten aus Kontexten und deren Verbindungen mit gewichteten Kanten
    for (context, word), weight in ssd_memory["scores"].items():
        G.add_node(context, color='red')
        if word in ssd_memory["words"]:
            G.add_edge(context, word, weight=weight)
    
    # Zeichnen des Graphen
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    edges = G.edges(data=True)
    edge_weights = [d['weight'] for (_, _, d) in edges]
    
    colors = ['red' if n in ssd_memory["relations"] else 'green' for n in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=colors, edge_color='gray', font_size=10, node_size=1000, width=edge_weights)
    plt.title("Wissensgraph der AGI mit Verbindungsstärken")
    plt.show()

# Plot ausführen
plot_knowledge_graph()
