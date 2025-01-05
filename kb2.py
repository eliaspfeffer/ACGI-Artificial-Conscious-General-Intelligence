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
    Nur die 'gute' Variante verwenden.
    (Falls in Zukunft doch mehr Varianten nötig: GUT, SCHLECHT, usw.)
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
    
    def link_to(self, other: 'Information', strength: float=1.0):
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
#  4) GEDANKEN-ENGINE & LERNEN VON WIKIPEDIA
###############################################################################

class ThoughtEngine:
    """
    Kern: "rollende Kugel" + Mechanik, um Wikipedia zu durchsuchen.
    
    - choose_next_info(): Welches Info-Objekt betrachte ich als nächstes?
    - step(): Ein Simulationsschritt: 
        -> nächste Info wählen
        -> happiness anpassen
        -> ggf. "lernen" (Wikipedia-Suche), 
           wenn wir zu einer Info noch nicht viel wissen.
    """
    def __init__(self,
                 knowledge_pool: List[Information],
                 needs: NeedsPyramid):
        self.knowledge_pool = knowledge_pool
        self.needs = needs
        self.current_info: Optional[Information] = None
        
        # Schwelle, ab der wir sagen "Ok, wir wissen genug"
        # z.B. "min. 3 weitere verlinkte Infos" => ist "gelernt"
        self.min_link_threshold = 3
        
        # Falls wir zu einer Info (content) bereits gegoogelt haben, 
        # speichern wir das hier, damit wir nicht unendlich oft 
        # dasselbe Wikipedia-Thema abrufen.
        self.already_searched = set()
    
    def choose_next_info(self) -> Information:
        """
        Nimmt ggf. random eine 'unerforschte' Info, sonst verlinkte Nachbarn.
        """
        if not self.knowledge_pool:
            raise RuntimeError("Knowledge pool ist leer - nichts zu tun.")
        
        if not self.current_info:
            # Starte mit einer zufälligen Information
            self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        neighbors = list(self.current_info.links.items())  # (info, weight)
        if not neighbors:
            # Keine Nachbarn => Springe einfach zu einer "unerforschten" Info oder random
            candidates = [inf for inf in self.knowledge_pool if len(inf.links) < 2]
            if candidates:
                self.current_info = random.choice(candidates)
            else:
                self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        # Etwas Zufall
        r = random.random()
        if r < 0.7:
            # wähle einen Nachbarn
            self.current_info = random.choice(neighbors)[0]
        else:
            # wähle Info, die noch "wenig Wissen" hat
            candidates = [inf for inf in self.knowledge_pool if len(inf.links) < self.min_link_threshold]
            if candidates:
                self.current_info = random.choice(candidates)
            else:
                # fallback
                self.current_info = random.choice(self.knowledge_pool)
        return self.current_info
    
    def learn_about(self, info: Information):
        """
        Sucht in Wikipedia nach info.content, 
        holt ggf. Zusammenfassung, baut daraus neue Knoten. 
        Verlinkt sie untereinander und mit dem originalen Info-Knoten.
        """
        topic = info.content.strip()
        
        # 1) Falls schon gesucht -> Abbrechen
        if topic in self.already_searched:
            return
        self.already_searched.add(topic)
        
        # 2) Wikipedia-Suche
        try:
            search_results = wikipedia.search(topic)
            if not search_results:
                return
            
            # Nimm erstes Ergebnis
            page_title = search_results[0]
            # Hole summary
            summary_text = wikipedia.summary(page_title, sentences=2)
            
            # 3) Zerlege summary_text in Sätze oder Phrasen
            #    Sehr grob: split an Punkten
            sentences = summary_text.split(". ")
            
            # 4) Baue pro Satz ein Info-Objekt
            #    (Wir labeln es als WAS und BELIEVED_TRUE, neutral)
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
                # Verlinke es
                new_info.link_to(info, strength=0.5)
                
        except Exception as e:
            # Falls Wikipedia was nicht findet oder offline ist, ignoriere
            print(f"Warnung: Fehler beim Laden aus Wikipedia für '{topic}': {e}")
    
    def step(self) -> Information:
        """
        Ein 'Denkschritt':
          - Nächste Info wählen
          - happiness anpassen (einfaches Schema)
          - Falls Info noch nicht genug verlinkt => Wikipedia-Lernen
        """
        next_info = self.choose_next_info()
        
        # Happiness-Regel: 
        # Positive Infos => +0.01, Negative => -0.01, Neutral => 0
        if next_info.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif next_info.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        
        # Prüfen, ob next_info genug verlinkt ist
        link_count = len(next_info.links)
        if link_count < self.min_link_threshold:
            # => Lerne Info
            self.learn_about(next_info)
        
        return next_info


###############################################################################
#  5) DAS KÜNSTLICHE BEWUSSTSEIN (GUT)
###############################################################################

class KuenstlichesBewusstsein:
    """
    - Nur 'gute' Pyramide
    - Endlosschleife: unendlich 'step()'
    - knowledge_pool
    - Manuelles Hinzufügen erster Infos
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
        bis man das Skript z.B. via KeyboardInterrupt beendet.
        """
        print(f"[{self.name}] Starte unendliche Schleife. Drücke Strg+C zum Abbrechen.")
        try:
            step_counter = 0
            while True:
                step_counter += 1
                self.timestep += 1
                info_obj = self.thought_engine.step()
                
                # Einfaches Logging alle x Steps
                if step_counter % 5 == 0:
                    h = self.needs.evaluate_satisfaction()
                    print(f"[{self.name} | step={step_counter}] Denke über: {info_obj.content[:50]} ... | Happiness={h:.3f}")
                    
                # Kleiner Sleep, damit man den Output besser verfolgen kann
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
    - Fügt eine Handvoll Startinformationen hinzu
    - Verlinkt sie
    - Startet dann die Endlosschleife (Wikipedia-Lernen etc.)
    """
    
    kb = KuenstlichesBewusstsein()
    
    # 1) Startinfos hinzufügen
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
    
    # 2) Links
    kb.link_informations(info_klima, info_ebike, 0.8)
    kb.link_informations(info_klima, info_bodensee, 0.4)
    kb.link_informations(info_ebike, info_bodensee, 0.2)
    
    # 3) Unendliche Schleife starten
    kb.run_infinite_loop()

# -----------------------------------------------------------------------------
# MAIN GUARD
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    demo_main()
