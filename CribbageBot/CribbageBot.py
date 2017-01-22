# This is a bot that will play cribbage with you (and probably lose)
# -*- coding: UTF-8 -*-
import sys
from random import shuffle, randint, sample
import itertools
import csv

class Deck:
    deck = []
    place_in_deck = 0
    def shuffle(self):
        shuffle(self.deck)

    def split(self):
        split_point = randint(self.place_in_deck, 42)
        return self.deck[split_point]

    def deal1(self):
        self.place_in_deck += 1  # 0 on first and so on
        return self.deck[self.place_in_deck - 1]

    def deal6(self):
        cards = []
        for i in range(6):
            cards.append(self.deal1())
        return cards

    def rest_of_deck(self, cards):
        rest = []
        #print len(self.deck)
        for c in self.deck:
            if c not in cards:
                rest.append(c)
        return rest

    def __init__(self):
        self.deck = []
        for suit in [u'h', u'd', u'c', u's']:
            for i, card in enumerate([u'A', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'J', u'Q', u'K']):
                self.deck.append(Card(card, suit, min(i+1, 10), i))

class Card:

    def __init__(self, value, suit, numeric_value, ord):
        self.value = value
        self.suit = suit
        self.numeric_value = numeric_value
        self.ord = ord

    def __str__(self):
        return unicode(self.value + self.suit)

