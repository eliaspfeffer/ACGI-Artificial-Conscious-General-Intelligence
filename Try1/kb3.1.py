#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import uuid
import time
import wikipedia  # pip install wikipedia
from enum import Enum
from typing import Dict, List, Optional

###############################################################################
#  1) ENUMS & BASIS
###############################################################################

class InfoCategory(Enum):
    """
    Kategorien als grobe Anlehnung an W-Fragen.
    """
    WER = "Wer"
    WAS = "Was"
    WARUM = "Warum"
    WIE = "Wie"
    WO = "Wo"
    WANN = "Wann"

class InfoValidity(Enum):
    """
    Richtigkeiten wie in deinem Konzept.
    """
    BELIEVED_TRUE = 1
    SCIENTIFICALLY_TRUE = 2

class NeedsVariant(Enum):
    """
    Nur die 'gute' Variante.
    """
    GUT = 1

class Sentiment(Enum):
    """
    Vereinfachte Einteilung in positiv, negativ, neutral.
    """
    NEGATIV = -1
    NEUTRAL = 0
    POSITIV = 1

###############################################################################
#  2) INFORMATION & NEURONALES NETZ
###############################################################################

class Information:
    """
    Knoten in unserem Wissens-Netz.
    content: Text
    category: W-Frage-Kategorie
    validity: BELIEVED_TRUE oder SCIENTIFICALLY_TRUE
    sentiment: +/-/0
    links: Andere Informationen (bidirektional, mit Gewicht)
    """
    def __init__(self,
                 content: str,
                 category: InfoCategory = InfoCategory.WAS,
                 validity: InfoValidity = InfoValidity.BELIEVED_TRUE,
                 sentiment: Sentiment = Sentiment.NEUTRAL):
        self.id = uuid.uuid4()
        self.content = content
        self.category = category
        self.validity = validity
        self.sentiment = sentiment
        
        self.links: Dict['Information', float] = {}
    
    def link_to(self, other: 'Information', strength: float = 1.0):
        if other == self:
            return
        if other not in self.links:
            self.links[other] = 0.0
        self.links[other] += strength
        
        if self not in other.links:
            other.links[self] = 0.0
        other.links[self] += strength
    
    def __repr__(self):
        cat = self.category.value
        return f"Information[{cat}]<{self.content[:30]}>"

###############################################################################
#  3) BEDÜRFNISPYRAMIDE (GUT) & GLÜCKSSKALA
###############################################################################

class NeedsPyramid:
    """
    Nur 'gute' Variante: 1) WissenUndEnergie, 2) Nächstenliebe, 3) Ich
    plus einfache Glücksskala [0..1].
    """
    def __init__(self):
        self.levels = ["WissenUndEnergie", "Nächstenliebe", "Ich"]
        self.happiness = 0.5
    
    def current_priority(self) -> str:
        """
        Naive Logik: Bei <0.3 => Stufe 0, <0.6 => Stufe 1, sonst Stufe 2.
        """
        if self.happiness < 0.3:
            return self.levels[0]
        elif self.happiness < 0.6:
            return self.levels[1]
        else:
            return self.levels[2]
    
    def adjust_happiness(self, delta: float):
        self.happiness = max(0.0, min(1.0, self.happiness + delta))
    
    def evaluate_satisfaction(self) -> float:
        return self.happiness

###############################################################################
#  4) GEDANKEN-ENGINE & LERNMECHANISMEN
###############################################################################

