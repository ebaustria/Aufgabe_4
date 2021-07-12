#!/usr/bin/env python
# coding: utf-8

from collections import Counter, defaultdict
import enum
from math import floor
from typing import Any, DefaultDict, Optional, Union, List, Dict
from tabulate import tabulate
import random


class Node:
    def __init__(self, key: int, value: Any):
        self.key = key
        self.value = value

    def __str__(self):
        return "(" + str(self.key) + ", " + str(self.value) + ")"


random.seed(27)  # do not change


class CuckooHashing:
    maxLoop = 50  # do not change

    def __init__(self, hash_table_size: int) -> None:
        self.hash_table_size = hash_table_size
        self.current_size = 0
        self.hash_table_1: List[Optional[Node]] = [None] * self.hash_table_size
        self.hash_table_2: List[Optional[Node]] = [None] * self.hash_table_size
        self.num_rebuilds: int = 0
        self.evictions: Dict = {}

        self.hash_func_params = [
            random.randint(2, self.hash_table_size) for _ in range(0, 4)
        ]

    # obviously do not change the hash functions
    def hash_func_1(self, key: int) -> int:
        return (
            (key % self.hash_func_params[0]) + (key % self.hash_func_params[1])
        ) % self.hash_table_size

    def hash_func_2(self, key: int) -> int:
        return (
            (key % self.hash_func_params[2]) - (key % self.hash_func_params[3])
        ) % self.hash_table_size

    def delete(self, key: int) -> bool:
        if self.retrieve_1(key) is not None:
            self.hash_table_1[self.hash_func_1(key)] = None
            return True

        if self.retrieve_2(key) is not None:
            self.hash_table_2[self.hash_func_2(key)] = None
            return True

        return False

    def insert(self, key: int, value: Any) -> bool:
        # we do not have to insert duplicates
        if self.retrieve(key) != None:
            return False

        for _ in range(self.maxLoop):
            if self.hash_table_1[self.hash_func_1(key)] == None:
                self.hash_table_1[self.hash_func_1(key)] = Node(key, value)
                return True

            # apparently another node is already in the nest
            # we evict it like a "cuckoo"
            tmp: Node = self.hash_table_1[self.hash_func_1(key)]
            self.hash_table_1[self.hash_func_1(key)] = Node(key, value)
            key = tmp.key
            value = tmp.value
            self.evictions[tmp.value] += 1

            if self.hash_table_2[self.hash_func_2(key)] == None:
                self.hash_table_2[self.hash_func_2(key)] = Node(key, value)
                return True

            # same as before for the other hash_table
            tmp: Node = self.hash_table_2[self.hash_func_2(key)]
            self.hash_table_2[self.hash_func_2(key)] = Node(key, value)
            key = tmp.key
            value = tmp.value
            self.evictions[tmp.value] += 1

        # if maxLoop iterations were reached -> try other hashfunctions
        self.rehash_tables()
        self.insert(key, value)
        return True

    def rehash_tables(self) -> None:
        self.num_rebuilds += 1

        # create new hash functions
        self.hash_func_params = [
            random.randint(2, self.hash_table_size) for i in range(0, 4)
        ]

        # collect already existing nodes
        nodes: List[Node] = []
        for i in range(0, self.hash_table_size):
            if self.hash_table_1[i] is not None:
                nodes.append(self.hash_table_1[i])

            if self.hash_table_2[i] is not None:
                nodes.append(self.hash_table_2[i])

        # use new (empty) hash_tables
        self.hash_table_1 = [None] * self.hash_table_size
        self.hash_table_2 = [None] * self.hash_table_size

        for node in nodes:
            self.insert(node.key, node.value)

    def retrieve_1(self, key: int) -> Union[None, Any]:
        h1 = self.hash_func_1(key)
        value_at_h1 = self.hash_table_1[h1]

        if value_at_h1 != None and value_at_h1.key == key:
            return value_at_h1.value
        return None

    def retrieve_2(self, key: int) -> Union[None, Any]:
        h2 = self.hash_func_2(key)
        value_at_h2 = self.hash_table_2[h2]

        if value_at_h2 != None and value_at_h2.key == key:
            return value_at_h2.value
        return None

    def retrieve(self, key: int) -> Union[None, Any]:
        h1 = self.hash_func_1(key)
        h2 = self.hash_func_2(key)

        # check both positions
        value_at_h1 = self.hash_table_1[h1]
        value_at_h2 = self.hash_table_2[h2]

        if value_at_h1 != None and value_at_h1.key == key:
            return value_at_h1.value
        elif value_at_h2 != None and value_at_h2.key == key:
            return value_at_h2.value
        else:
            return None

    def print_hash_tables(self) -> None:
        print(
            tabulate(
                [
                    ["Pos " + str(i) for i in range(0, self.hash_table_size)],
                    self.hash_table_1,
                    self.hash_table_2,
                ],
                headers="firstrow",
                tablefmt="grid",
            )
        )


language_cuckoo = CuckooHashing(16)

languages_list = [
    "Ada",
    "Basic",
    "C",
    "C#",
    "C++",
    "D",
    "Eiffel",
    "F#",
    "Erlang",
    "Fortran",
    "Go",
    "Haskell",
    "Java",
    "Javascript",
    "Kotlin",
    "Lisp",
    "MATLAB",
    "Pascal",
    "Perl",
    "PHP",
    "Prolog",
    "Python",
    "Ruby",
    "Scala",
    "Smalltalk",
    "SQL",
    "Swift",
    "TypeScript",
]

for key, lang in enumerate(languages_list):
    language_cuckoo.evictions[lang] = 0
    language_cuckoo.insert(key, lang)

language_cuckoo.print_hash_tables()

print("Number of rebuilds: ", language_cuckoo.num_rebuilds)
print("Evictions: ", language_cuckoo.evictions)

to_delete = [8, 21, 27]
for key in to_delete:
    language_cuckoo.delete(key)

language_cuckoo.print_hash_tables()

to_reinsert = [(8, "Erlang"), (27, "TypeScript"), (21, "Python")]
for key, lang in to_reinsert:
    language_cuckoo.insert(key, lang)

language_cuckoo.print_hash_tables()

"""
# # Codebeispiele für Aufgabe 4

# a)
for i, programming_language in enumerate(languages_list):
    assert language_cuckoo.retrieve(i) == programming_language

# b)
for i, node in enumerate(language_cuckoo.hash_table_1):
    if node is None:
        pass
    else:
        assert i == language_cuckoo.hash_func_1(node.key)

for i, node in enumerate(language_cuckoo.hash_table_2):
    if node is None:
        pass
    else:
        assert i == language_cuckoo.hash_func_2(node.key)

# c
values_hash_table_1 = [n.value for n in language_cuckoo.hash_table_1 if n is not None]
values_hash_table_2 = [n.value for n in language_cuckoo.hash_table_2 if n is not None]
for programming_language in languages_list:
    assert (
        programming_language in values_hash_table_1
        or programming_language in values_hash_table_2
    )

# d)
key_to_test = 0
value_to_test = "Ada"
hash_1 = language_cuckoo.hash_func_1(key_to_test)
hash_2 = language_cuckoo.hash_func_2(key_to_test)
assert (
    language_cuckoo.hash_table_1[hash_2].value == value_to_test
    or language_cuckoo.hash_table_2[hash_1].value == value_to_test
)
"""