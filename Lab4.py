import random
import re


def generate_strings_from_regex(pattern, limit=5):
    steps = []

    def expand_exponentiation(match):
        """Expands (a|b)^n notation."""
        choices = match.group(1).split('|')
        count = int(match.group(2))
        selection = ''.join(random.choice(choices) for _ in range(count))
        steps.append(f"Expanding exponentiation {match.group(0)} -> {selection}")
        return selection

    def expand_repetitions(match):
        """Expands repetitions like a+ or a* up to the limit."""
        char = match.group(1)
        op = match.group(2)
        count = random.randint(1, limit) if op == '+' else random.randint(0, limit)
        result = char * count
        steps.append(f"Expanding repetition {match.group(0)} -> {result}")
        return result

    def expand_group(match):
        """
        Expands groups like (a|b|c)+ or (a|b|c)* by repeating random selections.
        """
        group_content = match.group(1)
        repetition = match.group(2)
        choices = group_content.split('|')
        count = random.randint(1, limit) if repetition == '+' else random.randint(0, limit)
        selection = ''.join(random.choice(choices) for _ in range(count))
        steps.append(f"Expanding group {match.group(0)} -> {selection}")
        return selection

    def expand_simple_group(match):
        """
        Expands simple groups like (a|b|c) with a single random choice.
        """
        choices = match.group(1).split('|')
        selection = random.choice(choices)
        steps.append(f"Selecting from group {match.group(0)} -> {selection}")
        return selection

    def expand_optional(match):
        """Expands optional elements like a?"""
        selection = match.group(1) if random.choice([True, False]) else ''
        steps.append(f"Expanding optional {match.group(0)} -> {selection}")
        return selection

    # Step-by-step expansion
    pattern = re.sub(r'\(([^)]+)\)\^([0-9]+)', expand_exponentiation, pattern)     # (a|b)^3
    pattern = re.sub(r'\(([^)]+)\)([+*])', expand_group, pattern)                  # (a|b)+ or (x|y|z)*
    pattern = re.sub(r'([a-zA-Z])([+*])', expand_repetitions, pattern)             # a+ or a*
    pattern = re.sub(r'\(([^)]+)\)', expand_simple_group, pattern)                 # (a|b|c)
    pattern = re.sub(r'([a-zA-Z])\?', expand_optional, pattern)                    # a?

    return pattern, steps


def generate_samples(regex_list, num_samples=5):
    """Generates multiple samples for a list of regex patterns."""
    results = []
    for _ in range(num_samples):
        generated, steps = generate_strings_from_regex(regex_list[0])
        results.append((generated, steps))
    return results


# Given regex patterns
regex_patterns = [
    "O(P|Q|R)+2(3|4)",
    "A*B(C|D|E)F(G|H|I)^2",
    "J+K(L|M|N)*O?(P|Q)^3"
]

# Generate samples for each pattern
for regex in regex_patterns:
    print(f"Regex: {regex}")
    samples = generate_samples([regex], 5)
    for sample, steps in samples:
        print(f"Generated: {sample}")
        print("Processing Steps:")
        for step in steps:
            print(f"  - {step}")
        print()
