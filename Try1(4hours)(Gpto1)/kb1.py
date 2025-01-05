#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import uuid
from enum import Enum
from typing import Dict, List, Optional

###############################################################################
#  1) GRUNDLAGEN & ENUMS
###############################################################################

class InfoCategory(Enum):
    """
    Kategorien für unsere W-Fragen: Wer, Was, Warum, Wie, Wo, Wann.
    """
    WER = "Wer"
    WAS = "Was"
    WARUM = "Warum"
    WIE = "Wie"
    WO = "Wo"
    WANN = "Wann"
    
    # Du könntest hier zusätzlich "Wohin", "Welche", "Welche Ursachen", etc. ergänzen.


class InfoValidity(Enum):
    """
    Zwei mögliche Richtigkeiten, wie in deinem Text erwähnt:
    - BELIEVED_TRUE: Gilt als richtig, weil es oft wiederholt wird
    - SCIENTIFICALLY_TRUE: Naturwissenschaftlich bewiesen
    """
    BELIEVED_TRUE = 1
    SCIENTIFICALLY_TRUE = 2


class NeedsVariant(Enum):
    """
    Variante der Bedürfnispyramide:
    - GUT:    Wissen->Nächstenliebe->Ich
    - SCHLECHT: Wissen->Ich->Nächstenliebe
    (stark vereinfacht, an deinen Text angelehnt)
    """
    GUT = 1
    SCHLECHT = 2


class Sentiment(Enum):
    """
    Für einfache 'Stimmung' / 'Tonalität' einer Information:
    NEUTRAL, POSITIV, NEGATIV (könnte man erweitern)
    """
    NEGATIV = -1
    NEUTRAL = 0
    POSITIV = 1


###############################################################################
#  2) INFORMATION & NEURONALES NETZ
###############################################################################