class Hand:

    #def count_points(self):
    def smart_discard(self):
        if self.cards:
            best_hand = []
            score = 0
            for sub_hand in itertools.combinations(self.cards, 4):
                if score_hand_4(sub_hand) >= score:
                    best_hand = sub_hand
                    score = score_hand_4(sub_hand)
            #print "Best hand is: " + ", ".join([str(x) for x in sub_hand]) + " with score: " + str(score)
            discard = []
            for c in self.cards:
                if c not in best_hand:
                    discard.append(c)
            #print "Discarding: " + ", ".join([str(x) for x in discard])
            self.cards = list(best_hand)
            return self.cards

    def statistical_discard(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                options.append((sub_hand, card, score_hand_5(list(sub_hand), card), vals_only.count(card.numeric_value) / 46.0))
                #print "Turned: {0} scored: {1} percentage: {2:.2f}%".format(str(card), score_hand_5(list(sub_hand), card), (100 * vals_only.count(card.numeric_value) / 46.0))
        options.sort(key=lambda x: (x[2], x[1]), reverse=True)
        #print "Top"
        #for i in range(30):
        #    print "<" + ", ".join([str(x) for x in options[i][0]]) + ">\t{0}, {1}, {2:.2f}%".format(str(options[i][1]), options[i][2], 100*options[i][3])

        self.cards = list(options[0][0])
        return self.cards

    def statistical_discard_2(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                options.append((sub_hand, card, score_hand_5(list(sub_hand), card), vals_only.count(card.numeric_value) / 46.0))
                #print "Turned: {0} scored: {1} percentage: {2:.2f}%".format(str(card), score_hand_5(list(sub_hand), card), (100 * vals_only.count(card.numeric_value) / 46.0))
        options.sort(key=lambda x: (x[1], x[2]), reverse=True)
        #print "Top"
        #for i in range(30):
        #    print "<" + ", ".join([str(x) for x in options[i][0]]) + ">\t{0}, {1}, {2:.2f}%".format(str(options[i][1]), options[i][2], 100*options[i][3])

        self.cards = list(options[0][0])
        return self.cards

    def play(played_you, played_opp, count):
        remaining_cards = [x for x in self.cards if x not in played_you]
        best_points = 0
        best_card = None
        for c in remaining_cards:
            if count + c.value <= 31:
                if count + c.value == 15:
                    
                    return 2, c
                elif count + c.value == 21:
                    return 2, c





    def discard_random(self, kitty):
        l = sample(range(0, 6), 2)
        kitty.accept(self.cards[l[0]])
        kitty.accept(self.cards[l[1]])
        del self.cards[max(l)]
        del self.cards[min(l)]

    def discard(self, first, second, kitty):
        kitty.accept(self.cards[first])
        kitty.accept(self.cards[second])
        del self.cards[max(first, second)]
        del self.cards[min(first, second)]

    def sort(self):
        self.cards.sort(key=lambda x: x.ord)

    def accept(self, card):
        self.cards.append(card)

    def __init__(self):
        self.cards = []

    def __str__(self):
        return "(" + ', '.join(str(c) for c in self.cards) + ")"

def score_hand_5(cards, turned_up_card):
    return count_fifteen(cards + [turned_up_card,]) + count_pairs(cards + [turned_up_card,]) + count_run_5(cards + [turned_up_card,]) + count_nibs(cards, turned_up_card)

def score_hand_4(cards):
    return count_fifteen(list(cards)) + count_pairs(list(cards)) + count_run_4(list(cards))

def score_hand_5_v(cards, turned_up_card):
    sum = 0
    fifteen = count_fifteen(cards + [turned_up_card,])
    print "Fifteen for: " + str(fifteen)
    sum += fifteen

    pairs = count_pairs(cards + [turned_up_card,])
    print "Pairs for: " + str(pairs)
    sum += pairs

    run = count_run_5(cards + [turned_up_card,])
    print "Run for: " + str(run)
    sum += run
    
    nibs = count_nibs(cards, turned_up_card)
    print "Nibs for 1"
    sum += 1

    return sum

def count_nibs(cards, turned_up_card):
    for c in cards:
        if c.value == 'J' and c.suit == turned_up_card.suit:
            return 1
        else:
            return 0

def count_fifteen(cards):
    points = 0
    for i in range(2, len(cards)+1):
        for c in itertools.combinations(cards, i):
            tmp = 0
            for j in range(i):
                tmp += c[j].numeric_value
            if (tmp == 15):
                points += 2
    return points

def count_pairs(cards):
     points = 0
     for c in itertools.combinations(cards, 2):
         if c[0].ord == c[1].ord:
             points += 2
     return points

def count_run_simple(cards):
    cards.sort(key=lambda x: x.ord)
    first = cards[0]
    count = 1
    for i in range(1, len(cards) -1):
        if cards[i].ord + 1 != first.ord:
            break
        else:
            first = cards[i]
            count += 1
    if count > 2:
        return count
    else:
        return 0

def count_run_5(cards):
    cards.sort(key=lambda x: x.ord)
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-3 == cards[4].ord-4: # A 2 3 4 5
        return 5
    if cards[0].ord == cards[1].ord == cards[2].ord == cards[3].ord-1 == cards[4].ord-2:     # A A A 2 3
        return 9
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-1 == cards[3].ord-2 == cards[4].ord-2: # A 2 2 3 3
        return 9
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-2 == cards[4].ord-2: # A 2 3 3 3
        return 9
    if cards[0].ord == cards[1].ord == cards[2].ord -1 == cards[3].ord -1 == cards[4].ord-2: # A A 2 2 3
        return 12
    if cards[0].ord == cards[1].ord == cards[2].ord -1 == cards[3].ord -2 == cards[4].ord-2: # A A 2 3 3
        return 12
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-1 == cards[3].ord-2 == cards[4].ord-2: # A 2 2 3 3
        return 12
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-3: # A 2 3 4 x
        return 4
    if cards[1].ord == cards[2].ord-1 == cards[3].ord-2 == cards[4].ord-3: # x A 2 3 4
        return 4
    if cards[0].ord == cards[1].ord == cards[2].ord-1 == cards[3].ord-2:   # A A 2 3 x
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-1 == cards[3].ord-2: # A 2 2 3 x
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-2: # A 2 3 3 x
        return 6
    if cards[1].ord == cards[2].ord == cards[3].ord-1 == cards[4].ord-2:   # x A A 2 3
        return 6
    if cards[1].ord == cards[2].ord-1 == cards[3].ord-1 == cards[4].ord-2: # x A 2 2 3
        return 6
    if cards[1].ord == cards[2].ord-1 == cards[3].ord-2 == cards[4].ord-2: # x A 2 3 3
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2: # A 2 3 x x
        return 3
    if cards[1].ord == cards[2].ord-1 == cards[3].ord-2: # x A 2 3 x
        return 3
    if cards[2].ord == cards[3].ord-1 == cards[4].ord-2: # x x A 2 3
        return 3
    else:
        return 0

def count_run_4(cards):
    cards.sort(key=lambda x: x.ord)
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-3: # A 2 3 4
        return 4
    if cards[0].ord == cards[1].ord == cards[2].ord-1 == cards[3].ord-2:   # A A 2 3
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-1 == cards[3].ord-2: # A 2 2 3
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2 == cards[3].ord-2: # A 2 3 3
        return 6
    if cards[0].ord == cards[1].ord-1 == cards[2].ord-2: # A 2 3 x
        return 3
    if cards[1].ord == cards[2].ord-1 == cards[3].ord-2: # x A 2 3
        return 3
    else:
        return 0

def quick_deal(*args):
    h = Hand()
    for i in args:
        h.accept(Card(i, 's', i, i))

def redeal():
    my_hand = Hand()
    d = Deck()
    d.shuffle()
    for i in range(6):
        my_hand.accept(d.deal1())
    my_hand.sort()
    return my_hand

def deal_and_statistical_discard():
    d = Deck()
    d.shuffle()

    my_hand = Hand()
    other_hand = Hand()
    third_hand = Hand()

    my_hand.sort()
    
    for i in range(6):
        my_hand.accept(d.deal1())
        other_hand.accept(d.deal1())
        third_hand.accept(d.deal1())

    kitty = Hand()

    my_hand.statistical_discard(d.rest_of_deck(my_hand.cards))
    other_hand.statistical_discard_2(d.rest_of_deck(my_hand.cards))
    #other_hand.smart_discard()
    third_hand.discard_random(kitty)

    turn_card = d.split()

    my_hand_score = score_hand_5(my_hand.cards, turn_card)
    other_hand_score = score_hand_5(other_hand.cards, turn_card)
    return my_hand_score, other_hand_score, score_hand_5(third_hand.cards, turn_card)


def deal_and_smart_discard():
    d = Deck()
    d.shuffle()

    my_hand = Hand()
    other_hand = Hand()

    my_hand.sort()
    
    for i in range(6):
        my_hand.accept(d.deal1())
        other_hand.accept(d.deal1())

    
    kitty = Hand()

    my_hand.smart_discard()
    other_hand.discard_random(kitty)

    
    turn_card = d.split()

    my_hand_score = score_hand_5(my_hand.cards, turn_card)
    if (my_hand_score > 25):
        print "Score: " + str(my_hand_score) + " " + ", ".join([str(x) for x in my_hand.cards]) + " " + str(turn_card)
        score_hand_5_v(my_hand.cards, turn_card)
    return my_hand_score, score_hand_5(other_hand.cards, turn_card)

def deal_and_count():
    d = Deck()
    d.shuffle()

    my_hand = Hand()
    other_hand = Hand()

    my_hand.sort()

    for i in range(6):
        my_hand.accept(d.deal1())
        other_hand.accept(d.deal1())

    kitty = Hand()

    my_hand.discard_random(kitty)

    other_hand.discard_random(kitty)


    turn_card = d.split()

    #print "my score: " + str(score_hand_5(my_hand.cards+[turn_card,]))
    #print "other score: " + str(score_hand_5(other_hand.cards+[turn_card,]))
    #print "kitty score: " + str(score_hand_5(kitty.cards+[turn_card,]))
    my_score = score_hand_5(my_hand.cards, turn_card)
    #if my_score >= 10:
    #    print "Yay got a decent hand: " + str(my_score)
    #    print my_hand
    #    print turn_card
    return my_hand, turn_card

def compare_smart_and_dumb():
    with open("out.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(1000):
            if i % 10 == 0:
                print str(i/10.0) + "%"
            x, y = deal_and_smart_discard()
            writer.writerow([x, y])

def main():
    with open("out.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(100):
            if i % 1 == 0:
                print str(i/1.0) + "%"
            x, y, z = deal_and_statistical_discard()
            writer.writerow([x, y, z])
'''
def main():
    d = Deck()
    d.shuffle()

    my_hand = Hand()
    other_hand = Hand()

    my_hand.sort()
    
    for i in range(6):
        my_hand.accept(d.deal1())
        other_hand.accept(d.deal1())

    others = d.rest_of_deck(my_hand.cards)

    score = my_hand.statistical_discard(others)

    vals_only = [x.numeric_value for x in others]

    print "Base score: " + str(score)
    print "Hand: " + ", ".join([str(x) for x in my_hand.cards])

    
    print len(others)
'''

if __name__ == "__main__":
    
    print sys.stdout.encoding
    main()