class ThoughtEngine:
    """
    Kern: "rollende Kugel" + Mechanik, um Wikipedia zu durchsuchen und
    neue Gedanken zu entwickeln.
    
    - choose_next_info(): Welches Info-Objekt betrachte ich als nächstes?
      Berücksichtigt:
        - Aufmerksamkeitsspanne (attention_span)
        - Zufällige Drift
        - Verknüpfungen (neighbors)
    - step(): Ein Simulationsschritt
        -> Nächste Info wählen
        -> Happiness anpassen
        -> Wikipedia lernen
        -> Neue Gedanken
    """
    def __init__(self, knowledge_pool: List[Information], needs: NeedsPyramid):
        self.knowledge_pool = knowledge_pool
        self.needs = needs
        
        # Aktuelle "rollende Kugel"
        self.current_info: Optional[Information] = None
        
        # Schwelle, ab der wir sagen "Ok, wir wissen genug"
        self.min_link_threshold = 3
        
        # Für Wikipedia-Lernen: bereits gesuchte Topics merken
        self.already_searched = set()
        
        # Aufmerksamkeitsspanne
        self.attention_span = 15
        self.steps_in_focus = 0
        
        # Chance zufällig vom Thema abzuweichen
        self.drift_probability = 0.1
        
        # Chance, einfach so einen neuen Gedanken zu entwickeln
        self.new_thought_probability = 0.2
    
    def choose_next_info(self) -> Information:
        """
        Wählt die nächste Information basierend auf:
         - Fokusdauer (Wechsel nach attention_span)
         - Zufälliges Abdriften
         - Verknüpfte Nachbarn
        """
        if not self.knowledge_pool:
            raise RuntimeError("Knowledge pool ist leer - nichts zu tun.")
        
        # 1) Thema wechseln, falls kein aktuelles Info
        #    oder wenn attention_span überschritten
        if (not self.current_info) or (self.steps_in_focus >= self.attention_span):
            # Suche nach Infos, die noch nicht "genug" verlinkt sind
            candidates = [inf for inf in self.knowledge_pool if len(inf.links) < self.min_link_threshold]
            if not candidates:  # Falls es keine "unvollständigen" gibt
                candidates = self.knowledge_pool
            
            self.current_info = random.choice(candidates)
            self.steps_in_focus = 0
            return self.current_info
        
        # 2) Prüfen, ob wir zufällig driften
        if random.random() < self.drift_probability:
            self.current_info = random.choice(self.knowledge_pool)
            self.steps_in_focus = 0
            return self.current_info
        
        # 3) Ansonsten: Bleiben wir beim Thema, aber wandern evtl. zu einem Nachbarn
        self.steps_in_focus += 1
        neighbors = list(self.current_info.links.items())  # (info, weight)
        if not neighbors:
            # Keine Nachbarn => bleib bei dir selbst
            return self.current_info
        
        # 50% Chance: bleibe beim selben Info, 50% => gehe zu einem Nachbarn
        if random.random() < 0.5:
            return self.current_info
        else:
            return random.choice(neighbors)[0]
    
    def learn_about(self, info: Information):
        """
        Sucht in Wikipedia nach info.content, holt Zusammenfassung, 
        baut daraus neue Knoten. Verlinkt sie mit info.
        """
        topic = info.content.strip()
        
        if topic in self.already_searched:
            return
        self.already_searched.add(topic)
        
        try:
            search_results = wikipedia.search(topic)
            if not search_results:
                return
            # Nimm erstes Ergebnis
            page_title = search_results[0]
            summary_text = wikipedia.summary(page_title, sentences=2)
            
            # Zerlege summary_text in Sätze (sehr grob)
            sentences = summary_text.split(". ")
            
            for s in sentences:
                clean_s = s.strip()
                if len(clean_s) < 5:
                    continue
                new_info = Information(
                    content=clean_s,
                    category=InfoCategory.WAS,
                    validity=InfoValidity.BELIEVED_TRUE,
                    sentiment=Sentiment.NEUTRAL
                )
                self.knowledge_pool.append(new_info)
                new_info.link_to(info, strength=0.5)
            
        except Exception as e:
            print(f"Warnung: Fehler beim Laden aus Wikipedia für '{topic}': {e}")
    
    def step(self) -> Information:
        """
        Ein Denk-Schritt:
         1) Nächste Info wählen
         2) Happiness anpassen
         3) Wikipedia-Lernen, wenn Info < min_link_threshold
         4) Neue Gedanken
        """
        next_info = self.choose_next_info()
        
        # Falls wir das Thema wechseln -> setze current_info
        self.current_info = next_info
        
        # Happiness: je nach Sentiment +/-
        if next_info.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif next_info.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        
        # Erschöpfungseffekt: wenn schon länger auf demselben Thema
        if self.steps_in_focus >= (self.attention_span / 2):
            self.needs.adjust_happiness(-0.01)
        
        # Falls Info noch nicht genug verlinkt => Wikipedia-Lernen
        if len(next_info.links) < self.min_link_threshold:
            self.learn_about(next_info)
        
        # Neue Gedanken (random) hinzufügen
        if random.random() < self.new_thought_probability:
            new_content = f"Random Thought {uuid.uuid4().hex[:4]}"
            new_info = Information(content=new_content, category=InfoCategory.WAS)
            self.knowledge_pool.append(new_info)
            # Verknüpfen mit aktuellem Info
            next_info.link_to(new_info, strength=0.5)
            print(f"Neuer Gedanke entwickelt: {new_content}")
        
        return next_info

