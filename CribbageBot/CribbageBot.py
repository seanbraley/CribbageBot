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

    def deal1_s(self, card):
        for c in self.deck:
            if str(c.value + c.suit).lower() == str(card).lower():
                return c
            
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
        #print(len(self.deck)
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
    def play_1(self, sum, played_cards, total_played):
        best_card = None;
        best_points = 0
        remaining_cards = [x for x in self.cards if x not in total_played]
        if len(remaining_cards) == 0 or min([x.numeric_value for x in remaining_cards]) + sum > 31:
            return None, 0, sum # go
        else:
            # you have some card that you can play
            playable_cards = [x for x in remaining_cards if x.numeric_value + sum <= 31]
            # pick highest card not bringin future sum to [5, 10, 21, 30] IF POSSIBLE

            best_card = max(playable_cards, key=lambda x: x.numeric_value)

            # sort and find the first card that is lower (should be a better option) but 10 is better than 5
            count = 0
            if best_card.numeric_value + sum in [5, 10, 21]:
                playable_cards.sort(key=lambda x: x.ord)
                for i in range(1, len(playable_cards)):
                    if playable_cards[i].numeric_value != 5 and playable_cards[i].numeric_value < best_card.numeric_value:
                        count += 1
                        best_card = playable_cards[i]
                        break

            if len(played_cards) >= 1:
                for card in remaining_cards:
                    future_sum = sum + card.numeric_value
                    potential_points = 0
                    if (played_cards[-1].ord == card.ord): # pair
                        potential_points = 2
                        if len(played_cards) >= 2:
                            if (played_cards[-2].ord == card.ord): # double pair
                                potential_points = 6
                            elif count_run_simple(played_cards[-2:] + [card,]) == 3: # run
                                potential_points = 3
                                for i in range(3, len(played_cards)): # 3, 4, 5..
                                    if count_run_simple(played_cards[-i:] + [card,]) == i+1:
                                        potential_points += 1

                    if future_sum == 15: # could be a pair and 15/31 2+2/6or could just be 15/31 +2
                        potential_points += 2
                    elif future_sum == 31:
                        potential_points += 1

                    if potential_points > best_points:
                        best_card = card
                        best_points = potential_points

            return best_card, best_points, sum + best_card.numeric_value

    #def count_points(self):
    def smart_discard(self):
        if self.cards:
            best_hand = []
            score = 0
            for sub_hand in itertools.combinations(self.cards, 4):
                if score_hand_4(sub_hand) >= score:
                    best_hand = sub_hand
                    score = score_hand_4(sub_hand)
            #print("Best hand is: " + ", ".join([str(x) for x in sub_hand]) + " with score: " + str(score)
            discard = []
            for c in self.cards:
                if c not in best_hand:
                    discard.append(c)
            #print("Discarding: " + ", ".join([str(x) for x in discard])
            self.cards = list(best_hand)
            return self.cards

    def statistical_discard(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                options.append((sub_hand, card, score_hand_5(list(sub_hand), card), vals_only.count(card.numeric_value) / 46.0))
                #print("Turned: {0} scored: {1} percentage: {2:.2f}%".format(str(card), score_hand_5(list(sub_hand), card), (100 * vals_only.count(card.numeric_value) / 46.0))
        options.sort(key=lambda x: (x[3], x[2]), reverse=True)
        #print("Top"
        #for i in range(5):
        #    print("<" + ", ".join([str(x) for x in options[i][0]]) + ">\t{0}, {1}, {2:.2f}% {3}".format(str(options[i][1]), options[i][2], 100*options[i][3], score_hand_4(list(options[i][0])))

        self.cards = list(options[0][0])
        return self.cards

    def statistical_discard_2(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                options.append((sub_hand, card, score_hand_5(list(sub_hand), card), vals_only.count(card.numeric_value) / 46.0))
                #print("Turned: {0} scored: {1} percentage: {2:.2f}%".format(str(card), score_hand_5(list(sub_hand), card), (100 * vals_only.count(card.numeric_value) / 46.0))
        options.sort(key=lambda x: (x[2], x[3]), reverse=True)
        print("Top")
        for i in range(5):
            print("<" + ", ".join([str(x) for x in options[i][0]]) + ">\t{0}, {1}, {2:.2f}% {3}".format(str(options[i][1]), options[i][2], 100*options[i][3], score_hand_4(list(options[i][0]))))

        self.cards = list(options[0][0])
        return self.cards

    def statistical_discard_max_points(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        p = {}
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                score = score_hand_5(list(sub_hand), card)
                if p.has_key((sub_hand, score)):
                    p[(sub_hand, score)] += 1/46.0
                else:
                    p[(sub_hand, score)] = 1/46.0

        #print("Top by Points"
        new_options = [(x[0][0], x[0][1], x[1]) for x in p.items()]
        # new options is [sub_hand, points, percentage]
        new_options.sort(key=lambda x: (x[1], x[2]), reverse=True)
        #for i in range(10):
        #    print("<" + ", ".join([str(x) for x in new_options[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options[i][1]), 100*new_options[i][2])

        self.cards = list(new_options[0][0])
        return self.cards

    def statistical_discard_max_percentage(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        p = {}
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                score = score_hand_5(list(sub_hand), card)
                if p.has_key((sub_hand, score)):
                    p[(sub_hand, score)] += 1/46.0
                else:
                    p[(sub_hand, score)] = 1/46.0

        #print("Top by Percentage"
        new_options = [(x[0][0], x[0][1], x[1]) for x in p.items()]
        # new options is [sub_hand, points, percentage]
        new_options.sort(key=lambda x: (x[2], x[1]), reverse=True)
        #for i in range(10):
        #    print("<" + ", ".join([str(x) for x in new_options[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options[i][1]), 100*new_options[i][2])

        self.cards = list(new_options[0][0])
        return self.cards

    def statistical_discard_average(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        p = {}
        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                score = score_hand_5(list(sub_hand), card)
                if p.has_key(sub_hand):
                    p[sub_hand][0] += 1/46.0
                    p[sub_hand][1] += score
                    p[sub_hand][2] += 1.0
                else:
                    p[sub_hand] = [1/46.0, score, 1.0]

        #print("Top by Percentage"
        new_options = [(x[0], x[1][1]/x[1][2], x[1][0]) for x in p.items()]
        # new options is [sub_hand, points, percentage]
        new_options.sort(key=lambda x: (x[1], x[2]), reverse=True)
        #for i in range(min(len(new_options_2), 15)):
        #    print("<" + ", ".join([str(x) for x in new_options[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options[i][1]), 100*new_options[i][2])
        
        self.cards = list(new_options[0][0])
        return self.cards

    def statistical_discard_weighted_average(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        # 1/46 % for each to start
        # make an array of tuples
        # collapse tuples when hand == hand and points == points
        p = {}

        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                score = score_hand_5(list(sub_hand), card)
                if p.has_key((sub_hand, score)):
                    p[(sub_hand, score)] += 1/46.0
                else:
                    p[(sub_hand, score)] = 1/46.0
                q = {}

        for key in p.keys(): # key will be (sub_hand, score)
            if key[0] in q.keys(): # if we have hand already
                q[key[0]] += key[1]*p[key] # add the score multiplied by the percentage chance
            else:
                q[key[0]] = key[1]*p[key]

        # resulting dict is key[hand] = blended score
        opt = [(x[0], x[1]) for x in q.items()]
        #print("Top by blended average"
        opt.sort(key=lambda x: x[1], reverse=True)
        #for i in range(5):
        #    print("<" + ", ".join([str(x) for x in opt[i][0]]) + ">\t{0}".format(str(opt[i][1]))

        self.cards = list(opt[0][0])
        print("Expecting: ~{0:.2f}".format(opt[0][1]))
        return self.cards

    def statistical_discard_3(self, other_cards):
        vals_only = [x.numeric_value for x in other_cards]
        options = []
        # 1/46 % for each to start
        # make an array of tuples
        # collapse tuples when hand == hand and points == points
        p = {}

        for sub_hand in itertools.combinations(self.cards, 4):  
            for card in other_cards:
                score = score_hand_5(list(sub_hand), card)
                if p.has_key((sub_hand, score)):
                    p[(sub_hand, score)] += 1/46.0
                else:
                    p[(sub_hand, score)] = 1/46.0

                #options.append([sub_hand, card, score_hand_5(list(sub_hand), card), 1/46.0])
                #options.append((sub_hand, card, score_hand_5(list(sub_hand), card), vals_only.count(card.numeric_value) / 46.0))
                #print("Turned: {0} scored: {1} percentage: {2:.2f}%".format(str(card), score_hand_5(list(sub_hand), card), (100 * vals_only.count(card.numeric_value) / 46.0))

        q = {}
        for key in p.keys(): # key will be (sub_hand, score)
            if key[0] in q.keys(): # if we have hand already
                q[key[0]] += key[1]*p[key] # add the score multiplied by the percentage chance
            else:
                q[key[0]] = key[1]*p[key]

        # resulting dict is key[hand] = blended score
        opt = [(x[0], x[1]) for x in q.items()]
        print(len(q.items()))
        print("Top by blended average")
        opt.sort(key=lambda x: x[1], reverse=True)
        for i in range(5):
            print("<" + ", ".join([str(x) for x in opt[i][0]]) + ">\t{0}".format(str(opt[i][1])))
        # So now we know the top scoring hands possible
        # but different points are not combined. for instance:
        # <10d, Qs, Qh, Jh>	16, 15.22%
        # <10d, Qs, Qh, Jh>	15, 4.35%
        # <10d, Qs, Qh, Jh>	13, 6.52%
        # there is a 15% chance you will score 16 with this hand, but a 25% chance you will score 13-16

        new_options = [(x[0][0], x[0][1], x[1]) for x in p.items()]
        new_options_2 = [(x[0], x[1][1]/x[1][2], x[1][0]) for x in q.items()]
        # new options is [sub_hand, points, percentage]
        
        print("Top by average, total: " + str(len(new_options_2)))
        new_options_2.sort(key=lambda x: (x[1], x[2]), reverse=True)
        for i in range(min(len(new_options_2), 15)):
            print("<" + ", ".join([str(x) for x in new_options_2[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options_2[i][1]), 100*new_options_2[i][2]))
        
        print("Top by Points, total: " + str(len(new_options)))
        new_options.sort(key=lambda x: (x[1], x[2]), reverse=True)
        for i in range(10):
            print("<" + ", ".join([str(x) for x in new_options[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options[i][1]), 100*new_options[i][2]))
        
        print("Top by reality")
        new_options.sort(key=lambda x: (x[2], x[1]), reverse=True)
        for i in range(10):
            print("<" + ", ".join([str(x) for x in new_options[i][0]]) + ">\t{0}, {1:.2f}%".format(str(new_options[i][1]), 100*new_options[i][2]))

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
        self.remaining_cards = []

    def __str__(self):
        return "(" + ', '.join(str(c) for c in self.cards) + ")"

def score_hand_5(cards, turned_up_card):
    return count_fifteen(cards + [turned_up_card,]) + count_pairs(cards + [turned_up_card,]) + count_run_5(cards + [turned_up_card,]) + count_nibs(cards, turned_up_card)

def score_hand_4(cards):
    return count_fifteen(list(cards)) + count_pairs(list(cards)) + count_run_4(list(cards))

def score_hand_5_v(cards, turned_up_card):
    sum = 0
    fifteen = count_fifteen(cards + [turned_up_card,])
    print("Fifteen for: " + str(fifteen))
    sum += fifteen

    pairs = count_pairs(cards + [turned_up_card,])
    print("Pairs for: " + str(pairs))
    sum += pairs

    run = count_run_5(cards + [turned_up_card,])
    print("Run for: " + str(run))
    sum += run
    
    nibs = count_nibs(cards, turned_up_card)
    print("Nibs for " + str(nibs))
    sum += nibs

    return sum

def count_nibs(cards, turned_up_card):
    for c in cards:
        if c.value == 'J' and c.suit == turned_up_card.suit:
            return 1
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
    if len(cards) != 5:
        print(len(cards)
        print(", ".join([str(x) for x in cards])))
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

    kitty = Hand()
    
    # other_hand.statistical_discard_2(d.rest_of_deck(other_hand.cards))
    # other_hand.smart_discard()
    turn_card = d.split()

    cds = my_hand.cards
    my_hand.smart_discard()#d.rest_of_deck(my_hand.cards))
    my_hand_score = score_hand_5(my_hand.cards, turn_card)

    my_hand.cards = cds
    my_hand.statistical_discard_max_points(d.rest_of_deck(my_hand.cards))
    other_hand_score = score_hand_5(my_hand.cards, turn_card)

    my_hand.cards = cds
    my_hand.statistical_discard_weighted_average(d.rest_of_deck(my_hand.cards))

    return my_hand_score, other_hand_score, score_hand_5(my_hand.cards, turn_card)


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
        print("Score: " + str(my_hand_score) + " " + ", ".join([str(x) for x in my_hand.cards]) + " " + str(turn_card))
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

    #print("my score: " + str(score_hand_5(my_hand.cards+[turn_card,]))
    #print("other score: " + str(score_hand_5(other_hand.cards+[turn_card,]))
    #print("kitty score: " + str(score_hand_5(kitty.cards+[turn_card,]))
    my_score = score_hand_5(my_hand.cards, turn_card)
    #if my_score >= 10:
    #    print("Yay got a decent hand: " + str(my_score)
    #    print(my_hand
    #    print(turn_card
    return my_hand, turn_card

def compare_smart_and_dumb():
    with open("out.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(1000):
            if i % 10 == 0:
                print(str(i/10.0) + "%")
            x, y = deal_and_smart_discard()
            writer.writerow([x, y])

def play():
    while True:
        d = Deck()
        d.shuffle()
        h = Hand()
        x = raw_input("enter cards comma seperated: ")
        if x == 'q':
            break
        cards = x.split(",")
        for c in cards:
            h.accept(d.deal1_s(c))
        print("Hand: <" + ", ".join([str(x) for x in h.cards]) + ">")
        h.statistical_discard_weighted_average(d.rest_of_deck(h.cards))
        print("Keep: <" + ", ".join([str(x) for x in h.cards]) + ">")

        x = raw_input("Enter turned card: ")
        turn_card = d.deal1_s(x)
        print("Hand score: " + str(score_hand_5_v(h.cards, turn_card)))

def main():
    x, y, z = deal_and_statistical_discard()
    
    with open("out.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(1000):
            if i % 10 == 0:
                print(str(i/10.0) + "%")
            x, y, z = deal_and_statistical_discard()
            writer.writerow([x, y, z])
    
def play_round(im_on_first, p1_score, p2_score):
    # computers battle it out
    d = Deck()
    d.shuffle()
    
    my_hand = Hand()
    other_hand = Hand()
    kitty = Hand()
    
    if im_on_first:
        for i in range(6):
            my_hand.accept(d.deal1())
            other_hand.accept(d.deal1())

        before = my_hand.cards
        my_hand.statistical_discard_average(d.rest_of_deck(my_hand.cards))
        for card in before:
            if card not in my_hand.cards:
                kitty.accept(card)
            
        before = other_hand.cards
        other_hand.statistical_discard_average(d.rest_of_deck(other_hand.cards))
        for card in before:
            if card not in other_hand.cards:
                kitty.accept(card)

        # p1 deals first so 'other hand' is p1
        other_score, my_score = play_hands(other_hand, my_hand)

        turn_card = d.split()

        hand_score = score_hand_5(other_hand.cards, turn_card)
        print("Other hand: " + str(hand_score))
        other_score += hand_score
        print("other player pegs: " + str(other_score))

        hand_score = score_hand_5(my_hand.cards, turn_card)
        print("my hand: " + str(hand_score))
        my_score += hand_score

        hand_score = score_hand_5(kitty.cards, turn_card)
        print("kitty score: " + str(hand_score))
        my_score += hand_score
        print("your player pegs: " + str(my_score))
    else:
        for i in range(6):
            other_hand.accept(d.deal1())
            my_hand.accept(d.deal1())

        before = other_hand.cards
        other_hand.statistical_discard_average(d.rest_of_deck(other_hand.cards))
        for card in before:
            if card not in other_hand.cards:
                kitty.accept(card)
            
        before = my_hand.cards
        my_hand.statistical_discard_average(d.rest_of_deck(my_hand.cards))
        for card in before:
            if card not in my_hand.cards:
                kitty.accept(card)

        # p1 deals first so 'other hand' is p1
        my_score, other_score = play_hands(my_hand, other_hand)

        turn_card = d.split()

        hand_score = score_hand_5(my_hand.cards, turn_card)
        print("Other hand: " + str(hand_score))
        my_score += hand_score
        print("other player pegs: " + str(my_score))

        hand_score = score_hand_5(other_hand.cards, turn_card)
        print("my hand: " + str(hand_score))
        other_score += hand_score

        hand_score = score_hand_5(kitty.cards, turn_card)
        print("kitty score: " + str(hand_score))
        other_score += hand_score
        print("your player pegs: " + str(other_score))
    return my_score + p1_score, other_score + p2_score

def play_against_human(my_hand, human_p1=False):
    sum = 0
    played_cards = []
    total_played = []
    goed_1 = 0
    goed_2 = 0
    p1_score = 0
    p2_score = 0
    last_to_play = 2
    p2_leads = False
    d = Deck()
    if human_p1:
        other_hand = my_hand
    while (len(total_played) < 8):
        if not p2_leads:
            if human_p1:
                x = raw_input("enter card,points,sum: ")
                if x:
                    data = x.split(",")
                    card = d.deal1_s(data[0])
                    points, sum = data[1], data[2]
                else:
                    card, points, sum =  None, 0, sum
            else:
                card, points, sum = my_hand.play_1(sum, played_cards, total_played)
            if points == 0 and card is None:
                print("p1 Go") # other player gets a point
                goed_1 = 1
                played_cards = []
            else:
                last_to_play = 1
                p1_score += points
                total_played.append(card)
                played_cards.append(card)
                print("p1 played: " + str(card) + " " + str(sum) + " for " + str(points) + " (" + str(p1_score) + ")")
        else:
            print("P2 leading")
        p2_leads = False
        
        if not human_p1:
            x = raw_input("enter for p2 {card,points}: ")
            if x:
                data = x.split(",")
                card = d.deal1_s(data[0])
                points = int(data[1])
                sum += card.numeric_value
            else:
                card, points, sum =  None, 0, sum
        else:
            card, points, sum = other_hand.play_1(sum, played_cards, total_played)
        if points == 0 and card is None:
            print("p2 Go") # other player gets a point
            goed_2 = 1
            played_cards = []
        else:
            last_to_play = 2
            p2_score += points
            total_played.append(card)
            played_cards.append(card)
            print("p2 played: " + str(card) + " " + str(sum) + " for " + str(points) + " (" + str(p2_score) + ")")

        if goed_1 + goed_2 == 2:
            goed_1 = 0
            goed_2 = 0
            sum = 0
            played_cards = []
            if last_to_play == 1:
                p2_leads = True
                p1_score += 1
                print("p1 gets the point" + " (" + str(p1_score) + ")")
            else:
                p2_score += 1
                print("p2 gets the point" + " (" + str(p2_score) + ")")

    if last_to_play == 1:
        p1_score += 1
        print("p1 gets the point for last card" + " (" + str(p1_score) + ")")
    else:
        p2_score += 1
        print("p2 gets the point for last card" + " (" + str(p2_score) + ")")

    print("p1 got: " + str(p1_score))
    print("p2 got: " + str(p2_score))

def play_hands(my_hand=None, other_hand=None):
    d = Deck()
    d.shuffle()
    if my_hand is None:
        my_hand = Hand()
        my_hand.accept(d.deal1_s('10c'))
        my_hand.accept(d.deal1_s('10h'))
        my_hand.accept(d.deal1_s('ac'))
        my_hand.accept(d.deal1_s('ad'))

    if other_hand is None:
        other_hand = Hand() 
        other_hand.accept(d.deal1_s('7d'))
        other_hand.accept(d.deal1_s('8s'))
        other_hand.accept(d.deal1_s('4h'))
        other_hand.accept(d.deal1_s('4c'))
    


    #play_against_human(my_hand)
    

    sum = 0
    played_cards = []
    total_played = []
    goed_1 = 0
    goed_2 = 0
    p1_score = 0
    p2_score = 0
    last_to_play = 2
    p2_leads = False

    while (len(total_played) < 8):

        if not p2_leads:
            card, points, sum = my_hand.play_1(sum, played_cards, total_played)
            if points == 0 and card is None:
                print("p1 Go") # other player gets a point
                goed_1 = 1
                played_cards = []
            else:
                last_to_play = 1
                p1_score += points
                total_played.append(card)
                played_cards.append(card)
                print("p1 played: " + str(card) + " " + str(sum) + " for " + str(points) + " (" + str(p1_score) + ")")
        else:
            print("P2 leading")
        p2_leads = False

        card, points, sum = other_hand.play_1(sum, played_cards, total_played)
        if points == 0 and card is None:
            print("p2 Go") # other player gets a point
            goed_2 = 1
            played_cards = []
        else:
            last_to_play = 2
            p2_score += points
            total_played.append(card)
            played_cards.append(card)
            print("p2 played: " + str(card) + " " + str(sum) + " for " + str(points) + " (" + str(p2_score) + ")")

        if goed_1 + goed_2 == 2:
            goed_1 = 0
            goed_2 = 0
            sum = 0
            played_cards = []
            if last_to_play == 1:
                p2_leads = True
                p1_score += 1
                print("p1 gets the point" + " (" + str(p1_score) + ")")
            else:
                p2_score += 1
                print("p2 gets the point" + " (" + str(p2_score) + ")")

    if last_to_play == 1:
        p1_score += 1
        print("p1 gets the point for last card" + " (" + str(p1_score) + ")")
    else:
        p2_score += 1
        print("p2 gets the point for last card" + " (" + str(p2_score) + ")")

    print("I got: " + str(p1_score))
    print("other got: " + str(p2_score))

    return p1_score, p2_score
    #for i in range(6):
    #    my_hand.accept(d.deal1())
    #    other_hand.accept(d.deal1())

    


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

    print("Base score: " + str(score)
    print("Hand: " + ", ".join([str(x) for x in my_hand.cards])

    
    print(len(others)
'''

if __name__ == "__main__":
    #play()
    my_score = 0
    other_score = 0
    i = 2
    while my_score < 120 and other_score < 120:
        my_score, other_score = play_round(i % 2 == 0, my_score, other_score)
        print("SCORE: {0} | {1}".format(my_score, other_score))
        i += 1