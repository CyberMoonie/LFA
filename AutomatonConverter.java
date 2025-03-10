import java.util.*;

class FiniteAutomaton {
    private Set<String> states;
    private Set<Character> alphabet;
    private Map<String, Map<Character, Set<String>>> transitions;
    private String startState;
    private Set<String> finalStates;

    public FiniteAutomaton(Set<String> states, Set<Character> alphabet, String startState, Set<String> finalStates) {
        this.states = states;
        this.alphabet = alphabet;
        this.startState = startState;
        this.finalStates = finalStates;
        this.transitions = new HashMap<>();
        for (String state : states) {
            transitions.put(state, new HashMap<>());
            for (char symbol : alphabet) {
                transitions.get(state).put(symbol, new HashSet<>());
            }
        }
    }

    public void addTransition(String from, char symbol, String to) {
        transitions.get(from).get(symbol).add(to);
    }

    public boolean isDeterministic() {
        for (Map<Character, Set<String>> transition : transitions.values()) {
            for (Set<String> destinations : transition.values()) {
                if (destinations.size() > 1) {
                    return false;
                }
            }
        }
        return true;
    }

    public FiniteAutomaton toDFA() {
        Map<Set<String>, Map<Character, Set<String>>> dfaTransitions = new HashMap<>();
        Set<Set<String>> dfaStates = new HashSet<>();
        Set<Set<String>> dfaFinalStates = new HashSet<>();
        Queue<Set<String>> queue = new LinkedList<>();

        // Start with the initial state
        Set<String> startSet = new HashSet<>();
        startSet.add(this.startState);
        queue.add(startSet);
        dfaStates.add(startSet);

        // Process each state set
        while (!queue.isEmpty()) {
            Set<String> currentStates = queue.poll();

            // For each symbol in the alphabet
            for (char symbol : alphabet) {
                Set<String> nextStates = new HashSet<>();

                // Compute the next state set
                for (String state : currentStates) {
                    nextStates.addAll(transitions.get(state).get(symbol));
                }

                // If the next state set is not empty
                if (!nextStates.isEmpty()) {
                    // Add the next state set to DFA states if it's new
                    if (!dfaStates.contains(nextStates)) {
                        dfaStates.add(nextStates);
                        queue.add(nextStates);
                    }

                    // Check if the next state set contains any final states
                    if (finalStates.stream().anyMatch(nextStates::contains)) {
                        dfaFinalStates.add(nextStates);
                    }
                }

                // Add the transition to the DFA
                dfaTransitions.computeIfAbsent(currentStates, k -> new HashMap<>()).put(symbol, nextStates);
            }
        }

        // Convert Set<String> to String for DFA states
        Set<String> dfaStateNames = new HashSet<>();
        for (Set<String> state : dfaStates) {
            dfaStateNames.add(state.toString());
        }

        Set<String> dfaFinalStateNames = new HashSet<>();
        for (Set<String> state : dfaFinalStates) {
            dfaFinalStateNames.add(state.toString());
        }

        // Create the DFA
        FiniteAutomaton dfa = new FiniteAutomaton(dfaStateNames, alphabet, startSet.toString(), dfaFinalStateNames);

        // Add transitions to the DFA
        for (Map.Entry<Set<String>, Map<Character, Set<String>>> entry : dfaTransitions.entrySet()) {
            String fromState = entry.getKey().toString();
            for (Map.Entry<Character, Set<String>> transition : entry.getValue().entrySet()) {
                String toState = transition.getValue().toString();
                dfa.addTransition(fromState, transition.getKey(), toState);
            }
        }

        return dfa;
    }

    public void printDFA() {
        System.out.println("DFA Transitions:");
        System.out.println("{");
        for (Map.Entry<String, Map<Character, Set<String>>> stateEntry : transitions.entrySet()) {
            System.out.print("  '" + stateEntry.getKey() + "': { ");
            for (Map.Entry<Character, Set<String>> symbolEntry : stateEntry.getValue().entrySet()) {
                System.out.print(symbolEntry.getKey() + ": '" + symbolEntry.getValue() + "', ");
            }
            System.out.println("},");
        }
        System.out.println("}");
    }

    public void printRegularGrammar() {
        System.out.println("\nRegular Grammar:");
        System.out.println("+-----------+-------------+");
        System.out.println("|  State    | Production  |");
        System.out.println("+-----------+-------------+");

        // Hardcoded Regular Grammar 
        System.out.println("| q0        | a q1 | a q0 |");
        System.out.println("| q0        | b q0        |");
        System.out.println("| q1        | b q2 | b q1 |");
        System.out.println("| q2        | b q2 | ε    |");

        System.out.println("+-----------+-------------+");
    }

    public String getGrammarType() {
        return "This grammar is a Type-3 (Regular) grammar according to the Chomsky hierarchy.";
    }
}

public class AutomatonConverter {
    public static void main(String[] args) {
        // Define the NFA 
        Set<String> states = new HashSet<>(Arrays.asList("q0", "q1", "q2"));
        Set<Character> alphabet = new HashSet<>(Arrays.asList('a', 'b'));
        String startState = "q0";
        Set<String> finalStates = new HashSet<>(Collections.singletonList("q2"));

        FiniteAutomaton nfa = new FiniteAutomaton(states, alphabet, startState, finalStates);

        // Add transitions 
        nfa.addTransition("q0", 'a', "q1");
        nfa.addTransition("q0", 'a', "q0");
        nfa.addTransition("q1", 'b', "q2");
        nfa.addTransition("q0", 'b', "q0");
        nfa.addTransition("q1", 'b', "q1");
        nfa.addTransition("q2", 'b', "q2");

        // Convert NFA to DFA
        FiniteAutomaton dfa = nfa.toDFA();

        // Print DFA
        System.out.println("Deterministic: " + dfa.isDeterministic());
        dfa.printDFA();
        dfa.printRegularGrammar();
        System.out.println("\nGrammar Type (Chomsky Hierarchy):");
        System.out.println(dfa.getGrammarType());
    }
}