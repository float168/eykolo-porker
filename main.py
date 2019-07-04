#!/usr/bin/env python3

import itertools
import functools

import card


def main():
    cardset = build_default_cardset()
    deck = card.Deck(cardset)

    user_cards = deck.draw(5)
    user_hand = Hand(user_cards)

    bot_cards = deck.draw(5)
    bot_hand = Hand(bot_cards)

    def colorize_card(card):
        s = str(card)
        if card.suit in [Suit.JOKER]:
            s = Color.blue(s)
        elif card.suit in [Suit.HEART, Suit.DIAMOND]:
            s = Color.red(s)
        return s

    def format_colored_hand(cards, hand, prefix):
        return prefix + " " + ", ".join(map(colorize_card, cards)) + \
               " ({})".format(hand)

    print(format_colored_hand(user_cards, user_hand, "Your hand:"))
    print(format_colored_hand(bot_cards, bot_hand, "Dealer hand:"))

    if user_hand == bot_hand:
        print("Draw")
    elif user_hand > bot_hand:
        print("You win!")
    else:
        print("You lose")

class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERSE   = '\033[07m'

    @classmethod
    def blue(cls, s):
        return cls.BLUE + s + cls.END

    @classmethod
    def red(cls, s):
        return cls.RED + s + cls.END

# スート
# ジョーカーも含める
class Suit(card.OrderedValueEnum):
    JOKER   = ('★', -1)
    SPADE   = ('♠', 1)
    HEART   = ('♥', 2)
    CLUB    = ('♣', 3)
    DIAMOND = ('♦', 4)

class Rank(card.OrderedValueEnum):
    JOKER = ('Joker',  -1)
    ACE   = ('A',  1)
    KING  = ('K',  2)
    QUEEN = ('Q',  3)
    JACK  = ('J',  4)
    TEN   = ('10', 5)
    NINE  = ('9',  6)
    EIGHT = ('8',  7)
    SEVEN = ('7',  8)
    SIX   = ('6',  9)
    FIVE  = ('5',  10)
    FOUR  = ('4',  11)
    THREE = ('3',  12)
    TWO   = ('2',  13)

# ジョーカーn枚を含めた52+n枚のカードセットを作成
def build_default_cardset(n_jokers=2):
    suits   = list(Suit)[1:]
    ranks = list(Rank)[1:]

    cardset = [card.Card(s, r) for s, r in itertools.product(suits, ranks)]
    cardset += [card.Card(Suit.JOKER, Rank.JOKER)] * n_jokers
    return cardset

@functools.total_ordering
class Hand:
    def __init__(self, cards):
        assert(len(cards) == 5)
        self.__cards = cards
        self.__judge()

    @property
    def score(self):
        return self.__score

    def __str__(self):
        return self.__name

    def __repr__(self):
        return "<Hand: name = {}>".format(self)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.score < other.score

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.score == other.score

    def __judge(self):
        self.__jokers = self.__cards.indexes(Suit.JOKER)

        self.__normal_count = len(self.__cards) - len(self.__jokers)

        # スートとランクのヒストグラム生成
        # ジョーカーは特別扱いするためにヒストグラムから除外
        def make_histogram(enums, excludes=[]):
            if len(enums) == 0:
                return {}

            enum_cls = enums[0].__class__
            hist = {item: 0 for item in enum_cls}
            for item in enums:
                hist[item] += 1
            for ex in excludes:
                hist.pop(ex)
            return hist

        self.__suit_hist = make_histogram(self.__cards.suits, excludes=[Suit.JOKER])
        self.__rank_hist = make_histogram(self.__cards.ranks, excludes=[Rank.JOKER])

        if self.__is_five_card():
            self.__name = 'Five of a Kind'
            self.__score = 10000
        elif self.__is_royal_flush():
            self.__name = 'Royal Flush'
            self.__score = 9000
        elif self.__is_straight_flush():
            self.__name = 'Straight Flush'
            self.__score = 8000
        elif self.__is_four_card():
            self.__name = 'Four of a Kind'
            self.__score = 7000
        elif self.__is_full_house():
            self.__name = 'Full House'
            self.__score = 6000
        elif self.__is_flush():
            self.__name = 'Flush'
            self.__score = 5000
        elif self.__is_straight():
            self.__name = 'Straight'
            self.__score = 4000
        elif self.__is_three_card():
            self.__name = 'Three of a Kind'
            self.__score = 3000
        elif self.__is_two_pair():
            self.__name = 'Two Pair'
            self.__score = 2000
        elif self.__is_one_pair():
            self.__name = 'One Pair'
            self.__score = 1000
        else:
            self.__name = 'High Card'
            self.__score = 0

    def __is_five_card(self):
        if self.__normal_count in self.__rank_hist.values():
            return True

        return False

    # ジョーカー4枚以上ならこれより下にならない

    def __is_royal_flush(self):
        royal_ranks = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]
        royal_count = sum([self.__rank_hist[rank] for rank in royal_ranks])

        if self.__normal_count in self.__suit_hist.values() and royal_count == self.__normal_count:
            return True

        return False

    def __is_straight_flush(self):
        if self.__normal_count in self.__suit_hist.values():
            return self.__is_straight()

        return False

    def __is_four_card(self):
        if self.__normal_count - 1 in self.__rank_hist.values():
            return True

        return False

    # ジョーカー3枚以上ならこれより下にならない

    def __is_full_house(self):
        # フルハウスの時、手札に存在するランクは2種類のみ
        # 逆に言えば手札に存在しないランクがN-2種類
        if list(self.__rank_hist.values()).count(0) == len(self.__rank_hist) - 2:
            return True

        return False

    def __is_flush(self):
        if self.__normal_count in self.__suit_hist.values():
            return True

        return False

    def __is_straight(self):

        if list(self.__rank_hist.values()).count(1) == self.__normal_count:
            start_ranks = list(Rank)[1:-4]
            stop_ranks  = list(Rank)[6:]

            seq_count = sum([self.__rank_hist[rank] for rank in start_ranks[:5]])
            if seq_count == self.__normal_count:
                return True

            for prev_rank, next_rank in zip(start_ranks, stop_ranks):
                seq_count -= self.__rank_hist[prev_rank]
                seq_count += self.__rank_hist[next_rank]
                if seq_count == self.__normal_count:
                    return True

        return False

    def __is_three_card(self):
        if self.__normal_count - 2 in self.__rank_hist.values():
            return True

        return False

    # ジョーカー2枚以上ならこれより下にならない

    def __is_two_pair(self):
        # ツーペアの時、手札に存在するランクは3種類のみ
        # 逆に言えば手札に存在しないランクがN-3種類
        if list(self.__rank_hist.values()).count(0) == len(self.__rank_hist) - 3:
            return True

        return False

    def __is_one_pair(self):
        # ワンペアの時、手札に存在するランクは4種類のみ
        # 逆に言えば手札に存在しないランクがN-4種類
        if list(self.__rank_hist.values()).count(0) == len(self.__rank_hist) - 4:
            return True

        return False

if __name__ == '__main__':
    main()

