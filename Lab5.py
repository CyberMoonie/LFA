from typing import List, Set, Dict, Tuple
import itertools

Symbol = str
Production = List[Symbol]

class Grammar:
    def __init__(
        self,
        variables: Set[Symbol],
        terminals: Set[Symbol],
        start: Symbol,
        productions: Dict[Symbol, List[Production]]
    ):
        # V: nonterminals, T: terminals, S: start symbol
        self.V: Set[Symbol] = set(variables)
        self.T: Set[Symbol] = set(terminals)
        self.S: Symbol = start
        # P: mapping A -> list of productions (each production is list of symbols; empty list denotes ε)
        self.P: Dict[Symbol, List[Production]] = {
            A: [list(prod) for prod in prods]
            for A, prods in productions.items()
        }

    def eliminate_epsilon(self):
        # 1. Find nullable nonterminals
        nullable = {A for A, prods in self.P.items() if [] in prods}
        changed = True
        while changed:
            changed = False
            for A, prods in self.P.items():
                for prod in prods:
                    if all(sym in nullable for sym in prod) and A not in nullable:
                        nullable.add(A)
                        changed = True
        # 2. Remove ε and add all combinations omitting nullable symbols
        newP: Dict[Symbol, List[Production]] = {}
        for A, prods in self.P.items():
            new_prods: Set[Tuple[Symbol, ...]] = set()
            for prod in prods:
                if prod == []:
                    continue
                positions = [i for i, sym in enumerate(prod) if sym in nullable]
                for mask in range(1 << len(positions)):
                    tmp = prod.copy()
                    for i, pos in enumerate(positions):
                        if mask & (1 << i):
                            tmp[pos] = None
                    filtered = [s for s in tmp if s is not None]
                    if filtered:
                        new_prods.add(tuple(filtered))
                new_prods.add(tuple(prod))
            newP[A] = [list(p) for p in new_prods]
        if self.S in nullable:
            newP.setdefault(self.S, []).append([])
        self.P = newP

    def eliminate_unit(self):
        # Build unit relation
        unit = {(A, A) for A in self.V}
        for A, prods in self.P.items():
            for prod in prods:
                if len(prod) == 1 and prod[0] in self.V:
                    unit.add((A, prod[0]))
        changed = True
        while changed:
            changed = False
            for A, B in list(unit):
                for C, D in list(unit):
                    if B == C and (A, D) not in unit:
                        unit.add((A, D))
                        changed = True
        # Rebuild productions without unit steps
        newP: Dict[Symbol, List[Production]] = {A: [] for A in self.V}
        for A, B in unit:
            for prod in self.P.get(B, []):
                if not (len(prod) == 1 and prod[0] in self.V) and prod not in newP[A]:
                    newP[A].append(prod)
        self.P = newP

    def eliminate_inaccessible(self):
        reachable = {self.S}
        changed = True
        while changed:
            changed = False
            for A in list(reachable):
                for prod in self.P.get(A, []):
                    for sym in prod:
                        if sym in self.V and sym not in reachable:
                            reachable.add(sym)
                            changed = True
        self.V &= reachable
        self.P = {A: prods for A, prods in self.P.items() if A in reachable}

    def eliminate_nonproductive(self):
        productive = set()
        changed = True
        while changed:
            changed = False
            for A, prods in self.P.items():
                for prod in prods:
                    if all(sym in self.T or sym in productive for sym in prod):
                        if A not in productive:
                            productive.add(A)
                            changed = True
        good = self.V & productive
        self.V = good
        self.P = {
            A: [prod for prod in prods if all(sym in self.T or sym in good for sym in prod)]
            for A, prods in self.P.items() if A in good
        }

    def convert_to_cnf(self):
        # 1) replace terminals in long productions with new vars
        newP: Dict[Symbol, List[Production]] = {}
        term_map: Dict[Symbol, Symbol] = {}
        counter = itertools.count(1)
        def get_term_var(t: Symbol) -> Symbol:
            if t not in term_map:
                var = f"T_{t}_{next(counter)}"
                term_map[t] = var
                self.V.add(var)
                newP[var] = [[t]]
            return term_map[t]
        for A, prods in self.P.items():
            newP.setdefault(A, [])
            for prod in prods:
                if len(prod) <= 1:
                    newP[A].append(prod)
                else:
                    transformed = [get_term_var(sym) if sym in self.T else sym for sym in prod]
                    newP[A].append(transformed)
        # 2) binarize longer productions
        cnfP: Dict[Symbol, List[Production]] = {}
        counter2 = itertools.count(1)
        for A, prods in newP.items():
            cnfP.setdefault(A, [])
            for prod in prods:
                if len(prod) <= 2:
                    cnfP[A].append(prod)
                else:
                    symbols = prod
                    prev = symbols[0]
                    for sym in symbols[1:-1]:
                        nxt = f"X_{next(counter2)}"
                        self.V.add(nxt)
                        cnfP.setdefault(nxt, []).append([prev, sym])
                        prev = nxt
                    cnfP[A].append([prev, symbols[-1]])
        self.P = cnfP

    def print_grammar(self, title: str):
        print(f"=== {title} ===")
        for A in sorted(self.P):
            rhs = []
            for prod in self.P[A]:
                rhs.append("ε" if not prod else "".join(prod))
            print(f"{A} -> {' | '.join(rhs)}")
        print()

    def normalize_all(self):
        self.print_grammar("Original Grammar")
        self.eliminate_epsilon()
        self.print_grammar("After eliminating empty productions")
        self.eliminate_unit()
        self.print_grammar("After eliminating unit productions")
        self.eliminate_inaccessible()
        self.print_grammar("After eliminating inaccessible symbols")
        self.eliminate_nonproductive()
        self.print_grammar("After eliminating non-productive symbols")
        self.convert_to_cnf()
        self.print_grammar("Chomsky Normal Form")


if __name__ == '__main__':
    variables = {'S', 'A', 'B', 'C', 'D'}
    terminals = {'a', 'b'}
    start = 'S'
    productions = {
        'S': [['a','B'], ['A'], ['B']],
        'A': [['b'], ['a','D'], ['A','S'], ['b','A','B'], []],
        'B': [['a'], ['b','S']],
        'C': [['A','B']],
        'D': [['B','B']],
    }

    g = Grammar(variables, terminals, start, productions)
    g.normalize_all()
