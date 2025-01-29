import itertools
import math

class KnowledgeGraph:
    def __init__(self):
        self.contexts = {}
        self.relations = {}

    def add_context(self, context_id, attributes, truth_score):
        self.contexts[context_id] = {
            "attributes": attributes,
            "truth_score": truth_score
        }

    def add_relation(self, context1, context2, frequency):
        self.relations[(context1, context2)] = {
            "frequency": frequency
        }

    def calculate_jaccard_index(self, context1, context2):
        attrs1 = set(self.contexts[context1]["attributes"])
        attrs2 = set(self.contexts[context2]["attributes"])
        intersection = len(attrs1 & attrs2)
        union = len(attrs1 | attrs2)
        return intersection / union if union > 0 else 0

    def evaluate_path(self, path, lambda_weight=5):
        # Calculate Bmin(P)
        b_min = min(self.contexts[ctx]["truth_score"] for ctx in path)

        # Calculate Bwiderspruch(P)
        consistency_scores = [
            self.calculate_jaccard_index(path[i], path[i + 1])
            for i in range(len(path) - 1)
        ]
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 1
        widerspruch = 1 - avg_consistency
        b_widerspruch = b_min - lambda_weight * widerspruch

        # Calculate Bmultiplikativ(P)
        b_multiplicative = math.prod(self.contexts[ctx]["truth_score"] for ctx in path)

        # Combine to get B(P)
        b_p = b_min * b_widerspruch * b_multiplicative
        return b_p

    def calculate_path_score(self, path):
        # Frequency of relations
        relation_scores = sum(
            self.relations.get((path[i], path[i + 1]), {}).get("frequency", 0)
            for i in range(len(path) - 1)
        )

        # Path length
        path_length = len(path)

        # Consistency
        consistency = sum(
            self.calculate_jaccard_index(path[i], path[i + 1])
            for i in range(len(path) - 1)
        ) / (len(path) - 1) if len(path) > 1 else 1

        # Truthfulness
        b_p = self.evaluate_path(path)

        # Score
        return b_p + relation_scores + path_length + consistency

    # def find_best_path(self, target_context):
    #     paths = []

    #     # Generate all possible paths up to a certain length
    #     for length in range(1, len(self.contexts) + 1):
    #         paths.extend(itertools.permutations(self.contexts.keys(), length))

    #     # Filter paths that end in the target context
    #     paths = [path for path in paths if path[-1] == target_context]

    #     # Calculate scores
    #     scored_paths = [(path, self.calculate_path_score(path)) for path in paths]

    #     # Return the best path
    #     return max(scored_paths, key=lambda x: x[1], default=(None, 0))

    def find_best_path(self, target_context):
        paths = []

        # Include single-context paths
        single_context_paths = [(ctx,) for ctx in self.contexts.keys()]
        paths.extend(single_context_paths)

        # Generate all possible paths up to a certain length
        for length in range(2, len(self.contexts) + 1):
            paths.extend(itertools.permutations(self.contexts.keys(), length))

        # Filter paths that end in the target context
        paths = [path for path in paths if path[-1] == target_context]

        # Calculate scores
        scored_paths = [(path, self.calculate_path_score(path)) for path in paths]

        # Return the best path
        return max(scored_paths, key=lambda x: x[1], default=(None, 0))

# Beispielimplementierung
kg = KnowledgeGraph()

# Kontexte hinzufügen
kg.add_context("K1", ["=Der", "Was=Apfel", "=ist", "Wie=grün"], 1.5)
kg.add_context("K2", ["=Ein", "Was=Baum", "=hat", "Wie=grün", "Was=Blätter"], 1.5)
kg.add_context("K3", ["Was=Chlorophyll", "Was=verursacht", "Wie=grün", "Was=Farbe"], 0.5)
kg.add_context("K4", ["=Ein", "Was=Baum", "=ist", "Wo=im", "Was=Apfel"], 0.5)

# Relationen hinzufügen
kg.add_relation("K1", "K3", 10)
kg.add_relation("K2", "K4", 1)

# Besten Pfad berechnen
best_path, best_score = kg.find_best_path("K3")
print("Best Path:", best_path)
print("Best Score:", best_score)
