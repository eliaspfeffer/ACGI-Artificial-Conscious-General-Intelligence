"""
Ein rudimentäres Modul für Richtigkeits- und Semantik-Checks.
Du hast erwähnt, dass "Der Apfel kauft einen Traktor" unsinnig ist.
Hier könnte man Logikregeln / Ontologien / Physik-Prüfungen einbauen.
Aktuell sehr einfach gehalten.
"""

class SemanticChecker:
    def __init__(self):
        # Beispiel: Einfache "Typisierung" für manche Wörter
        self.known_types = {
            "Apfel": "Objekt",
            "Baum": "Objekt",
            "kauft": "Verb",
            "Traktor": "Objekt",
            "Hund": "Lebewesen",
            "Mensch": "Lebewesen",
            "liebt": "Verb",
        }
    
    def is_semantically_valid(self, words):
        """
        words: Liste von Strings z.B. ["Apfel", "kauft", "Traktor"]
        Wir prüfen einfach, ob ein "Objekt" ein "Verb" ausführt, 
        das laut Logik nur "Lebewesen" kann.
        
        Das ist SEHR vereinfacht, du könntest tausendfach erweitern.
        """
        # Extrem simpler Pattern-Check:
        # Falls Pattern: OBJ - VERB - OBJ => semantisch fraglich
        #                LEBE - VERB - OBJ => ok
        # (usw.)
        if len(words) != 3:
            return True  # wir prüfen nur 3er-Sätze als Demo
        
        subj_type = self.known_types.get(words[0], "Unbekannt")
        verb_type = self.known_types.get(words[1], "Unbekannt")
        obj_type  = self.known_types.get(words[2], "Unbekannt")
        
        if verb_type != "Verb":
            # Keine valide Satzstruktur -> unkritisch oder wir ignorieren's
            return True
        
        # Annahme: Nur Lebewesen dürfen "Verben" ausführen
        if subj_type == "Objekt" and verb_type == "Verb":
            # Apfel + kauft + Traktor => semantisch unsinnig
            return False

        # Demo: "Baum" gilt hier als Objekt -> "Baum liebt Hund" => semantisch unsinnig
        # "Mensch liebt Hund" => semantisch ok
        return True
