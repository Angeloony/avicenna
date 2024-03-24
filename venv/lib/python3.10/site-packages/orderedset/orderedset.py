import itertools
from collections.abc import Set, Iterator, Iterable
from typing import TypeVar, Generic, Optional, Any, Dict, Union

from frozendict import frozendict

T = TypeVar("T")
S = TypeVar("S")


class OrderedSet(Set[T], Generic[T]):
    def __init__(self, base: Optional[Union[Dict[T, None], Iterable[T]]] = None):
        self.the_dict: Dict[T, None]
        if not base:
            self.the_dict = {}
        elif isinstance(base, dict):
            self.the_dict = base
        else:
            self.the_dict = dict.fromkeys(base)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (OrderedSet, list)):
            return len(self) == len(other) and list(self) == list(other)
        elif isinstance(other, Set):
            return set(self) == set(other)
        return NotImplemented

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __str__(self) -> str:
        return "{" + ", ".join(list(map(str, self.the_dict))) + "}"

    def __repr__(self) -> str:
        return f"OrderedSet({repr(self.the_dict)})"

    def __getitem__(self, item: int | slice) -> T | 'OrderedSet[T]':
        """
        Returns the indexed item or subset.

        Example:

        >>> s = OrderedSet([1, 2, 3, 4, 5])

        We can access individual elements of the list, starting from index 0.

        >>> s[1]
        2

        Negative indices work, too, just as for Python lists.

        >>> s[-2]
        4

        If we access an item with a too high index, we receive and error.

        >>> s[5]
        Traceback (most recent call last):
        ...
        IndexError: list index out of range

        Slices work, too:

        >>> s[1:3]
        OrderedSet({2: None, 3: None})

        Their semantics is the same as for ordinary lists.

        >>> list(s)[1:3] == list(s[1:3])
        True

        High indices are fine:

        >>> s[1:700]
        OrderedSet({2: None, 3: None, 4: None, 5: None})

        However, negative indices are not allowed (this is different for lists!):

        >>> s[-1:700]
        Traceback (most recent call last):
        ...
        ValueError: Indices for islice() must be None or an integer: 0 <= x <= sys.maxsize.

        :param item: An item index or a slice defining what item(s) to return.
        :return: The indexed item or subset.
        """
        assert isinstance(item, int) or isinstance(item, slice)
        if isinstance(item, int):
            if item < 0:
                item = len(self) + item

            if item < 0 or item >= len(self):
                raise IndexError("list index out of range")

            idx = 0
            for elem in iter(self):
                if idx == item:
                    return elem

                idx += 1

            assert False
        else:
            start = item.start or 0
            stop = item.stop or len(self)
            step = item.step or 1

            return OrderedSet(itertools.islice(iter(self), start, stop, step))

    def add(self, element: T) -> None:
        self.the_dict = {**self.the_dict, **{element: None}}

    def clear(self) -> None:
        self.the_dict.clear()

    def copy(self) -> 'OrderedSet[T]':
        return OrderedSet(self.the_dict.copy())

    def difference(self, s: Iterable[Any]) -> 'OrderedSet[T]':
        return OrderedSet({e: None for e in self.the_dict if e not in s})

    def difference_update(self, s: Iterable[Any]) -> None:
        self.the_dict = {e: None for e in self.the_dict if e not in s}

    def discard(self, element: T) -> None:
        del self.the_dict[element]

    def intersection(self, s: Iterable[Any]) -> 'OrderedSet[T]':
        return OrderedSet({e: None for e in self.the_dict if e in s})

    def intersection_update(self, s: Iterable[Any]) -> None:
        self.the_dict = {e: None for e in self.the_dict if e in s}

    def isdisjoint(self, s: Iterable[Any]) -> bool:
        return self.the_dict.keys().isdisjoint(s)

    def issubset(self, s: Iterable[Any]) -> bool:
        return set(self).issubset(set(s))

    def issuperset(self, s: Iterable[Any]) -> bool:
        return set(self).issuperset(set(s))

    def pop(self) -> T:
        items = list(self.the_dict)
        result = items.pop()
        self.the_dict = dict.fromkeys(items)
        return result

    def remove(self, element: T) -> None:
        self.discard(element)

    def symmetric_difference(self, s: Iterable[T]) -> 'OrderedSet[T]':
        return OrderedSet(
            dict.fromkeys([e for e in self.the_dict if e not in s] +
                          [e for e in s if e not in self.the_dict]))

    def symmetric_difference_update(self, s: Iterable[T]) -> None:
        self.the_dict = self.symmetric_difference(s).the_dict

    def union(self, s: Iterable[T]) -> 'OrderedSet[T]':
        return OrderedSet({**self.the_dict, **dict.fromkeys(s)})

    def update(self, s: Iterable[T]) -> None:
        self.the_dict = self.union(s).the_dict

    def __len__(self) -> int:
        return len(self.the_dict)

    def __contains__(self, o: object) -> bool:
        return o in self.the_dict

    def __iter__(self) -> Iterator[T]:
        return iter(self.the_dict)

    def __and__(self, s: Set[T]) -> 'OrderedSet[T]':
        return self.intersection(s)

    def __iand__(self, s: Set[T]) -> 'OrderedSet[T]':
        result = self.intersection(s)
        self.the_dict = result.the_dict
        return result

    def __or__(self, s: Set[S]) -> 'OrderedSet[Union[T, S]]':
        return self.union(s)

    def __ior__(self, s: Set[S]) -> 'OrderedSet[Union[T, S]]':
        result = self.union(s)
        self.the_dict = result.the_dict
        return result

    def __sub__(self, s: Set[Optional[T]]) -> 'OrderedSet[T]':
        return self.difference(s)

    def __isub__(self, s: Set[Optional[T]]) -> 'OrderedSet[T]':
        result = self.difference(s)
        self.the_dict = result.the_dict
        return result

    def __xor__(self, s: Set[S]) -> 'OrderedSet[Union[T, S]]':
        return self.symmetric_difference(s)

    def __ixor__(self, s: Set[S]) -> 'OrderedSet[Union[T, S]]':
        result = self.symmetric_difference(s)
        self.the_dict = result.the_dict
        return result

    def __le__(self, s: Set[T]) -> bool:
        return self.issubset(s)

    def __lt__(self, s: Set[T]) -> bool:
        return self.issubset(s) and len(self) < len(s)

    def __ge__(self, s: Set[T]) -> bool:
        return set(self) >= set(s)

    def __gt__(self, s: Set[T]) -> bool:
        return set(self) > set(s)


