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
    WER = "Wer"
    WAS = "Was"
    WARUM = "Warum"
    WIE = "Wie"
    WO = "Wo"
    WANN = "Wann"

class InfoValidity(Enum):
    BELIEVED_TRUE = 1
    SCIENTIFICALLY_TRUE = 2

class NeedsVariant(Enum):
    GUT = 1

class Sentiment(Enum):
    NEGATIV = -1
    NEUTRAL = 0
    POSITIV = 1

###############################################################################
#  2) INFORMATION & NEURONALES NETZ
###############################################################################

class Information:
    """
    Knoten in unserem Wissens-Netz.
    Neu: 'visit_count' = wie oft wurde dieser Knoten schon fokussiert?
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
        
        # Zählt, wie oft wir diesen Knoten aktiv besucht haben
        self.visit_count: int = 0
    
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
        return f"Info[{cat}]<{self.content[:30]}|visits={self.visit_count}>"

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
        if self.happiness < 0.3:
            return self.levels[0]  # WissenUndEnergie
        elif self.happiness < 0.6:
            return self.levels[1]  # Nächstenliebe
        else:
            return self.levels[2]  # Ich
    
    def adjust_happiness(self, delta: float):
        self.happiness = max(0.0, min(1.0, self.happiness + delta))
    
    def evaluate_satisfaction(self) -> float:
        return self.happiness

###############################################################################
#  4) GEDANKEN-ENGINE & LERNEN VON WIKIPEDIA
###############################################################################

class ThoughtEngine:
    """
    - choose_next_info(): Endlos-Impuls mit 3 Modi (geringster Widerstand, Zufall, Bedürfnis).
      + 'Boredom-Faktor': Wenn ein Info-Knoten schon zu oft besucht, 
        oder wir hängen ewig am selben Subthema => drift to new node.
      
    - step(): Ein Simulationsschritt 
        => happiness anpassen
        => check "Wikipedia-Lernen"
    
    - learn_about(...): holt Wikipedia-Infos, generiert Knoten
    """
    def __init__(self,
                 knowledge_pool: List[Information],
                 needs: NeedsPyramid):
        self.knowledge_pool = knowledge_pool
        self.needs = needs
        self.current_info: Optional[Information] = None
        
        self.min_link_threshold = 3
        self.already_searched = set()
        
        # Grenzwert, ab wann wir "gelangweilt" von einem Knoten sind
        self.boredom_threshold = 5  
        
    def choose_next_info(self) -> Information:
        if not self.knowledge_pool:
            raise RuntimeError("Knowledge pool ist leer.")
        
        # Falls wir keinen Startpunkt haben => pick random
        if not self.current_info:
            self.current_info = random.choice(self.knowledge_pool)
            self.current_info.visit_count += 1
            return self.current_info
        
        # "Endlos Impuls" ~ 3 Modi
        r = random.random()
        
        # 1) Minimaler Widerstand (stärkster Link)
        if r < 0.3:
            neighbors = list(self.current_info.links.items())  # (info, weight)
            if not neighbors:
                # Falls keine Nachbarn, wähle random
                self.current_info = random.choice(self.knowledge_pool)
            else:
                # Wähle best neighbor
                best_neighbor = max(neighbors, key=lambda x: x[1])[0]
                self.current_info = best_neighbor
        
        # 2) Zufall
        elif r < 0.6:
            # Wähle random neighbor, 
            # wenn bored: random ANY from knowledge_pool
            neighbors = list(self.current_info.links.items())
            if neighbors:
                # Check boredom
                if self.current_info.visit_count > self.boredom_threshold:
                    # => "Breche aus" auf total random Node
                    self.current_info = random.choice(self.knowledge_pool)
                else:
                    self.current_info = random.choice(neighbors)[0]
            else:
                self.current_info = random.choice(self.knowledge_pool)
        
        # 3) Bedürfnis-gesteuert
        else:
            focus = self.needs.current_priority().lower()
            neighbors = list(self.current_info.links.items())
            candidate_neighbors = []
            
            for (info, weight) in neighbors:
                # such im content nach 'focus'
                if focus in info.content.lower():
                    candidate_neighbors.append((info, weight))
            if candidate_neighbors:
                # Falls bored: randomize
                if self.current_info.visit_count > self.boredom_threshold:
                    self.current_info = random.choice(self.knowledge_pool)
                else:
                    self.current_info = random.choice(candidate_neighbors)[0]
            else:
                # fallback => random
                self.current_info = random.choice(self.knowledge_pool)
        
        # Erhöhe visit_count
        self.current_info.visit_count += 1
        
        # Optional: Link-Stärke abbauen, wenn wir hier schon zu oft waren:
        # if self.current_info.visit_count > 10:
        #     # Reduziere z.B. die Linkstärke um 10%
        #     for nbr in self.current_info.links:
        #         self.current_info.links[nbr] *= 0.9
        
        return self.current_info
    
    def learn_about(self, info: Information):
        """
        Wikipedia-Suche für info.content,
        falls nicht schon geschehen. Erzeugt pro Satz neue Knoten.
        """
        topic = info.content.strip()
        if topic in self.already_searched:
            return
        self.already_searched.add(topic)
        
        try:
            search_results = wikipedia.search(topic)
            if not search_results:
                return
            
            page_title = search_results[0]
            summary_text = wikipedia.summary(page_title, sentences=2)
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
        next_info = self.choose_next_info()
        
        # Happiness-Regel: 
        if next_info.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif next_info.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        
        # Prüfen, ob next_info genug verlinkt ist
        link_count = len(next_info.links)
        if link_count < self.min_link_threshold:
            self.learn_about(next_info)
        
        return next_info

###############################################################################
#  5) KÜNSTLICHES BEWUSSTSEIN (GUT) - UNENDLICHE SCHLEIFE
###############################################################################

class KuenstlichesBewusstsein:
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
        print(f"[{self.name}] Starte unendliche Schleife. Strg+C zum Abbruch.")
        try:
            step_counter = 0
            while True:
                step_counter += 1
                self.timestep += 1
                info_obj = self.thought_engine.step()
                
                # Alle x Schritte eine kleine Ausgabe
                if step_counter % 5 == 0:
                    h = self.needs.evaluate_satisfaction()
                    print(f"[{self.name} | step={step_counter}] "
                          f"Denke über: {info_obj} | Happiness={h:.3f}")
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            print(f"\n[{self.name}] Manuelle Unterbrechung. Ende.")
        except Exception as ex:
            print(f"\n[{self.name}] Ausnahmefehler: {ex}. Ende.")

###############################################################################
#  6) HAUPTPROGRAMM (DEMO)
###############################################################################

def demo_main():
    kb = KuenstlichesBewusstsein()
    
    # Beispiel-Startinfos
    i_klima = kb.add_information(
        content="Klimaschutz",
        category=InfoCategory.WAS,
        validity=InfoValidity.SCIENTIFICALLY_TRUE,
        sentiment=Sentiment.POSITIV
    )
    i_ebike = kb.add_information(
        content="E-Bike",
        category=InfoCategory.WAS,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.POSITIV
    )
    i_bodensee = kb.add_information(
        content="Bodensee",
        category=InfoCategory.WO,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    
    kb.link_informations(i_klima, i_ebike, 0.8)
    kb.link_informations(i_klima, i_bodensee, 0.4)
    kb.link_informations(i_ebike, i_bodensee, 0.2)
    
    kb.run_infinite_loop()

if __name__ == "__main__":
    demo_main()
