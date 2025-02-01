import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from mpl_toolkits.mplot3d import Axes3D
import random

# AGI Energy and Memory States
ENERGY = 100
ENERGY_DECAY = 5
ENERGY_GAIN = 10

# RAM Memory (Temporary Contexts)
ram_memory = {
    "K1": ["Apfel", "grüne Farbe"],
    "K2": ["Baum", "grüne Blätter"],
    "K3": ["Chlorophyll", "grüne Farbe"],
    "K4": ["Baum", "Apfel"],
}

# Truth values of contexts
truth_values = {"K1": 1.0, "K2": 1.0, "K3": 0.5, "K4": 0.1}

# Relations and Frequencies
relations = {"R12": ("K1", "K2", 10), "R13": ("K1", "K3", 10), "R24": ("K2", "K4", 1)}

# Movement Log
movement_log = []

# Function to calculate movement

def move_to_next_context():
    global ENERGY
    if ENERGY <= 0:
        print("AGI muss regenerieren!")
        return
    
    weighted_options = []
    for relation, (kn, km, freq) in relations.items():
        resistance = 1 / (freq + 1)  # Resistance inversely proportional to frequency
        weighted_options.append((resistance, kn, km))
    
    weighted_options.sort()
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
    
    # Add nodes for contexts
    for context in ram_memory:
        G.add_node(context)
    
    # Add edges based on movements
    for kn, km in movement_log:
        G.add_edge(kn, km)
    
    # 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    pos = nx.spring_layout(G, dim=3)
    
    for node, (x, y, z) in pos.items():
        ax.scatter(x, y, z, color='blue', s=100)
        ax.text(x, y, z, node, fontsize=10, ha='center')
    
    for edge in G.edges():
        x_vals = [pos[edge[0]][0], pos[edge[1]][0]]
        y_vals = [pos[edge[0]][1], pos[edge[1]][1]]
        z_vals = [pos[edge[0]][2], pos[edge[1]][2]]
        ax.plot(x_vals, y_vals, z_vals, color='gray', alpha=0.7)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title("AGI Kontextbewegung in 3D")
    plt.show()

# Execute plot
plot_knowledge_graph_3d()
