package source.main;
import java.util.*;

public class KnowledgeGraph {
    private static final List<String> ATTRIBUTE_KEYS = Arrays.asList("Wer", "Was", "Wie", "Wo", "Wann");
    private static final Map<String, Map<String, List<String>>> ramMemory = new HashMap<>();
    private static final Map<String, Double> truthValues = new HashMap<>();
    private static final Map<String, Tuple<String, String, Integer>> relations = new HashMap<>();
    private static final Map<String, Double> consistencies = new HashMap<>();
    private static final Map<String, Double> scores = new HashMap<>();

    static {
        ramMemory.put("K1", extractAttributesFromSentence("Der Apfel hat eine grüne Farbe"));
        ramMemory.put("K2", extractAttributesFromSentence("Ein Baum hat grüne Blätter"));
        ramMemory.put("K3", extractAttributesFromSentence("Chlorophyll verursacht grüne Farbe"));
        ramMemory.put("K4", extractAttributesFromSentence("Ein Baum ist im Apfel"));

        truthValues.put("K1", 1.0);
        truthValues.put("K2", 1.0);
        truthValues.put("K3", 0.5);
        truthValues.put("K4", 0.1);

        relations.put("R12", new Tuple<>("K1", "K2", 10));
        relations.put("R13", new Tuple<>("K1", "K3", 10));
        relations.put("R24", new Tuple<>("K2", "K4", 1));
    }

    private static Map<String, List<String>> extractAttributesFromSentence(String sentence) {
        String[] words = sentence.split(" ");
        Map<String, List<String>> attributes = new HashMap<>();
        for (String key : ATTRIBUTE_KEYS) {
            attributes.put(key, new ArrayList<>());
        }
        for (int i = 0; i < words.length && i < ATTRIBUTE_KEYS.size(); i++) {
            attributes.get(ATTRIBUTE_KEYS.get(i)).add(words[i]);
        }
        return attributes;
    }

    private static double jaccardIndex(Map<String, List<String>> attributes1, Map<String, List<String>> attributes2) {
        Set<String> set1 = new HashSet<>(), set2 = new HashSet<>();
        attributes1.values().forEach(set1::addAll);
        attributes2.values().forEach(set2::addAll);
        int intersection = (int) set1.stream().filter(set2::contains).count();
        int union = set1.size() + set2.size() - intersection;
        return union > 0 ? (double) intersection / union : 0;
    }

    private static void calculateScores() {
        int alpha = 50, beta = 5, gamma = 1, delta = 1, lambdaW = 5;
        for (Map.Entry<String, Tuple<String, String, Integer>> entry : relations.entrySet()) {
            String kn = entry.getValue().first, km = entry.getValue().second;
            int frequency = entry.getValue().third;
            double B_P = Math.min(truthValues.getOrDefault(kn, 0.0), truthValues.getOrDefault(km, 0.0));
            double Kons_P = consistencies.getOrDefault(kn + "," + km, 0.0);
            double Widerspruch = 1 - Kons_P;
            double score = (alpha * B_P) + (beta * frequency) + (gamma * Kons_P) + (delta * 1) - (lambdaW * Widerspruch);
            scores.put(entry.getKey(), score);
        }
    }

    public static void main(String[] args) {
        calculateScores();
        scores.forEach((key, value) -> System.out.println(key + ": " + value));
    }

    private static class Tuple<A, B, C> {
        public final A first;
        public final B second;
        public final C third;
        public Tuple(A first, B second, C third) {
            this.first = first;
            this.second = second;
            this.third = third;
        }
    }
}