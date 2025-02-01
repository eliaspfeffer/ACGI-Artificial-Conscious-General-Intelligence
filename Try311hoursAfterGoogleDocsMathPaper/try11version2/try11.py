import networkx as nx
import wikipedia
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ArtificialConsciousness:
    def __init__(self):
        self.graph = nx.Graph()
        self.honeypots = {"Reproduction": 0, "Regeneration": 0, "Energy_Intake": 0}
        self.energy_level = 100
        self.resistance_factor = 1.5  # Widerstandsfaktor für Gedankenbewegung
    
    def fetch_wikipedia_info(self, query):
        try:
            summary = wikipedia.summary(query, sentences=1)
            return summary
        except:
            return None

    def add_context(self, context):
        if context not in self.graph:
            self.graph.add_node(context, weight=1, pos=(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)))
        else:
            self.graph.nodes[context]['weight'] += 1

    def connect_contexts(self, context1, context2):
        if context1 in self.graph and context2 in self.graph:
            if self.graph.has_edge(context1, context2):
                self.graph[context1][context2]['weight'] += 1
            else:
                self.graph.add_edge(context1, context2, weight=1)
    
    def calculate_resistance(self, context1, context2):
        return self.resistance_factor / (1 + self.graph[context1][context2]['weight'])
    
    def simulate_thought_process(self, start_context):
        path = [start_context]
        current_context = start_context
        while self.energy_level > 0:
            neighbors = list(self.graph.neighbors(current_context))
            if not neighbors:
                break
            
            next_context = min(neighbors, key=lambda x: self.calculate_resistance(current_context, x))
            path.append(next_context)
            self.energy_level -= self.calculate_resistance(current_context, next_context)
            current_context = next_context
        
        return path
    
    def reinforce_memory(self, context1, context2):
        if self.graph.has_edge(context1, context2):
            self.graph[context1][context2]['weight'] += 2
    
    def update_honeypot(self, need):
        if need in self.honeypots:
            self.honeypots[need] += 1
            self.energy_level += 10  # Simulate satisfaction increasing energy
    
    def run_simulation(self, query):
        context = self.fetch_wikipedia_info(query)
        if context:
            self.add_context(context)
            related_context = random.choice(list(self.graph.nodes)) if self.graph.nodes else None
            if related_context:
                self.connect_contexts(context, related_context)
        
        return self.simulate_thought_process(context) if context else []
    
    def plot_graph_3d(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        pos = nx.get_node_attributes(self.graph, 'pos')
        for node, (x, y, z) in pos.items():
            ax.scatter(x, y, z, color='blue', s=20)
            ax.text(x, y, z, node[:10], fontsize=8)
        
        for edge in self.graph.edges():
            x_vals = [pos[edge[0]][0], pos[edge[1]][0]]
            y_vals = [pos[edge[0]][1], pos[edge[1]][1]]
            z_vals = [pos[edge[0]][2], pos[edge[1]][2]]
            ax.plot(x_vals, y_vals, z_vals, color='gray')
        
        plt.show()

# Example usage
ac = ArtificialConsciousness()
ac.run_simulation("Apple")
ac.plot_graph_3d()
