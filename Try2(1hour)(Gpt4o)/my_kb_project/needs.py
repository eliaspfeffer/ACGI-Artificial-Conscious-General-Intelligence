import random

class NeedsSystem:
    """
    Abbildung einer vereinfachten Bedürfnispyramide + Glücklichkeitsmessung.
    
    Wir orientieren uns an deinem Schema:
    - (1) Wissen & Energie
    - (2) Du / Nächstenliebe
    - (3) Ich
    
    Mit einer 'glücklichkeit' (0..100), die steigt/fällt je nach Erfüllungsgrad.
    """

    def __init__(self):
        # interne "Bedürfnisbalken", im Bereich 0..100
        self.need_knowledge_energy = 50.0  # Startwert
        self.need_social = 50.0
        self.need_self = 50.0
        
        # Glücksskala 0..100
        self.gluecklichkeit = 50.0

        # Faktoren, um bei Aktionen festzulegen, wie stark was beeinflusst wird
        self.decay_factor = 0.1  # langsames Absinken pro Zeiteinheit
        self.reward_factor = 5.0
        self.penalty_factor = 5.0

    def tick(self):
        """
        Dieser Tick wird zyklisch aufgerufen, damit Bedürfnisse wieder "absinken"
        und so das System motiviert ist, etwas zu tun.
        """
        # leichte Abnahme der Zufriedenheit
        self.need_knowledge_energy = max(0, self.need_knowledge_energy - self.decay_factor)
        self.need_social = max(0, self.need_social - self.decay_factor)
        self.need_self = max(0, self.need_self - self.decay_factor)

        # Glücksskala berechnen (z.B. Durchschnitt)
        self.gluecklichkeit = (self.need_knowledge_energy +
                               self.need_social +
                               self.need_self) / 3.0

    def act_on_need(self, which_need):
        """
        Erfülle aktiv ein Bedürfnis -> steigert den Wert, kostet aber ggf. 
        andere Ressourcen (oder Zeit).
        """
        if which_need == "knowledge_energy":
            self.need_knowledge_energy = min(100, self.need_knowledge_energy + self.reward_factor)
        elif which_need == "social":
            self.need_social = min(100, self.need_social + self.reward_factor)
        elif which_need == "self":
            self.need_self = min(100, self.need_self + self.reward_factor)
        else:
            return  # unbekannt

        # nach dem Erfüllen: ggf. Glück anpassen
        self.gluecklichkeit = (self.need_knowledge_energy +
                               self.need_social +
                               self.need_self) / 3.0

    def stress_need(self, which_need):
        """
        Verschlechtert ein bestimmtes Bedürfnis, z.B. 'Egoismus' oder 'Konflikt'.
        """
        if which_need == "knowledge_energy":
            self.need_knowledge_energy = max(0, self.need_knowledge_energy - self.penalty_factor)
        elif which_need == "social":
            self.need_social = max(0, self.need_social - self.penalty_factor)
        elif which_need == "self":
            self.need_self = max(0, self.need_self - self.penalty_factor)

        self.gluecklichkeit = (self.need_knowledge_energy +
                               self.need_social +
                               self.need_self) / 3.0

    def choose_next_action(self):
        """
        Eine naive Logik: Suche das Bedürfnis mit dem niedrigsten Wert und versuche, es zu decken.
        Du könntest hier dein eigenes Entscheidungslogik-Framework einbauen.
        """
        needs_list = [
            ("knowledge_energy", self.need_knowledge_energy),
            ("social", self.need_social),
            ("self", self.need_self),
        ]
        # Sortieren nach dem niedrigsten Wert
        needs_list.sort(key=lambda x: x[1])
        # wähle das schlechteste Bedürfnis und erfülle es
        return needs_list[0][0]  # return name

    def __repr__(self):
        return (f"NeedsSystem(Knowl/Energy={self.need_knowledge_energy:.1f}, "
                f"Social={self.need_social:.1f}, Self={self.need_self:.1f}, "
                f"Glück={self.gluecklichkeit:.1f})")