class FrozenOrderedSet(OrderedSet[T]):
    def __init__(self, base: Union[Dict[T, None], Iterable[T]]):
        super().__init__()
        self.the_dict: frozendict[T, None]
        if not base:
            self.the_dict = frozendict({})
        elif isinstance(base, frozendict):
            self.the_dict = base
        else:
            self.the_dict = frozendict.fromkeys(base)

    def __hash__(self):
        return 17 * hash(self.the_dict)

    def __repr__(self) -> str:
        return f"FrozenOrderedSet({repr(self.the_dict)})"

    def add(self, element: T) -> None:
        raise NotImplementedError('Cannot add to FrozenOrderedSet')

    def clear(self) -> None:
        raise NotImplementedError('Cannot clear FrozenOrderedSet')

    def copy(self) -> 'FrozenOrderedSet[T]':
        return FrozenOrderedSet(self.the_dict)

    def difference(self, s: Iterable[Any]) -> 'FrozenOrderedSet[T]':
        return FrozenOrderedSet(frozendict({e: None for e in self.the_dict if e not in s}))

    def difference_update(self, s: Iterable[Any]) -> None:
        self.the_dict = frozendict(
            {e: None for e in self.the_dict if e not in s})

    def discard(self, element: T) -> None:
        raise NotImplementedError('Cannot discard from FrozenOrderedSet')

    def intersection(self, s: Iterable[Any]) -> 'FrozenOrderedSet[T]':
        return FrozenOrderedSet(frozendict({e: None for e in self.the_dict if e in s}))

    def intersection_update(self, s: Iterable[Any]) -> None:
        self.the_dict = FrozenOrderedSet(frozendict(
            {e: None for e in self.the_dict if e in s}))

    def pop(self) -> T:
        raise NotImplementedError('Cannot pop from FrozenOrderedSet')

    def remove(self, element: T) -> None:
        raise NotImplementedError('Cannot remove from FrozenOrderedSet')

    def symmetric_difference(self, s: Iterable[T]) -> 'FrozenOrderedSet[T]':
        return FrozenOrderedSet(
            frozendict.fromkeys([e for e in self.the_dict if e not in s] +
                                [e for e in s if e not in self.the_dict]))

    def symmetric_difference_update(self, s: Iterable[T]) -> None:
        raise NotImplementedError('Cannot update FrozenOrderedSet')

    def union(self, s: Iterable[T]) -> 'FrozenOrderedSet[T]':
        return FrozenOrderedSet(frozendict({**self.the_dict, **dict.fromkeys(s)}))

    def update(self, s: Iterable[T]) -> None:
        raise NotImplementedError('Cannot update FrozenOrderedSet')

    def __and__(self, s: Set[T]) -> 'FrozenOrderedSet[T]':
        return self.intersection(s)

    def __iand__(self, s: Set[T]) -> 'FrozenOrderedSet[T]':
        raise NotImplementedError('Cannot update FrozenOrderedSet')

    def __or__(self, s: Set[S]) -> 'FrozenOrderedSet[Union[T, S]]':
        return self.union(s)

    def __ior__(self, s: Set[S]) -> 'FrozenOrderedSet[Union[T, S]]':
        raise NotImplementedError('Cannot update FrozenOrderedSet')

    def __sub__(self, s: Set[Optional[T]]) -> 'FrozenOrderedSet[T]':
        return self.difference(s)

    def __isub__(self, s: Set[Optional[T]]) -> 'FrozenOrderedSet[T]':
        raise NotImplementedError('Cannot update FrozenOrderedSet')

    def __xor__(self, s: Set[S]) -> 'FrozenOrderedSet[Union[T, S]]':
        return self.symmetric_difference(s)

    def __ixor__(self, s: Set[S]) -> 'FrozenOrderedSet[Union[T, S]]':
        raise NotImplementedError('Cannot update FrozenOrderedSet')
