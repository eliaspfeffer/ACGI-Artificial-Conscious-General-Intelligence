import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D
import random

# AGI Energy and Memory States
ENERGY = 100
ENERGY_DECAY = 5
ENERGY_GAIN = 10
LAMBDA_G = 0.1  # Exponential decay factor for happiness function

# RAM Memory (Temporary Contexts) with structured attributes
ram_memory = {
    "K1": {"Wer": "Der Apfel", "Was": "ist", "Wie": "grün"},
    "K2": {"Wer": "Ein Baum", "Was": "hat", "Wie": "grüne Blätter"},
    "K3": {"Was": "Chlorophyll", "Wie": "verursacht grüne Farbe"},
    "K4": {"Wer": "Ein Baum", "Was": "ist", "Wo": "im Apfel"},
}

# Truth values of contexts
truth_values = {"K1": 1.0, "K2": 1.0, "K3": 0.5, "K4": 0.1}

# Honeypots (Motivation Centers)
honeypots = {"Energieaufnahme": "K1"}  # Zielkontext für Energieaufnahme

# Relations and Frequencies
relations = {"R12": ("K1", "K2", 10), "R13": ("K1", "K3", 10), "R24": ("K2", "K4", 1)}

# Movement Log
movement_log = []

# Function to compute resistance
def compute_resistance(frequency):
    return 1 / (frequency + 1)  # Resistance inversely proportional to frequency

# Function to compute distance to honeypot
def compute_distance_to_honeypot(context):
    if context not in honeypots.values():
        path_length = sum(compute_resistance(relations[r][2]) for r in relations if context in relations[r])
        return path_length
    return 0

# Function to compute happiness level
def compute_happiness(context):
    distance = compute_distance_to_honeypot(context)
    return np.exp(-LAMBDA_G * distance)  # Happiness decays exponentially with distance

# Function to calculate movement
def move_to_next_context():
    global ENERGY
    if ENERGY <= 0:
        print("AGI muss regenerieren!")
        return
    
    weighted_options = []
    for relation, (kn, km, freq) in relations.items():
        resistance = compute_resistance(freq)
        happiness = compute_happiness(km)
        decision_factor = resistance * (1 / happiness)  # Decision equation
        weighted_options.append((decision_factor, kn, km))
    
    weighted_options.sort(key=lambda x: x[0])
    chosen_relation = weighted_options[0] if ENERGY < 20 else random.choice(weighted_options[:3])
    
    kn, km = chosen_relation[1], chosen_relation[2]
    ENERGY -= ENERGY_DECAY * chosen_relation[0]  # Energy decay based on movement cost
    print(f"AGI bewegt sich von {kn} zu {km}. Verbleibende Energie: {ENERGY}")
    movement_log.append((kn, km))

# Run AGI simulation for movements
for _ in range(10):
    move_to_next_context()

# 3D Plot Function
def plot_knowledge_graph_3d():
    G = nx.Graph()
    
    # Add nodes for contexts and their information
    for context, attributes in ram_memory.items():
        G.add_node(context, color='blue')
        for attr_type, info in attributes.items():
            node_name = f"{info} ({attr_type})"
            G.add_node(node_name, color='green')
            G.add_edge(context, node_name)  # Connect context to its structured attribute
    
    # Add edges based on movements
    for kn, km in movement_log:
        G.add_edge(kn, km)
    
    # 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    pos = nx.spring_layout(G, dim=3)
    
    for node, (x, y, z) in pos.items():
        color = 'blue' if node in ram_memory else 'green'
        ax.scatter(x, y, z, color=color, s=100)
        ax.text(x, y, z, node, fontsize=10, ha='center')
    
    for edge in G.edges():
        x_vals = [pos[edge[0]][0], pos[edge[1]][0]]
        y_vals = [pos[edge[0]][1], pos[edge[1]][1]]
        z_vals = [pos[edge[0]][2], pos[edge[1]][2]]
        ax.plot(x_vals, y_vals, z_vals, color='gray', alpha=0.7)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("AGI Kontextbewegung in 3D mit Attributspezifikation")
    plt.show()

# Execute plot
plot_knowledge_graph_3d()