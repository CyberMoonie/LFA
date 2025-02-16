import java.util.*;

class Grammar {     // Class representing the grammar
    Set<String> VN; // Non-terminal symbols
    Set<String> VT; // Terminal symbols
    Map<String, List<String>> productions; // Production rules

    public Grammar(Set<String> VN, Set<String> VT, Map<String, List<String>> productions) {
        this.VN = VN;
        this.VT = VT;
        this.productions = productions;
    }

    public List<String> generateStrings() {
        List<String> strings = new ArrayList<>();
        Random random = new Random();
        for (int i = 0; i < 3; i++) {     // Generate 5 valid strings from the language
            StringBuilder sb = new StringBuilder();
            generateRecursive("S", sb, random);
            strings.add(sb.toString());
        }
        return strings;
    }

    private void generateRecursive(String symbol, StringBuilder sb, Random random) {
        if (!VN.contains(symbol)) { // If terminal, append to result
            sb.append(symbol);
            return;
        }
        List<String> rules = productions.get(symbol);
        String selectedRule = rules.get(random.nextInt(rules.size())); // Select random rule
        for (char c : selectedRule.toCharArray()) {
            generateRecursive(String.valueOf(c), sb, random);
        }
    }

    // Convert the grammar to a finite automaton
    public FiniteAutomaton toFiniteAutomaton() {
        return new FiniteAutomaton(VN, VT, productions);
    }
}

class FiniteAutomaton {                        // Class representing the Finite Automaton
    Set<String> states;
    Set<String> alphabet;
    Map<String, List<String>> transitions;
    String startState = "S";
    Set<String> finalStates = Set.of("C");  // Final state is 'C' based on the grammar

    public FiniteAutomaton(Set<String> states, Set<String> alphabet, Map<String, List<String>> transitions) {
        this.states = states;
        this.alphabet = alphabet;
        this.transitions = transitions;
    }

    // Method to check if a string is accepted by the finite automaton
    public boolean isStringAccepted(String input) {
        return checkString(input, startState);
    }

    private boolean checkString(String input, String currentState) {
        if (input.isEmpty()) {
            return finalStates.contains(currentState);
        }
        char symbol = input.charAt(0);
        String remaining = input.substring(1);

        if (!transitions.containsKey(currentState)) return false;

        for (String rule : transitions.get(currentState)) {
            if (!rule.isEmpty() && rule.charAt(0) == symbol) {
                String nextState = rule.length() > 1 ? rule.substring(1) : "";
                if (checkString(remaining, nextState)) return true;
            }
        }
        return false;
    }
}

// Main class to run the program
public class GrammarAutomatonDemo {
    public static void main(String[] args) {
        // Define the grammar
        Set<String> VN = new HashSet<>(Arrays.asList("S", "A", "B", "C"));
        Set<String> VT = new HashSet<>(Arrays.asList("a", "b"));

        // Define production rules
        Map<String, List<String>> productions = new HashMap<>();
        productions.put("S", Arrays.asList("aA", "aB"));
        productions.put("A", Arrays.asList("bS"));
        productions.put("B", Arrays.asList("aC"));
        productions.put("C", Arrays.asList("a", "bS"));

        // Create Grammar object
        Grammar grammar = new Grammar(VN, VT, productions);

        // Generate 5 valid strings
        System.out.println("Generated Strings:");
        List<String> validStrings = grammar.generateStrings();
        validStrings.forEach(System.out::println);

        // Convert to finite automaton
        FiniteAutomaton automaton = grammar.toFiniteAutomaton();

        // Check if a string is accepted
        String testString = "aa"; // Example string S → aA | aB or A → bS or  B → aC or C → a | bS
        System.out.println("\nIs the string '" + testString + "' accepted? " + automaton.isStringAccepted(testString));
    }
}