class Information:
    """
    Repräsentiert eine einzelne Informationseinheit.
    Jede Information hat:
    - content: Textueller Inhalt
    - category: welche W-Frage-Kategorie (Wer, Was, Warum, ...)
    - validity: BELIEVED_TRUE oder SCIENTIFICALLY_TRUE
    - sentiment: Grobe Einordnung, ob positiv, negativ oder neutral
    - links: Verknüpfungen zu anderen Informationen (Nachbarn im "Neuronalen Netz")
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
        
        # links: Dict[Information, float] => Gewicht = "Stärke" oder "Wahrscheinlichkeit"
        self.links: Dict['Information', float] = {}
    
    def link_to(self, other: 'Information', strength: float=1.0) -> None:
        """
        Erstellt oder verstärkt eine bidirektionale Verbindung zwischen zwei Infos.
        """
        if other == self:
            return  # Nicht mit sich selbst verlinken
        
        if other not in self.links:
            self.links[other] = 0.0
        self.links[other] += strength
        
        # Gegenseitige Verstärkung
        if self not in other.links:
            other.links[self] = 0.0
        other.links[self] += strength
    
    def __repr__(self):
        s_val = f"({self.sentiment.name[:3]})"  # e.g. (POS)
        return f"Information[{self.category.value}]<{self.content[:30]}>{s_val}"


###############################################################################
#  3) BEDÜRFNISPYRAMIDE + GLÜCKLICHKEITS-SKALA
###############################################################################

class NeedsPyramid:
    """
    Sehr vereinfachte Bedürfnispyramide.
    Wir nehmen 3 Stufen (nach deinem Schema):
    
      - WissenUndEnergie  (höchste Priorität)
      - Du/Nächstenliebe
      - Ich
     
    ...und deren Reihenfolge hängt von 'NeedsVariant' ab.

    Wir behalten zusätzlich ein 'happiness'-Attribut als "Glücksskala".
    """
    def __init__(self, variant: NeedsVariant = NeedsVariant.GUT):
        self.variant = variant
        
        # In deinem Text: "gute" Variante: 
        #   1) WissenUndEnergie, 2) Nächstenliebe, 3) Ich
        # "schlechte" Variante:
        #   1) WissenUndEnergie, 2) Ich, 3) Nächstenliebe
        if variant == NeedsVariant.GUT:
            self.levels = ["WissenUndEnergie", "Nächstenliebe", "Ich"]
        else:
            self.levels = ["WissenUndEnergie", "Ich", "Nächstenliebe"]
        
        # Glücklichkeitswert: in [0..1], Start bei 0.5
        self.happiness = 0.5
    
    def current_priority(self) -> str:
        """
        Rudimentäre Heuristik: Je nach happiness-Wert fokussieren wir eine bestimmte Stufe.
        """
        # Du könntest hier beliebig komplexe Logik einbauen.
        if self.happiness < 0.3:
            return self.levels[0]  # höchste Priorität => Index 0
        elif self.happiness < 0.6:
            return self.levels[1]
        else:
            return self.levels[2]
    
    def adjust_happiness(self, delta: float) -> None:
        """
        Erhöhe oder senke Glück. Clampe in [0..1].
        """
        self.happiness = max(0.0, min(1.0, self.happiness + delta))
    
    def evaluate_satisfaction(self) -> float:
        """
        Gibt den aktuellen Glückswert zurück.
        """
        return self.happiness


###############################################################################
#  4) GEDANKEN "ENDLOS IMPULS" & KREATIVITÄT
###############################################################################

class ThoughtEngine:
    """
    Simuliert den "rollenden Billardball" (Endlos-Impuls),
    der durch das neuronale Netz wandert. 
    - choose_next_info() wählt die nächste Information 
      per "Zufall", "geringster Widerstand" oder "zielgesteuert" aus.
    - step() führt einen Simulationsschritt aus.
    
    Angelehnt an dein Konzept: 3 Möglichkeiten, wer als nächstes "angestoßen" wird:
     1) minimaler Widerstand / stärkster Link
     2) Zufall (Träumen / Kreativität)
     3) Bedürfnisgesteuert -> Sucht Informationen, 
        die thematisch zum Needs-Fokus passen.
    """
    def __init__(self,
                 knowledge_pool: List[Information],
                 needs: NeedsPyramid):
        self.knowledge_pool = knowledge_pool
        self.needs = needs
        
        # Aktuell "rollende Kugel"
        self.current_info: Optional[Information] = None
    
    def choose_next_info(self) -> Information:
        """
        Wählt Info je nach Zufall in 3 Hauptfällen.
        """
        if not self.current_info:
            # Falls wir noch keinen Startpunkt haben => pick random
            self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        neighbors = list(self.current_info.links.items())  # (info, weight)
        
        if not neighbors:
            # Wenn keine Links vorhanden => springe random
            self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        r = random.random()
        
        # 1) Minimaler Widerstand = Wähle Nachbar mit max. Link-Stärke
        if r < 0.4:
            best_neighbor = max(neighbors, key=lambda x: x[1])[0]
            self.current_info = best_neighbor
        
        # 2) Zufall (Kreativ/Träumen)
        elif r < 0.7:
            self.current_info = random.choice(neighbors)[0]
        
        # 3) Bedürfnisgesteuert: Sucht in den Nachbarn nach Keywords,
        #    die zur current_priority() passen
        else:
            focus = self.needs.current_priority().lower()  # z.B. "ich", "nächstenliebe", ...
            # Filtere Nachbarn, deren content/fokus passt
            candidate_neighbors = []
            for (info, weight) in neighbors:
                # z.B. wenn "ich" in info.content => relevant
                if focus in info.content.lower():
                    candidate_neighbors.append((info, weight))
            
            if candidate_neighbors:
                self.current_info = random.choice(candidate_neighbors)[0]
            else:
                # fallback => random neighbor
                self.current_info = random.choice(neighbors)[0]
        
        return self.current_info
    
    def step(self) -> Information:
        """
        Führt einen Schritt aus:
        - Wähle next_info
        - Passe Happiness an (z.B. +0.01 bei 'positiver' Info, -0.01 bei 'negativer')
        - Return next_info
        """
        next_info = self.choose_next_info()
        
        # Einfaches Beispiel: 
        if next_info.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif next_info.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        else:
            # NEUTRAL => +/- 0
            pass
        
        return next_info


###############################################################################
#  5) "DUMMHEIT" - Minimale Einbindung
###############################################################################

def check_dummheit_level(knowledge_pool: List[Information]) -> float:
    """
    Ein (extrem) vereinfachter "Dummheit"-Check:
    - Wir schauen, wie viele W-FRAGEN-Kategorien _gar nicht_ vorhanden sind.
    - Je weniger Vielfalt in den W-Fragen, desto höher die "Dummheit" (0..1).
    
    Du könntest hier natürlich viel komplexere Logik einbauen 
    (z.B. ob das System gar keine Fragen stellt, keine Links hat etc.).
    """
    categories = set(info.category for info in knowledge_pool)
    all_cats = set(InfoCategory)
    
    # Fehlende Kategorien => Indiz
    missing = all_cats - categories
    ratio_missing = len(missing) / len(all_cats)
    
    # ratio_missing = 1 => alle fehlen => total dumm
    # ratio_missing = 0 => nichts fehlt => "nicht dumm"
    return ratio_missing


###############################################################################
#  6) KÜNSTLICHES BEWUSSTSEIN (KB) - ALLES ZUSAMMEN
###############################################################################

class KuenstlichesBewusstsein:
    """
    Fasst alles zusammen:
    - Eine NeedsPyramid (gut oder schlecht)
    - Ein ThoughtEngine, die immer wieder step() aufruft
    - Ein "Speicher" an Informationen (knowledge_pool)
    - Einfache Mechanismen, um neue Infos hinzuzufügen, 
      die "Dummheit" zu checken, etc.
      
    Du könntest hier noch mehr "Systeme" integrieren (z.B. 
    Kopieren von Bewusstseins, Switch von 'Ich' zum PC, usw.)
    """
    def __init__(self, variant: NeedsVariant = NeedsVariant.GUT):
        self.variant = variant
        
        # 1) Erzeuge Basic Needs + Infos (Knowledge)
        self.needs = NeedsPyramid(variant=self.variant)
        self.knowledge_pool: List[Information] = []
        
        # 2) ThoughtEngine
        self.thought_engine = ThoughtEngine(self.knowledge_pool, self.needs)
        
        # 3) Optionale Metadaten
        self.name = f"KB_{variant.name}_{uuid.uuid4().hex[:5]}"
        
        # 4) "Zeitzähler" (Wann) - optional
        self.timestep = 0
    
    def add_information(self,
                        content: str,
                        category: InfoCategory = InfoCategory.WAS,
                        validity: InfoValidity = InfoValidity.BELIEVED_TRUE,
                        sentiment: Sentiment = Sentiment.NEUTRAL) -> Information:
        """
        Eine neue Information in den Pool legen.
        """
        new_info = Information(content, category, validity, sentiment)
        self.knowledge_pool.append(new_info)
        return new_info
    
    def link_informations(self, info_a: Information, info_b: Information, strength: float=1.0):
        """
        Verknüpfe zwei existierende Informationen (bidirektional).
        """
        info_a.link_to(info_b, strength)
    
    def run_thought_cycle(self, steps: int = 1, verbose: bool=True):
        """
        Lässt das KB 'steps' mal denken.
        """
        for i in range(steps):
            self.timestep += 1
            next_info = self.thought_engine.step()
            if verbose:
                h = self.needs.evaluate_satisfaction()
                print(f"[{self.name} | t={self.timestep:03d}] Next Thought => {next_info} | Happiness={h:.3f}")
    
    def measure_dummheit(self) -> float:
        """
        Mache via check_dummheit_level() einen (sehr simplen) 
        'Dummheits'-Index in [0..1].
        """
        return check_dummheit_level(self.knowledge_pool)


###############################################################################
#  7) DEMO / HAUPTPROGRAMM
###############################################################################

def demo_main():
    """
    Einfaches Hauptprogramm, das zwei KünstlicheBewusstseins-Instanzen anlegt:
    - Eines mit 'guter' Bedürfnispyramide
    - Eines mit 'schlechter' Bedürfnispyramide
    
    Dann ein kleines Wissensnetz anlegt, 
    und je 20 steps 'denken' lässt.
    """
    print("Starte Demo...\n")
    
    # 1) Erstelle zwei KB-Instanzen
    kb_good = KuenstlichesBewusstsein(variant=NeedsVariant.GUT)
    kb_bad = KuenstlichesBewusstsein(variant=NeedsVariant.SCHLECHT)
    
    # 2) Fülle etwas Wissen in kb_good
    i_wer_mensch = kb_good.add_information(
        "Elon Musk", 
        category=InfoCategory.WER,
        validity=InfoValidity.SCIENTIFICALLY_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    i_was_ebike = kb_good.add_information(
        "Ein selbstgebautes E-Bike", 
        category=InfoCategory.WAS,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.POSITIV
    )
    i_warum_klima = kb_good.add_information(
        "Klimaschutz rettet Leben", 
        category=InfoCategory.WARUM,
        validity=InfoValidity.SCIENTIFICALLY_TRUE,
        sentiment=Sentiment.POSITIV
    )
    i_wie_abreißen = kb_good.add_information(
        "Ein Haus sprengen", 
        category=InfoCategory.WIE,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEGATIV
    )
    i_wo_bodensee = kb_good.add_information(
        "Am Bodensee", 
        category=InfoCategory.WO,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    i_wann_morgen = kb_good.add_information(
        "Morgen früh", 
        category=InfoCategory.WANN,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    
    # Verlinkungen
    kb_good.link_informations(i_wer_mensch, i_was_ebike, 0.5)
    kb_good.link_informations(i_was_ebike, i_warum_klima, 0.8)
    kb_good.link_informations(i_warum_klima, i_wie_abreißen, 0.1)
    kb_good.link_informations(i_wie_abreißen, i_wo_bodensee, 0.2)
    kb_good.link_informations(i_wo_bodensee, i_wann_morgen, 0.3)
    
    # 3) Fülle etwas Wissen in kb_bad
    x_wer_trump = kb_bad.add_information(
        "Donald Trump", 
        category=InfoCategory.WER,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEGATIV
    )
    x_was_mauerbau = kb_bad.add_information(
        "Mauerbau", 
        category=InfoCategory.WAS,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEGATIV
    )
    x_warum_macht = kb_bad.add_information(
        "Machtgier", 
        category=InfoCategory.WARUM,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEGATIV
    )
    x_wie_wahlkampf = kb_bad.add_information(
        "Wahlkampf betreiben", 
        category=InfoCategory.WIE,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEGATIV
    )
    x_wo_usa = kb_bad.add_information(
        "In den USA", 
        category=InfoCategory.WO,
        validity=InfoValidity.SCIENTIFICALLY_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    x_wann_jetzt = kb_bad.add_information(
        "Jetzt sofort", 
        category=InfoCategory.WANN,
        validity=InfoValidity.BELIEVED_TRUE,
        sentiment=Sentiment.NEUTRAL
    )
    
    # Verlinkungen
    kb_bad.link_informations(x_wer_trump, x_was_mauerbau, 0.9)
    kb_bad.link_informations(x_was_mauerbau, x_warum_macht, 0.7)
    kb_bad.link_informations(x_warum_macht, x_wie_wahlkampf, 0.5)
    kb_bad.link_informations(x_wie_wahlkampf, x_wo_usa, 0.4)
    kb_bad.link_informations(x_wo_usa, x_wann_jetzt, 0.3)
    
    # 4) Lasse beide 20 Schritte "denken"
    print("---- KB_GUT denkt 20 Schritte ----")
    kb_good.run_thought_cycle(steps=20, verbose=True)
    
    print("\n---- KB_BAD denkt 20 Schritte ----")
    kb_bad.run_thought_cycle(steps=20, verbose=True)
    
    # 5) Miss "Dummheit"
    dumm_good = kb_good.measure_dummheit()
    dumm_bad = kb_bad.measure_dummheit()
    print(f"\n[Ergebnis] Dummheit KB_GUT = {dumm_good:.2f}")
    print(f"[Ergebnis] Dummheit KB_BAD = {dumm_bad:.2f}")

    print("\nDemo beendet.")


###############################################################################
#  8) MAIN GUARD
###############################################################################

if __name__ == "__main__":
    demo_main()