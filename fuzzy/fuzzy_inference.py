from .fuzzy_logic import FuzzyPredicate
from .fuzzy_number import FuzzyMinWith, FuzzyProductWith, FuzzyMax
from matplotlib import pyplot

class FuzzySet(FuzzyPredicate):
    def __init__(self, domain: str, degree: str, member_function):
        self.domain = domain
        self.degree = degree
        self.member_function = member_function

    def __call__(self, *args, **values):
        return self.member_function(values[self.domain])

    def __str__(self):
        return f'{self.domain} is {self.degree}'

    def plot(self, interval=(0, 1), points=1000):
        a, b = interval
        step = (b - a)/points
        pyplot.figure()
        xs = [a + x * step for x in range(points + 1)]
        ys = [self.member_function(x) for x in xs]
        pyplot.xlabel(self.domain)
        pyplot.ylabel(self.degree)
        pyplot.axis([a, b, 0, 1])
        pyplot.plot(xs, ys)
        pyplot.show()

class LinguisticVariable:
    def __init__(self, name: str, **categories):
        self.name = name
        self.categories = categories

    def __getattr__(self, category: str):
        return FuzzySet(self.name, category, self.categories[category])

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f'<{self.name}>: ' + ', '.join(c for c in self.categories)

class FuzzyRule:
    def __init__(self, antecedent: FuzzyPredicate, *consequences):
        self.antecedent = antecedent
        self.consequences = consequences
    
    def __str__(self):
        return f'{self.antecedent} => ' + ', '.join(str(c) for c in self.consequences)

class FuzzySystem:
    def __init__(self, input: tuple, output: tuple):
        self.rules = []
        try:
            self.input_variables = list(input)
        except TypeError:
            self.input_variables = [input]

        try:
            self.output_variables = list(output)
        except TypeError:
            self.output_variables = [output]

        if not self.input_variables or not self.output_variables:
            raise ValueError(f'Input and output cant be empty')

    def add_rule(self, antecedent: FuzzyPredicate, *consequences):
        if not consequences:
            raise ValueError(f'You must declare at least one consequence')

        for c in consequences:
            if all(c.domain != var.name for var in self.output_variables):
                raise ValueError(f'Variable <{c.domain}> is not an output varaible')
        
        self.rules.append(FuzzyRule(antecedent, *consequences))

    def __imod__(self, other: tuple):
        try:
            antecedent, *consequences = other
        except ValueError:
            raise ValueError(f'The rule is not in the correct format')
        self.add_rule(antecedent, *consequences)
        return self

    def mamdani(self, *values):
        vector = {var.name: value for var, value in zip(self.input_variables, values)}
        agregation = {var.name: [] for var in self.output_variables}

        for rule in self.rules:
            v = rule.antecedent(**vector)
            for c in rule.consequences:
                agregation[c.domain].append(FuzzyMinWith(v, c.member_function))

        return [FuzzySet(var.name, "Mamdani", FuzzyMax(*agregation[var.name]))
            for var in self.output_variables]

    def larsen(self, *values):
        vector = {var.name: value for var, value in zip(self.input_variables, values)}
        agregation = {var.name: [] for var in self.output_variables}

        for rule in self.rules:
            v = rule.antecedent(**vector)
            for c in rule.consequences:
                agregation[c.domain].append(FuzzyProductWith(v, c.member_function))

        return [FuzzySet(var.name, "Larsen", FuzzyMax(*agregation[var.name]))
            for var in self.output_variables]

    def __str__(self):
        return f'Input:\n' + '\n'.join(f'  {var}' for var in self.input_variables) +\
            f'\nOutput:\n' + '\n'.join(f'  {var}' for var in self.output_variables) +\
            '\nRules:\n' + '\n'.join(f'  {rule}' for rule in self.rules)