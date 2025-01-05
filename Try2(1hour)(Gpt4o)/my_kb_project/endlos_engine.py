import random
import threading
import time

from knowledge_graph import KnowledgeGraph, Neuron
from needs import NeedsSystem
from semantic_check import SemanticChecker


class EndlosEngine:
    """
    Steuert die "rollende Billardkugel" - also den kontinuierlichen 
    Gedankengang. 

    - Wir haben 3 Hauptfaktoren, warum als nächstes welcher Gedanke 
      (Neuron) angestoßen wird:
        1) geringster Widerstand / Gewohnheit
        2) Zufall
        3) höheres Ziel (Bedürfnispyramide)
    - Wir werden hier in einer Endlosschleife "ticks" abfeuern.
    """

    def __init__(self, 
                 knowledge_graph: KnowledgeGraph, 
                 needs_system: NeedsSystem,
                 semantic_checker: SemanticChecker,
                 random_factor: float = 0.2):
        """
        - random_factor: Wahrscheinlichkeit (0..1), dass wir zufällig die Richtung ändern
        """
        self.kg = knowledge_graph
        self.ns = needs_system
        self.sc = semantic_checker
        self.random_factor = random_factor

        # aktuell aktiver Gedanke (Neuron)
        self.current_neuron = None

        # Stop-Flag für Thread
        self._stop = False

        # Protokoll der "Gedanken"
        self.thought_log = []

    def choose_next_neuron(self):
        """
        Bestimmt den nächsten aktiven Neuron ("Billardkugel"), 
        je nach 1) Gewohnheit, 2) Zufall, 3) Bedürfnis
        """

        if self.current_neuron is None:
            # Falls kein aktueller Neuron, pick random
            return self.kg.get_random_neuron()

        # 1) Höherer Drang: Schauen, ob needs_system was "bestimmen" will
        #    => vereinfachtes Mapping: 
        #       - "knowledge_energy" => Suchen wir ein "Wissensnahes" Neuron?
        #       - "social" => Suchen wir ein "sozial" geprägtes Neuron? (z.B. "Mensch", "Hund", "liebt")
        #       - "self" => Suchen wir "Ich"-Themen, was auch immer das heißen mag.
        main_need = self.ns.choose_next_action()  # z.B. "knowledge_energy"

        possible_nexts = self.kg.get_related_neurons(self.current_neuron, threshold=0.01)
        # possible_nexts = [(neuron_obj, weight), ...]

        if not possible_nexts:
            # keine benachbarten - pick random global
            return self.kg.get_random_neuron()

        # Filtern wir mal, was "naheliegend" wäre (geringster Widerstand -> starker Link)
        # Sortieren nach descending weight
        possible_nexts.sort(key=lambda x: x[1], reverse=True)

        # 2) random factor
        if random.random() < self.random_factor:
            # reiner Zufall
            return random.choice(possible_nexts)[0]

        # 3) "gezielte Steuerung" - naive:
        #    wir gucken, ob wir Neuronen haben, die thematisch "passend" sind
        #    => z.B. "knowledge_energy" => random Ausschnitt
        #    Hier sehr vereinfacht: wir tun so, als hätten wir "Tags" im Namen
        #    (z.B. "Wissen_", "Sozial_", "Ich_") -> in Realität komplexer
        filtered = [p for p in possible_nexts if main_need in p[0].name]

        if not filtered:
            # fallback: nimm die stärkste Verbindung
            return possible_nexts[0][0]
        else:
            # nimm eine zufällige aus den gefilterten
            return random.choice(filtered)[0]

    def interpret_neuron(self, neuron: Neuron):
        """
        Versuche, semantische Aussagen aus dem Neuronen-Namen zu parsen,
        checke mit semantic_check, ob das "Sinn" ergibt.
        """
        words = neuron.name.split("_")
        # check
        is_ok = self.sc.is_semantically_valid(words)
        if not is_ok:
            # semantisch unsinnig => evtl. "Bestrafung"?
            self.ns.stress_need("knowledge_energy")  # z.B. Strafe
            log_str = f"[Semantik-Alarm] -> {neuron.name} unsinnig"
        else:
            log_str = f"[Semantik-OK] -> {neuron.name}"
        return log_str

    def step(self):
        """
        Eine Iteration der "Endlos-Schleife".
        """
        self.ns.tick()  # Bedürfnisse minimal absinken lassen
        
        next_neuron = self.choose_next_neuron()
        if not next_neuron:
            return

        self.current_neuron = next_neuron
        # "interpretieren"
        sem_str = self.interpret_neuron(self.current_neuron)

        # Das System könnte daraufhin eine Aktion ausführen, z.B. Bedürfnis erfüllen
        if random.random() < 0.3:
            # 30% Chance: wir erfüllen bewusst ein Bedürfnis
            n = self.ns.choose_next_action()
            self.ns.act_on_need(n)
            action_str = f"Aktive Bedürfnis-Erfüllung: {n}"
        else:
            action_str = "Keine direkte Bedürfnis-Erfüllung"

        # Logging
        info = f"Denke an: {self.current_neuron.name} | {sem_str} | {action_str} | Needs: {self.ns}"
        self.thought_log.append(info)

    def run_endlos(self, max_steps=50, delay=0.5):
        """
        Haupt-Loop, um z.B. 50 Iterationen abzufeuern.
        delay in Sekunden, um nicht alles in 0.1s durchzurasen.
        """
        for i in range(max_steps):
            if self._stop:
                break
            self.step()
            time.sleep(delay)

    def stop(self):
        self._stop = True

    def print_log(self):
        print("\n--- Gedankengang / Log ---")
        for line in self.thought_log:
            print(line)
