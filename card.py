import random
import copy
import enum
import operator


# 値を(文字列,順序)の順で定義するためのEnum
class OrderedValueEnum(enum.Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] >= other.value[1]
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] > other.value[1]
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] <= other.value[1]
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] < other.value[1]
        return NotImplemented

    def __str__(self):
        return self.value[0]

# カード
class Card:
    def __init__(self, suit, rank, expr=None):
        assert(issubclass(suit.__class__, OrderedValueEnum))
        assert(issubclass(rank.__class__, OrderedValueEnum))
        self.__suit = suit
        self.__rank = rank
        self.__expr = expr

    @property
    def suit(self):
        return self.__suit

    @property
    def rank(self):
        return self.__rank

    def __repr__(self):
        return "<Card {}>".format(str(self))

    def __str__(self):
        if self.__expr is not None:
            return self.__expr
        else:
            return " ".join(map(lambda x: str(x), [self.__suit, self.__rank]))

# カードの束
# 手札用
class Cards:
    def __init__(self, card_list):
        cards = list(card_list)
        for card in card_list:
            assert(isinstance(card, Card))
        self.__cards = copy.copy(cards)
        self.__update_members()

    @property
    def cards(self):
        return copy.copy(self.__cards)

    @property
    def suits(self):
        return copy.copy(self.__suits)

    @property
    def ranks(self):
        return copy.copy(self.__ranks)

    def __str__(self):
        return str(self.__cards)

    def __len__(self):
        return len(self.__cards)

    def __iter__(self):
        return self.__cards.__iter__()

    def __contains__(self, item):
        return self.count(item) > 0

    def count(self, item):
        return len(self.indexes(item))

    def indexes(self, item):
        if len(self.__cards) == 0:
            return []

        def _indexes(item, lst):
            return [i for i, x in enumerate(lst) if x == item]

        cls = item.__class__
        first = self.__cards[0]
        if cls == first.__class__:
            return _indexes(item, self.__cards)
        if cls == first.suit.__class__:
            return _indexes(item, self.__suits)
        if cls == first.rank.__class__:
            return _indexes(item, self.__ranks)

    def add(self, cards):
        self.__cards += list(cards)
        self.__update_members()

    def delete(self, idxs):
        idxs = list(idxs).sort()
        cnt = 0
        for idx in idxs:
            self.__cards.pop(idx - cnt)
            cnt += 1
        self.__update_members()

    def replace(self, cards, idxs):
        cards = list(cards)
        idxs  = list(idxs)
        assert(len(cards) == len(idxs))

        for card, idx in zip(cards, idxs):
            self.__cards[idx] = card
        self.__update_members()

    def __update_members(self):
        self.__cards.sort(key=operator.attrgetter('suit'))
        self.__cards.sort(key=operator.attrgetter('rank'))

        self.__suits = list(map(lambda x: x.suit, self.__cards))
        self.__ranks = list(map(lambda x: x.rank, self.__cards))

# デッキ
class Deck:
    def __init__(self, cardset):
        self.__cardset  = cardset
        self.__decksize = len(cardset)
        self.rebuild()

    # デッキを再構築
    # 既存のカードは破棄
    def rebuild(self):
        self.__deck = self.__random_cardset()

    # デッキに新たなシャッフル済みカードセットを追加
    # デッキの末尾に追加
    def append_cardset(self):
        self.__deck += self.__random_cardset()

    # デッキをシャッフル
    def shuffle(self):
        random.shuffle(self.__deck)

    # デッキから指定された数だけカードを引く
    # デッキが尽きたら継ぎ足す
    def draw(self, count):
        if count > len(self.__deck):
            self.append_cardset()
        return Cards([self.__deck.pop(0) for _ in range(count)])

    # カードセットをシャッフルしたものを生成
    def __random_cardset(self):
        return random.sample(self.__cardset, self.__decksize)

    def __repr__(self):
        return "<Deck: remain = {}>".format(len(self.__deck))
