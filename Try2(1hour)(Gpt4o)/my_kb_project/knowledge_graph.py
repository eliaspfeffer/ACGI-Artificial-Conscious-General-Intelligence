import math
import random
import time
from collections import defaultdict


class Neuron:
    """
    Repräsentiert einen Knoten im Netzwerk.
    - name: Klartext oder ID (z.B. "Apfel", "Baum" etc.)
    - links: {other_neuron: weight, ...}
    """
    def __init__(self, name):
        self.name = name
        self.links = {}  # andere Neuronen + Gewichte

    def link_to(self, other, weight=1.0):
        """
        Verknüpft 'self' mit 'other' (bidirektional)
        """
        if other not in self.links:
            self.links[other] = weight
        else:
            self.links[other] += weight

        if self not in other.links:
            other.links[self] = weight
        else:
            other.links[self] += weight

    def get_link_strength(self, other):
        """
        Gibt die Stärke der Verbindung zwischen self und other zurück,
        oder 0, falls nicht vorhanden.
        """
        return self.links.get(other, 0.0)

    def __repr__(self):
        return f"Neuron({self.name})"


class KnowledgeGraph:
    """
    Beinhaltet sämtliche Neuronen + deren Verknüpfungen.
    Zugriff z.B. über self.neurons_dict[name].
    """
    def __init__(self):
        self.neurons_dict = {}  # Name -> Neuron

    def get_or_create_neuron(self, name):
        """
        Falls Neuron (name) noch nicht existiert, erstelle es.
        Sonst liefere das existierende zurück.
        """
        if name not in self.neurons_dict:
            self.neurons_dict[name] = Neuron(name)
        return self.neurons_dict[name]

    def link_neurons(self, name_a, name_b, weight=1.0):
        """
        Erstellt bzw. verstärkt die Verbindung zwischen name_a und name_b.
        """
        a = self.get_or_create_neuron(name_a)
        b = self.get_or_create_neuron(name_b)
        a.link_to(b, weight)

    def get_random_neuron(self):
        """
        Gibt ein zufälliges Neuron zurück.
        """
        if not self.neurons_dict:
            return None
        return random.choice(list(self.neurons_dict.values()))

    def get_related_neurons(self, neuron, threshold=0.1):
        """
        Gibt eine Liste benachbarter Neuronen zurück, deren Verbindungsstärke
        über threshold liegt.
        """
        return [(n, w) for n, w in neuron.links.items() if w >= threshold]

    def __len__(self):
        return len(self.neurons_dict)

    def __repr__(self):
        return f"KnowledgeGraph({len(self.neurons_dict)} neurons)"
