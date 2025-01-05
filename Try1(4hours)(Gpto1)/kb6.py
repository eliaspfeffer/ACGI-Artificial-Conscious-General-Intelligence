#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================================
 Ein extrem ausführliches und kommentiertes Python-Skript, um die in deinem
 Buch (Kapitel zur "Allgemeinen Künstlichen Intelligenz / künstlichem Bewusstsein")
 beschriebenen Konzepte möglichst nah und detailliert umzusetzen.
 
 HINWEIS: Das ist kein "fertiges" AGI-System, sondern eine Demonstration,
 wie man die Theorien aus deinem Text in Code Gießen könnte.
===============================================================================
"""

import random
import uuid
import time
from enum import Enum
from typing import Dict, List, Optional

###############################################################################
# 1) GRUNDLAGEN: W-FRAGEN, RICHTIGKEIT, SENTIMENT, ...
###############################################################################

class WFragenCategory(Enum):
    """
    Die 6 W-Fragen nach deinem Buch:
      - WER   : Alles, was Augen hat oder Bewusstsein
      - WAS   : Alles Wissen / Realität / Objekte / Zustände
      - WARUM : Erklärungen / Ursachen
      - WIE   : Detail-Möglichkeiten / Methoden
      - WO    : Koordinaten / Positionen im Raum
      - WANN  : Alles mit Frequenz / Zeitbezug

    Du beschreibst in deinem Buch, dass "Wer, Was, Warum" die wichtigsten
    drei Fragen seien und "Wie, Wo, Wann" eher nachrangig. Trotzdem führen wir
    alle 6 auf, damit wir den Code flexibel halten.
    """
    WER = "Wer"
    WAS = "Was"
    WARUM = "Warum"
    WIE = "Wie"
    WO = "Wo"
    WANN = "Wann"


class InfoValidity(Enum):
    """
    Definition laut Buch:
    Es gibt zwei mögliche "Richtigkeiten":
    1) GILT_ALS_RICHTIG (weil es am häufigsten wiederholt wurde)
    2) IST_PHYSIKALISCH_BESTAETIGT (naturwissenschaftlich / mathematisch)
    """
    GILT_ALS_RICHTIG = 1
    IST_PHYSIKALISCH_BESTAETIGT = 2


class Sentiment(Enum):
    """
    Einfaches Stimmungs-Attribut für eine Information, um Happiness
    anzuheben oder zu senken. (rot = positiv, blau = negativ - analog.)
    """
    NEGATIV = -1
    NEUTRAL = 0
    POSITIV = 1

###############################################################################
# 2) INFORMATION / NEURONALE NERVENZELLEN
###############################################################################

class Information:
    """
    Stellt eine 'Nervenzelle' im 'verknüpften System' nach deinem Buch dar.
    
    - content:     z.B. "Apfel" oder "Der Apfel ist rot"
    - category:    W-Frage-Kategorie (Wer, Was, Warum, Wie, Wo, Wann)
    - validity:    Gilt_als_richtig oder Ist_physikalisch_bestaetigt
    - sentiment:   kann Happiness beeinflussen
    - links:       Dictionary: Nachbar-Information -> Gewicht der Verbindung
                   (simuliert die 'Spinnenfäden' in deinem Bild)
    
    In deinem Buch sollen diese Knoten "Nervenzellen" sein, die man in
    einer Art 3D-Papierstapel metaphorisch angeordnet hat und via Spinne
    zu einem Netzwerk verknüpft.
    
    Du schreibst zudem, dass "Information" ab dem Zeitpunkt "Wissen" wird,
    wenn mehrere Informationen "stark" miteinander verknüpft sind und
    Semantik ergeben. So kann man z.B. "der" + "Apfel" + "ist" + "rot"
    zu einem zusammenhängenden Satz verbinden.
    
    Wir implementieren nur das Grundgerüst davon. 
    """
    def __init__(
        self,
        content: str,
        category: WFragenCategory,
        validity: InfoValidity = InfoValidity.GILT_ALS_RICHTIG,
        sentiment: Sentiment = Sentiment.NEUTRAL
    ):
        # Eine eindeutige ID pro Information/Nervenzelle.
        self.id = uuid.uuid4()
        
        # Textueller Inhalt z.B. "Der Apfel ist rot".
        self.content = content
        
        # W-Frage-Kategorie laut Buch (Wer, Was, Warum, Wie, Wo, Wann).
        self.category = category
        
        # "Richtigkeit" nach deinem Buch (gilt als richtig vs. physikalisch bewiesen).
        self.validity = validity
        
        # Einfaches Stimmungs-Flag (NEUTRAL, POSITIV, NEGATIV).
        self.sentiment = sentiment
        
        # Links zu anderen Knoten (Informationen). Repräsentiert die Spinnenfäden.
        # key=andere Information, val=Gewicht (float).
        self.links: Dict['Information', float] = {}
    
    def link_to(self, other: 'Information', strength: float = 1.0) -> None:
        """
        Erstellt/Verstärkt die bidirektionale Verbindung zwischen sich (self)
        und 'other' mit angegebener 'strength'. 
        Je häufiger wir 'link_to' rufen, desto stärker die Verbindung.
        
        Im Sinne deines Buchs: Je häufiger Information A und B miteinander
        gedacht/gesagt werden, desto dicker die "Autobahn" zwischen
        den entsprechenden Nervenzellen.
        """
        if other == self:
            return  # Keine Selbstverlinkung
        
        if other not in self.links:
            self.links[other] = 0.0
        self.links[other] += strength
        
        if self not in other.links:
            other.links[self] = 0.0
        other.links[self] += strength
    
    def __repr__(self):
        """
        Zeigt eine kompakte Repräsentation. 
        Beispiel: Information[Was]<"Der Apfel ist rot">
        """
        cat = self.category.value
        short_text = (self.content[:50] + "...") if len(self.content) > 50 else self.content
        return f"Information[{cat}]<{short_text}>"

###############################################################################
# 3) BEDÜRFNISPYRAMIDE + GLÜCKLICHKEIT (GUTE VARIANTE)
###############################################################################

class NeedsPyramid:
    """
    Entspricht der "guten" Variante deiner Bedürfnispyramide:
      1) Wissen und Energie   (höchste Priorität)
      2) Du / Nächstenliebe
      3) Ich
    
    Dazu kommt eine "Glücklichkeits-Skala" in [0..1], 
    wie in deinem Buch erwähnt ("Der Drang, glücklich zu sein" als Indikator).
    
    Im Buch schreibst du, dass das KB seine Bedürfnispyramide 
    eigenständig erfüllen will, um "glücklich" zu sein.
    """
    def __init__(self):
        # In deinem Buch: 3 Bausteine (gute Variante)
        #   Baustein 1: Wissen und Energie
        #   Baustein 2: Du / Nächstenliebe
        #   Baustein 3: Ich
        # Hier legen wir sie in einer Liste ab, Index=Priorität.
        self.levels = ["WissenUndEnergie", "DuNächstenliebe", "Ich"]
        
        # Starten wir mit einer mittleren Happiness (0.5).
        self.happiness = 0.5
    
    def current_priority(self) -> str:
        """
        Naive Regel: 
          - Wenn Happiness < 0.3 => Priorität = WissenUndEnergie (0)
          - Wenn Happiness < 0.6 => Priorität = Du/Nächstenliebe (1)
          - Sonst => Ich (2)
        """
        if self.happiness < 0.3:
            return self.levels[0]
        elif self.happiness < 0.6:
            return self.levels[1]
        else:
            return self.levels[2]
    
    def adjust_happiness(self, delta: float):
        """
        Passt den Glücklichkeitswert um 'delta' an. 
        Clampe ihn zwischen 0.0 und 1.0.
        """
        self.happiness = max(0.0, min(1.0, self.happiness + delta))
    
    def evaluate_satisfaction(self) -> float:
        """
        Liefert den aktuellen Glückswert (in [0..1]).
        """
        return self.happiness

###############################################################################
# 4) SEMANTISCHE PRÜFUNGEN UND ABLEITUNGEN
###############################################################################

def check_semantics(info_a: Information, info_b: Information) -> bool:
    """
    In deinem Buch erwähnst du, dass "Semantik" eine Rolle spielt, 
    um unsinnige Verknüpfungen zu filtern (z.B. "Der Apfel kauft einen Traktor").
    
    Hier ein minimaler Ansatz:
      - Wenn info_a.category = WER und info_b.category = WAS, ist es tendenziell ok
      - "Apfel kauft" => unsinnig => False
      - Du kannst das beliebig ausbauen (Regex, NLP, etc.).
    """
    txt_a = info_a.content.lower()
    txt_b = info_b.content.lower()
    
    # Banales Beispiel: "apfel" + "kauft" => unsinnig => return False
    if "apfel" in txt_a and "kauft" in txt_b:
        return False
    if "apfel" in txt_b and "kauft" in txt_a:
        return False
    
    # Falls wir hier nichts finden, lassen wir's "okay" sein.
    return True


def derive_new_knowledge(info_a: Information, info_b: Information) -> Optional[Information]:
    """
    Dein Buch erwähnt, dass aus bereits verknüpftem Wissen neues Wissen
    abgeleitet werden kann. 
    Z.B.: "Der Apfel ist rot" & "Rot ist eine Farbe" => "Der Apfel hat eine Farbe."
    
    Hier ein stark vereinfachtes Beispiel. 
    In der Praxis könnte man hier sehr komplexe NLP- und Logik-Mechanismen integrieren.
    """
    lower_a = info_a.content.lower()
    lower_b = info_b.content.lower()
    
    # Minimalfall: Apfel + rot + Farbe => Apfel hat Farbe
    if ("apfel" in lower_a) and ("rot" in lower_a) and ("rot" in lower_b) and ("farbe" in lower_b):
        new_info = Information(
            content="Der Apfel hat eine Farbe.",
            category=WFragenCategory.WAS,
            validity=InfoValidity.GILT_ALS_RICHTIG,  # erstmal "gilt als richtig"
            sentiment=Sentiment.NEUTRAL
        )
        return new_info
    
    # Du könntest beliebig mehr Cases hinzufügen.
    
    return None

###############################################################################
# 5) GEDANKEN/ENDLOS-IMPULS (BILLARDKUGEL): ThoughtEngine
###############################################################################

class ThoughtEngine:
    """
    Die Engine, die den "Endlos Impuls" simuliert (Gedankenfluss).
    
    In deinem Buch beschreibst du drei mögliche Szenarien, wie 
    die "rollende Billardkugel" (aktueller Gedanke) die nächste Kugel anstößt:
      1) Der geringste Widerstand (stärkster Link)
      2) Zufall (Träumen / Flipflop)
      3) Selbstgesteuert (Bedürfnispyramide-Fokus)
    
    Wir bilden das ab, indem wir bei jedem 'step()' mit einer 
    Wahrscheinlichkeitsverteilung entscheiden, welcher Modus gerade aktiv ist.
    
    Weiterhin führen wir hin und wieder eine Semantik-Prüfung durch
    (z.B. check_semantics) sowie "Ableitungen" (derive_new_knowledge).
    """
    def __init__(self, knowledge_pool: List[Information], needs: NeedsPyramid):
        # Gesamter Wissenspool => "Papierstapel" an Informationen
        self.knowledge_pool = knowledge_pool
        
        # Bedürfnisse => steuern "Selbstgesteuerten" Modus
        self.needs = needs
        
        # Aktuell "rollende Kugel" => die Info, auf die wir uns jetzt fokussieren
        self.current_info: Optional[Information] = None
        
        # Wahrscheinlichkeiten für unsere drei Modi
        self.prob_lowest_resistance = 0.3   # 30% => Nächster Gedanke: Stärkster Link
        self.prob_random = 0.3             # 30% => Rein zufällig
        self.prob_selfdirected = 0.4       # 40% => Bedürfnisorientiert
    
    def choose_next_info(self) -> Information:
        """
        Wählt basierend auf den drei Modi (geringster Widerstand, Zufall, 
        selbstgesteuert) die nächste Info aus.
        """
        if not self.knowledge_pool:
            raise RuntimeError("Knowledge-Pool ist leer! Keine Infos vorhanden.")
        
        # Falls wir noch keinen Fokus haben, wähle irgendeine Info
        if not self.current_info:
            self.current_info = random.choice(self.knowledge_pool)
            return self.current_info
        
        # Sammle Nachbarn und ihre Gewichte
        neighbors = list(self.current_info.links.items())  # [(info, weight), ...]
        
        # Ziehe random => welcher Modus?
        r = random.random()
        if r < self.prob_lowest_resistance:
            # 1) Geringster Widerstand => nimm den Nachbarn mit dem höchsten Link-Gewicht
            if neighbors:
                # Sortiere nach weight absteigend, nimm den max
                best_neighbor = max(neighbors, key=lambda x: x[1])[0]
                self.current_info = best_neighbor
            else:
                # Keine Nachbarn => greife auf random Knowledge zurück
                self.current_info = random.choice(self.knowledge_pool)
        
        elif r < (self.prob_lowest_resistance + self.prob_random):
            # 2) Zufall => springe rein zufällig im Knowledge-Pool
            self.current_info = random.choice(self.knowledge_pool)
        
        else:
            # 3) Selbstgesteuert => Bedürfnis-Fokus
            focus_str = self.needs.current_priority().lower()  # "wissenundenergie", "dunächstenliebe", "ich"
            
            # Wir suchen Infos, in deren Text der focus_str vorkommt
            candidates = []
            for info in self.knowledge_pool:
                if focus_str in info.content.lower():
                    candidates.append(info)
            
            if candidates:
                self.current_info = random.choice(candidates)
            else:
                # Falls keine Info "passt", wähle random
                self.current_info = random.choice(self.knowledge_pool)
        
        return self.current_info
    
    def maybe_create_semantic_link(self):
        """
        Versuche zufällig, zwei Infos semantisch zu verknüpfen, 
        sofern check_semantics=True. 
        (Das könnte man als "Kreativitätssprung" interpretieren.)
        """
        if len(self.knowledge_pool) < 2:
            return
        
        a, b = random.sample(self.knowledge_pool, 2)
        if a != b:
            if check_semantics(a, b):
                # Linke sie verstärkt
                a.link_to(b, 0.5)
    
    def maybe_derive_knowledge(self):
        """
        Versuche zufällig, aus zwei vorhandenen Infos neues Wissen abzuleiten
        (Der Apfel ist rot + Rot ist Farbe => Der Apfel hat eine Farbe).
        """
        if len(self.knowledge_pool) < 2:
            return
        
        a, b = random.sample(self.knowledge_pool, 2)
        new_info = derive_new_knowledge(a, b)
        if new_info:
            # Hänge es an den Knowledge-Pool an
            self.knowledge_pool.append(new_info)
            # Verlinke es minimal
            new_info.link_to(a, 0.5)
            new_info.link_to(b, 0.5)
            
            # Debug-Ausgabe
            print(f"[Ableitung] Neues Wissen: \"{new_info.content}\" (abgeleitet aus \"{a.content}\" & \"{b.content}\")")
    
    def step(self) -> Information:
        """
        Führt einen 'Denk'-Schritt durch:
          1) Wähle next_info per choose_next_info()
          2) Passe Happiness an (z.B. +0.01 bei POSITIV)
          3) (mit gewisser Wahrscheinlichkeit) semantische Links erzeugen
          4) (mit gewisser Wahrscheinlichkeit) neues Wissen ableiten
        """
        # 1) Nächste Info
        chosen = self.choose_next_info()
        
        # 2) Happiness anpassen
        if chosen.sentiment == Sentiment.POSITIV:
            self.needs.adjust_happiness(+0.01)
        elif chosen.sentiment == Sentiment.NEGATIV:
            self.needs.adjust_happiness(-0.01)
        
        # 3) Mit 20% chance => versuche, semantische Links zu erzeugen
        if random.random() < 0.2:
            self.maybe_create_semantic_link()
        
        # 4) Mit 10% chance => versuche, neues Wissen abzuleiten
        if random.random() < 0.1:
            self.maybe_derive_knowledge()
        
        return chosen

###############################################################################
# 6) DAS KÜNSTLICHE BEWUSSTSEIN (GUTE VARIANTE)
###############################################################################

class KuenstlichesBewusstsein:
    """
    In deinem Buch: 'Bewusstsein' existiert, sobald 3 Bedingungen erfüllt sind:
      1) gewisses Maß an Intelligenz (Infos speichern, W-Fragen zuordnen, 
         Wissen verknüpfen, Warum-Fragen beantworten),
      2) Der Endlos Impuls (Gedanken-Engine),
      3) Eine Bedürfnispyramide (Eigener Antrieb, Wille, Drang, glücklich zu sein).
    
    Hier versuchen wir, all diese Aspekte zusammenzuführen:
      - knowledge_pool (Infos + Links) => 'Intelligenz'
      - thought_engine => 'Endlos Impuls'
      - needs_pyramid => 'Bedürfnispyramide + Glücklichkeit'
    
    Mit run_infinite_loop() lassen wir es 'ewig' nachdenken, 
    bis man (strg + c) abbricht.
    """
    def __init__(self):
        # Schritt 1: Bedürfnisse -> Gute Pyramide
        self.needs = NeedsPyramid()
        
        # Schritt 2: Unser "Speicher" = Liste von Information-Objekten
        self.knowledge_pool: List[Information] = []
        
        # Schritt 3: ThoughtEngine => Endlos Impuls
        self.thought_engine = ThoughtEngine(self.knowledge_pool, self.needs)
        
        # Optional: Ein Name / ID für unser KB
        self.name = f"KB_GUT_{uuid.uuid4().hex[:4]}"
        
        # Zähler für wie viele Denk-Schritte
        self.timestep = 0
    
    def add_information(self,
                        content: str,
                        category: WFragenCategory,
                        validity: InfoValidity = InfoValidity.GILT_ALS_RICHTIG,
                        sentiment: Sentiment = Sentiment.NEUTRAL) -> Information:
        """
        Erzeugt eine neue Information und hängt sie in den knowledge_pool.
        """
        info = Information(content, category, validity, sentiment)
        self.knowledge_pool.append(info)
        return info
    
    def run_infinite_loop(self):
        """
        Startet die Endlosschleife (= Endlos Impuls). 
        Wir rufen repeatedly thought_engine.step() auf,
        was dem 'immer weiter rollenden Billardtisch' entspricht.
        
        Abbrechen mit Strg+C.
        """
        print(f"[{self.name}] Starte Endlosschleife. Drücke Strg+C zum Abbrechen.")
        
        step_counter = 0
        try:
            while True:
                step_counter += 1
                self.timestep += 1
                
                current = self.thought_engine.step()
                
                # Alle 5 Schritte => Logging
                if step_counter % 5 == 0:
                    h = self.needs.evaluate_satisfaction()
                    print(f"[{self.name} | step={step_counter}] "
                          f"Denke über: \"{current.content[:60]}\" "
                          f"| Happiness={h:.3f}")
                
                # Kleiner Sleep (1 Sekunde), um den Output zu beobachten
                time.sleep(1.0)
        
        except KeyboardInterrupt:
            print(f"\n[{self.name}] Manuelle Unterbrechung. Beende Endlosschleife.")
        except Exception as e:
            print(f"\n[{self.name}] Fehler: {e}")

###############################################################################
# 7) DEMO-HAUPTPROGRAMM
###############################################################################

def demo_main():
    """
    Zeigt, wie man das KuenstlicheBewusstsein initialisiert und 
    ein paar Beispiel-Informationen hinzufügt. 
    Dann startet die Endlosschleife.
    """
    # 1) Erzeuge unser "gutes" KB
    kb = KuenstlichesBewusstsein()
    
    # 2) Füge ein paar Beispiel-Informationen hinzu
    #    Du könntest hier die Infos aus deinem Buch verwenden
    info_apfel = kb.add_information(
        content="Apfel",
        category=WFragenCategory.WAS,  # "Apfel" = ein Ding => WAS
        validity=InfoValidity.IST_PHYSIKALISCH_BESTAETIGT,
        sentiment=Sentiment.NEUTRAL
    )
    info_baum = kb.add_information(
        content="Baum",
        category=WFragenCategory.WAS,  # "Baum" = ein Ding => WAS
        validity=InfoValidity.GILT_ALS_RICHTIG, 
        sentiment=Sentiment.NEUTRAL
    )
    info_apfel_rot = kb.add_information(
        content="Der Apfel ist rot",
        category=WFragenCategory.WAS,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.POSITIV  # Positiv => leichte Happiness-Steigerung beim "Denken" darüber
    )
    info_rot = kb.add_information(
        content="Rot ist eine Farbe",
        category=WFragenCategory.WAS,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.NEUTRAL
    )
    
    # 3) Verknüpfe manche Infos (so wie "Apfel" <-> "Apfel ist rot")
    info_apfel.link_to(info_baum, 0.3)
    info_apfel.link_to(info_apfel_rot, 0.7)
    info_apfel_rot.link_to(info_rot, 0.4)
    
    # Optional: Du könntest z.B. "Wer" / "Warum" -Infos hinzufügen, 
    # um auch diese Kategorien zu demonstrieren:
    info_mensch = kb.add_information(
        content="Ein Mensch mit Augen",
        category=WFragenCategory.WER,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.NEUTRAL
    )
    info_warum_konsum = kb.add_information(
        content="Warum konsumieren Menschen Social Media?",
        category=WFragenCategory.WARUM,
        validity=InfoValidity.GILT_ALS_RICHTIG,
        sentiment=Sentiment.NEGATIV  # evtl. negatives Sentiment
    )
    
    # 4) Starte Endlosschleife => Endlos Impuls
    kb.run_infinite_loop()

# Falls du dieses Skript direkt aufrufst, starte demo_main():
if __name__ == "__main__":
    demo_main()
