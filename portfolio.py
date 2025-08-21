class OptionLeg:
    def __init__(self, option_type, strike, expiry, quantity):
        self.option_type = option_type
        self.strike = strike
        self.expiry = expiry
        self.quantity = quantity

class Portfolio:
    def __init__(self):
        self.legs = []
    def add_leg(self, leg):
        self.legs.append(leg)
    def remove_leg(self, idx):
        if 0 <= idx < len(self.legs):
            self.legs.pop(idx)
    def get_payoff(self, S):
        payoff = 0
        for leg in self.legs:
            if leg.option_type == 'Call':
                payoff += leg.quantity * max(S - leg.strike, 0)
            else:
                payoff += leg.quantity * max(leg.strike - S, 0)
        return payoff
    def payoff_diagram(self, S_range):
        return [self.get_payoff(S) for S in S_range]
