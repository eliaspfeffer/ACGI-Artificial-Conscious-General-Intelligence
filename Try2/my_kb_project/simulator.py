import random

from knowledge_graph import KnowledgeGraph
from needs import NeedsSystem
from semantic_check import SemanticChecker
from endlos_engine import EndlosEngine

def build_demo_knowledge_graph():
    """
    Erstellt ein Beispiel-Knowledge-Graph mit z.T. sinnvollen
    und z.T. unsinnigen Verknüpfungen.
    """
    kg = KnowledgeGraph()

    # Beispiel: Neuron-Namen sind "Mensch_liebt_Hund", "Apfel_kauft_Traktor" etc.
    # Für Variation: wir haben auch "knowledge_energy_Baum" etc. 
    #    => So kann das Engine naive Filter machen.
    data = [
        ("Mensch_liebt_Hund", "social_Mensch", 2.0),
        ("social_Mensch", "social_Hund", 2.0),
        ("Apfel_kauft_Traktor", "Objekt_Objekt_Verb", 5.0),
        ("knowledge_energy_Physik", "knowledge_energy_Mathematik", 3.0),
        ("knowledge_energy_Physik", "Mensch_liebt_Hund", 0.2),
        ("self_Reflexion", "Apfel_kauft_Traktor", 0.1),
        ("knowledge_energy_Baum", "knowledge_energy_Apfel", 3.0),
        ("knowledge_energy_Apfel", "Apfel_kauft_Traktor", 0.2),
        ("social_liebt", "Traktor", 1.0),
        ("self_Meditation", "self_Ego", 3.0),
        ("self_Ego", "social_Mensch", 0.4),
        ("self_Ego", "knowledge_energy_Physik", 0.1),
    ]

    # data: (A, B, weight)
    for (a, b, w) in data:
        kg.link_neurons(a, b, w)

    return kg

def run_simulation():
    kg = build_demo_knowledge_graph()
    ns = NeedsSystem()
    sc = SemanticChecker()

    engine = EndlosEngine(kg, ns, sc, random_factor=0.2)

    print("Starte Endlos-Schleife (10 Schritte) ...")
    engine.run_endlos(max_steps=10, delay=0.1)
    engine.print_log()

if __name__ == "__main__":
    run_simulation()