###############################################################################
#  5) DAS KÜNSTLICHE BEWUSSTSEIN (GUT)
###############################################################################

class KuenstlichesBewusstsein:
    """
    - Nur 'gute' Pyramide
    - Endlosschleife
    - Dynamisches Wechseln von Themen
    - Wikipedia-Lernen
    - Neue Gedanken
    """
    def __init__(self):
        self.variant = NeedsVariant.GUT
        self.needs = NeedsPyramid()
        self.knowledge_pool: List[Information] = []
        self.thought_engine = ThoughtEngine(self.knowledge_pool, self.needs)
        self.name = f"KB_GUT_{uuid.uuid4().hex[:4]}"
        self.timestep = 0
    
    def add_information(self,
                        content: str,
                        category: InfoCategory = InfoCategory.WAS,
                        validity: InfoValidity = InfoValidity.BELIEVED_TRUE,
                        sentiment: Sentiment = Sentiment.NEUTRAL) -> Information:
        info = Information(content, category, validity, sentiment)
        self.knowledge_pool.append(info)
        return info
    
    def link_informations(self, info_a: Information, info_b: Information, strength: float=1.0):
        info_a.link_to(info_b, strength)
    
    def run_infinite_loop(self):
        """
        Lässt das Bewusstsein 'unendlich' denken,
        bis man das Skript per Strg+C beendet.
        """
        print(f"[{self.name}] Starte unendliche Schleife. Drücke Strg+C zum Abbrechen.")
        step_counter = 0
        try:
            while True:
                step_counter += 1
                self.timestep += 1
                info_obj = self.thought_engine.step()
                
                # Logge alle x Schritte
                if step_counter % 5 == 0:
                    h = self.needs.evaluate_satisfaction()
                    print(f"[{self.name} | step={step_counter}] "
                          f"Denke über: {info_obj.content[:50]} ... | Happiness={h:.3f}")
                
                # Kurzer Sleep, damit man den Output verfolgen kann
                time.sleep(1.0)
        except KeyboardInterrupt:
            print(f"\n[{self.name}] Manuelle Unterbrechung. Beende Endlosschleife.")
        except Exception as ex:
            print(f"\n[{self.name}] Ausnahmefehler: {ex}. Beende Endlosschleife.")

###############################################################################
#  6) DEMO-HAUPTPROGRAMM
###############################################################################

def demo_main():
    """
    - Erzeugt ein 'gutes KB'
    - Fügt Startinformationen hinzu
    - Verlinkt sie
    - Startet dann die Endlosschleife
    """
    kb = KuenstlichesBewusstsein()
    
    # Startinformationen
    info_klima = kb.add_information(
        content="Klimaschutz", 
        category=InfoCategory.WAS,
        validity=InfoValidity.SCIENTIFICALLY_TRUE,
        sentiment=Sentiment.POSITIV
    )
    info_ebike = kb.add_information(
        content="E-Bike",
        category=InfoCategory.WAS,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.POSITIV
    )
    info_bodensee = kb.add_information(
        content="Bodensee",
        category=InfoCategory.WO,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    
    # Verlinkungen
    kb.link_informations(info_klima, info_ebike, 0.8)
    kb.link_informations(info_klima, info_bodensee, 0.4)
    kb.link_informations(info_ebike, info_bodensee, 0.2)
    
    # Endlosschleife
    kb.run_infinite_loop()

if __name__ == "__main__":
    demo_main()
