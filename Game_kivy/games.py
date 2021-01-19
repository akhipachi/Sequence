from cards import Card, Deck
from client import Backend
from game import BaseGame
from pile import Foundation, Jocker, Tableau, Waste


class Sequence(BaseGame):
    name = "Sequence"
    decks = 1
    num_tableau = 13
    num_waste = 2
    num_jocker = 1
    num_cols = 7
    num_rows = 3
    tableau_pos = [(i if i < 7 else i - 6, 1 if i < 7 else 2) for i in range(13)]
    foundation_pos = [(3 + i, 0) for i in range(4)]
    tableau_depth = [1 for i in range(13)]

    # setup the initial game layout
    def build(self):
        for i in range(self.num_tableau):
            self.add_pile(Tableau(self, *self.tableau_pos[i], fan="down"))
        for i, s in enumerate(Deck.suits):
            self.add_pile(Foundation(self, *self.foundation_pos[i]))
        self.add_pile(Waste(self, 0, 0, on_touch=self.get, suit="e"))
        self.add_pile(Waste(self, 1, 0))
        self.add_pile(Jocker(self, 2, 0, suit="j"))

    def get(self):
        if self.turn and self.piles["waste"][1].size() == 1 and self.cards == 0:
            Backend.get_instance().write.put("get")
            self.cards += 1

    # deal initial cards to given pile
    def start(self, pile, deck):
        if pile.type == "tableau":
            for i in range(self.tableau_depth[pile.index]):
                pile.add_card(deck.next(True))

    # can we add num cards from group to pile?

    def can_add(self, src, pile, group, num):
        if src.type == "waste" and src.index == 0:
            return False
        if src.type == "jocker" or pile.type == "jocker":
            return False
        # add self.turn
        if pile.type == "waste":
            return pile.index == 1 and pile.size() == 0 and num == 1 and self.turn
        if src.type == "waste" and src.index == 1:
            return self.turn
        return True

    def add_to_pile(self, card, pile_type, index):
        pile = self.piles[pile_type][index]
        pile.add_card(Card(card.split(" ")[0], card.split(" ")[1], True))
