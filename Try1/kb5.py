#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import uuid
import time
from enum import Enum
from typing import Dict, List, Optional

###############################################################################
#  1) ENUMS & BASIS
###############################################################################

class InfoCategory(Enum):
    """
    Die 6 W-Fragen: Wer, Was, Warum, Wie, Wo, Wann.
    (Andere wie Wohin könnte man ergänzen.)
    """
    WER = "Wer"       # Alles, was Augen hat oder bewusst ist
    WAS = "Was"       # Alles Wissen / Realität
    WARUM = "Warum"   # Erklärung/Ursache
    WIE = "Wie"       # Detail-Möglichkeiten / Methoden
    WO = "Wo"         # Koordinaten / Orte
    WANN = "Wann"     # Zeit / Frequenz

class InfoValidity(Enum):
    """
    'Richtigkeit': gilt_als_richtig vs. ist_physikalisch_bestaetigt
    """
    GILT_ALS_RICHTIG = 1           # weil es am häufigsten wiederholt wird
    IST_PHYSIKALISCH_BESTAETIGT = 2  # naturwiss. / mathematisch verifiziert

class Sentiment(Enum):
    """
    Einfaches Stimmungs-Flag, um z.B. Happiness zu beeinflussen.
    """
    NEGATIV = -1
    NEUTRAL = 0
    POSITIV = 1

###############################################################################
#  2) INFORMATION & WISSEN
###############################################################################

class Information:
    """
    Eine 'Nervenzelle' im 'verknüpften System'.
    
    - content: z.B. "Apfel" oder "Der Apfel ist rot"
    - category: W-Frage-Kategorie
    - validity: GILT_ALS_RICHTIG oder IST_PHYSIKALISCH_BESTAETIGT
    - sentiment: NEUTRAL, POSITIV, NEGATIV
    - links: Verweise auf andere Informationen (gewichtete Kanten)
    """
    def __init__(
        self,
        content: str,
        category: InfoCategory = InfoCategory.WAS,
        validity: InfoValidity = InfoValidity.GILT_ALS_RICHTIG,
        sentiment: Sentiment = Sentiment.NEUTRAL
    ):
        self.id = uuid.uuid4()
        self.content = content
        self.category = category
        self.validity = validity
        self.sentiment = sentiment
        
        # Bidirektionale Links: Info -> weight
        self.links: Dict['Information', float] = {}
    
    def link_to(self, other: 'Information', strength: float = 1.0) -> None:
        """
        Stellt eine (ggf. neue) bidirektionale Verbindung zu 'other' her.
        """
        if other == self:
            return
        self.links[other] = self.links.get(other, 0.0) + strength
        other.links[self] = other.links.get(self, 0.0) + strength
    
    def __repr__(self):
        c = self.category.value
        short_text = (self.content[:40] + "...") if len(self.content) > 40 else self.content
        return f"Information[{c}]<{short_text}>"

###############################################################################
#  3) BEDÜRFNISPYRAMIDE (GUT) + GLÜCKLICHKEIT
###############################################################################

class NeedsPyramid:
    """
    Gute Variante der Bedürfnispyramide:
        1) Wissen & Energie
        2) Du / Nächstenliebe
        3) Ich
    
    plus einfache "Glücklichkeitsskala" [0..1].
    """
    def __init__(self):
        # Reihenfolge: [höchste Priorität, ...]
        self.levels = ["WissenUndEnergie", "DuNächstenliebe", "Ich"]
        self.happiness = 0.5  # Startwert
    
    def current_priority(self) -> str:
        """
        Sehr naive Logik: je nach Happiness rückt ein anderes Level in den Fokus.
        """
        if self.happiness < 0.3:
            return self.levels[0]  # Wissen & Energie
        elif self.happiness < 0.6:
            return self.levels[1]  # Du / Nächstenliebe
        else:
            return self.levels[2]  # Ich
    
    def adjust_happiness(self, delta: float):
        """
        Passt die Happiness an, geclamped in [0..1].
        """
        self.happiness = max(0.0, min(1.0, self.happiness + delta))
    
    def evaluate_satisfaction(self) -> float:
        return self.happiness

###############################################################################
#  4) SEMANTIK-CHECK & HELFER
###############################################################################

