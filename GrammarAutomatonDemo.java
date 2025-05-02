import java.util.*;

class Grammar {
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
        for (int i = 0; i < 5; i++) { // Generate 5 valid strings
            StringBuilder sb = new StringBuilder();
            generateRecursive("S", sb, random); // Always start with "S"
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

    public FiniteAutomaton toFiniteAutomaton() {
        return new FiniteAutomaton(VN, VT, productions);
    }
}

class FiniteAutomaton {
    Set<String> states;
    Set<String> alphabet;
    Map<String, List<String>> transitions; // Transition rules
    String startState = "S"; // Start state
    Set<String> finalStates = Set.of("C"); // Final states

    public FiniteAutomaton(Set<String> states, Set<String> alphabet, Map<String, List<String>> transitions) {
        this.states = states;
        this.alphabet = alphabet;
        this.transitions = transitions;
    }

    // Check if a string is accepted by the automaton
    public boolean isStringAccepted(String input) {
        return checkString(input, startState);
    }

    private boolean checkString(String input, String currentState) {
        // If the input is empty, check if we're in a final state
        if (input.isEmpty()) {
            return finalStates.contains(currentState);
        }

        char symbol = input.charAt(0); // First character of input
        String remaining = input.substring(1); // Remaining input

        // If the current state has no transitions, return false
        if (!transitions.containsKey(currentState)) return false;

        // Check transitions from the current state
        for (String rule : transitions.get(currentState)) {
            // If the transition matches the current symbol, continue checking
            if (!rule.isEmpty() && rule.charAt(0) == symbol) {
                String nextState = rule.length() > 1 ? rule.substring(1) : currentState; // Get the next state
                if (checkString(remaining, nextState)) return true;
            }
        }
        return false; // No valid transition found
    }
}

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
        String testString = "aaa"; // Example string
        System.out.println("\nIs the string '" + testString + "' accepted? " + automaton.isStringAccepted(testString));
    }
}