def check_semantics(info_a: Information, info_b: Information) -> bool:
    """
    Sehr vereinfachter 'Semantik-Check', um klar unsinnige Verknüpfungen zu filtern.
    Beispiel: "Der Apfel kauft einen Traktor" => unsinnig -> return False
    
    Wir machen das hier minimal:
      - Wenn info_a.category = WER und info_b.category = WAS, dann okay.
      - Wenn "Apfel" und "Traktor" => gucken wir, ob "kauft" im Satz steckt (unsinnig).
    Du kannst hier beliebig mehr Cases reinhängen!
    """
    text_a = info_a.content.lower()
    text_b = info_b.content.lower()
    
    # Beispiel: 'apfel' + 'kauft' => unsinn
    if "apfel" in text_a and "kauft" in text_b:
        return False
    if "apfel" in text_b and "kauft" in text_a:
        return False
    
    # Minimalbeispiel: wer -> was => okay, was -> was => okay
    return True

def derive_new_knowledge(known1: Information, known2: Information) -> Optional[Information]:
    """
    Versuch eines Minimalkonzepts "Aus altem Wissen neues ableiten":
    
    Wenn known1 = "Der Apfel ist rot" (WAS),
       known2 = "Rot ist eine Farbe" (WAS),
    => Then we might create "Der Apfel hat eine Farbe" (WAS).
    
    Super stark vereinfacht.
    """
    c1 = known1.content.lower()
    c2 = known2.content.lower()
    
    # Bloßes Beispiel: Apfel + rot + Farbe => Apfel hat Farbe
    if ("apfel" in c1) and ("rot" in c1) and ("rot" in c2) and ("farbe" in c2):
        new_info = Information(
            content="Der Apfel hat eine Farbe.",
            category=InfoCategory.WAS,
            validity=InfoValidity.GILT_ALS_RICHTIG,
            sentiment=Sentiment.NEUTRAL
        )
        return new_info
    
    return None

###############################################################################
#  5) GEDANKEN-ENGINE (Endlos Impuls)
###############################################################################

class ThoughtEngine:
    """
    Steuert den 'rollenden Billardball':
    
    - current_info: welche Info 'bewegt' sich gerade?
    - 3 Modi, wie wir zur nächsten Info kommen:
        1) Der geringste Widerstand (stärkste Link)
        2) Zufall (Träume / Flipflop)
        3) Selbstgesteuert (Bedürfnispyramide-Fokus: 
           wir suchen z.B. Info, die 'passt')
    - Semantik-Filter: wir verknüpfen nur, wenn es Sinn ergibt.
    - Ableiten neuen Wissens.
    """
    def __init__(self, knowledge_pool: List[Information], needs: NeedsPyramid):
        self.knowledge_pool = knowledge_pool
        self.needs = needs
        self.current_info: Optional[Information] = None
        
        # Wahrscheinlichkeiten:
        self.prob_lowest_resistance = 0.3
        self.prob_random = 0.3
        self.prob_self_directed = 0.4
    
    def choose_next_info(self) -> Information:
        """
        Wählt mithilfe der 3 Modi die nächste Info.
        """
        if not self.knowledge_pool:
            raise RuntimeError("Wissenspool ist leer!")
        
        # Falls noch keine Info => pick random
        if not self.current_info:
            self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        # Neighbors = Liste (info, weight)
        neighbors = list(self.current_info.links.items())
        
        # Weighted random: welcher Modus?
        r = random.random()
        if r < self.prob_lowest_resistance:
            # 1) Der geringste Widerstand => stärke Link
            if neighbors:
                best_neighbor = max(neighbors, key=lambda x: x[1])[0]
                self.current_info = best_neighbor
            else:
                # Keine Nachbarn => random
                self.current_info = random.choice(self.knowledge_pool)
        elif r < (self.prob_lowest_resistance + self.prob_random):
            # 2) Zufall
            self.current_info = random.choice(self.knowledge_pool)
        else:
            # 3) Bedürfnis / Selbstgesteuert
            focus = self.needs.current_priority().lower()  # z.B. "wissenundenergie"
            # Finde Infos, deren content den Focus-String enthält
            candidates = []
            for info in self.knowledge_pool:
                if focus in info.content.lower():
                    candidates.append(info)
            if candidates:
                self.current_info = random.choice(candidates)
            else:
                # Fallback => random
                self.current_info = random.choice(self.knowledge_pool)
        
        return self.current_info
    
    def create_random_link(self):
        """
        Manchmal verbinden wir zwei zufällige Infos, wenn Semantik es zulässt.
        """
        if len(self.knowledge_pool) < 2:
            return
        
        a, b = random.sample(self.knowledge_pool, 2)
        # Falls ok, dann Link
        if check_semantics(a, b):
            # Erhöhe Verbindungsstärke um 0.5
            a.link_to(b, 0.5)
    
    def derive_knowledge_step(self):
        """
        Versuche, aus existierenden Paaren (known1, known2) neues Wissen abzuleiten.
        Nur ab und zu, damit es nicht explodiert.
        """
        # Minimal: wähle 2 random Info und guck, ob man was ableiten kann
        if len(self.knowledge_pool) < 2:
            return
        info_a, info_b = random.sample(self.knowledge_pool, 2)
        new_info = derive_new_knowledge(info_a, info_b)
        if new_info:
            # Falls wir was ableiten können
            self.knowledge_pool.append(new_info)
            # Verlinke es rudimentär
            info_a.link_to(new_info, 0.5)
            info_b.link_to(new_info, 0.5)
            print(f"[Ableitung] Neues Wissen entstanden: {new_info.content}")
    
    def step(self) -> Information:
        """
        Ein 'Gedanken'-Schritt:
          1) Nächste Info wählen
          2) Happiness anpassen (z.B. +0.01, -0.01)
          3) Random Link => semantischer Check
          4) Aus altem Wissen neues ableiten
        """
        next_info = self.choose_next_info()
        
        # Happiness-Anpassung rudimentär
        if next_info.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif next_info.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        
        # Manchmal random Link erstellen
        if random.random() < 0.2:
            self.create_random_link()
        
        # Manchmal neues Wissen ableiten
        if random.random() < 0.1:
            self.derive_knowledge_step()
        
        return next_info

###############################################################################
#  6) KÜNSTLICHES BEWUSSTSEIN
###############################################################################

class KuenstlichesBewusstsein:
    """
    - Enthält 'Bedürfnispyramide' (gute Variante).
    - Enthält 'ThoughtEngine' => Endlos Impuls in step().
    - Speichert ein 'verknüpftes System' => knowledge_pool
    """
    def __init__(self):
        self.needs = NeedsPyramid()
        self.knowledge_pool: List[Information] = []
        self.engine = ThoughtEngine(self.knowledge_pool, self.needs)
        self.name = f"KB_GUT_{uuid.uuid4().hex[:4]}"
        self.timestep = 0
    
    def add_information(self,
                        content: str,
                        category: InfoCategory,
                        validity: InfoValidity = InfoValidity.GILT_ALS_RICHTIG,
                        sentiment: Sentiment = Sentiment.NEUTRAL) -> Information:
        info = Information(content, category, validity, sentiment)
        self.knowledge_pool.append(info)
        return info
    
    def run_infinite_loop(self):
        """
        Lässt das KB ewig 'nachdenken'. Abbruch via Strg+C.
        """
        print(f"[{self.name}] Starte Endlosschleife. Drücke Strg+C zum Abbrechen.")
        step_count = 0
        try:
            while True:
                step_count += 1
                self.timestep += 1
                current_info = self.engine.step()
                
                # Logge alle 5 Steps
                if step_count % 5 == 0:
                    h = self.needs.evaluate_satisfaction()
                    print(f"[{self.name} | step={step_count}] "
                          f"Aktuelle Info: \"{current_info.content[:60]}\" | Happiness={h:.3f}")
                
                # Kurzer Sleep zum Beobachten
                time.sleep(1.0)
        except KeyboardInterrupt:
            print(f"\n[{self.name}] Manuelle Unterbrechung. Ende.")
        except Exception as e:
            print(f"\n[{self.name}] Fehler: {e}")

###############################################################################
#  7) DEMO
###############################################################################

def demo_main():
    kb = KuenstlichesBewusstsein()
    
    # Beispiel-Infos hinzufügen
    info_apfel = kb.add_information(
        content="Apfel", 
        category=InfoCategory.WAS,
        validity=InfoValidity.IST_PHYSIKALISCH_BESTAETIGT,
        sentiment=Sentiment.NEUTRAL
    )
    info_baum = kb.add_information(
        content="Baum", 
        category=InfoCategory.WAS,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.NEUTRAL
    )
    info_rot = kb.add_information(
        content="Rot ist eine Farbe", 
        category=InfoCategory.WAS,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.NEUTRAL
    )
    info_apfel_rot = kb.add_information(
        content="Der Apfel ist rot", 
        category=InfoCategory.WAS,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.POSITIV  # pos. => steigert Happiness minimal
    )
    
    # Verbinde etwas
    info_apfel.link_to(info_baum, 0.5)
    info_apfel.link_to(info_apfel_rot, 0.8)
    info_rot.link_to(info_apfel_rot, 0.5)
    
    # Starte Endlosschleife
    kb.run_infinite_loop()

if __name__ == "__main__":
    demo_main()
