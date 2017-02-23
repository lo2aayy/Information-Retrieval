"""
Copyright 2016 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys


class InvertedIndex:
    """ A simple inverted index, as explained in Lecture 1. """

    def __init__(self):
        """ Create an empty inverted index. """

        self.inverted_lists = {}

    def read_from_file(self, file_name):
        """ Construct from given file (one record per line).

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example.txt")
        >>> sorted(ii.inverted_lists.items())
        [('doc', [1, 2, 3]), ('first', [1]), ('second', [2]), ('third', [3])]
        """

        record_id = 0
        with open(file_name) as file:
            for line in file:
                record_id += 1
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 0:
                        # If word seen first time, create inverted list.
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = []
                            self.inverted_lists[word].append(record_id)
                        elif record_id != self.inverted_lists[word][len(
                                            self.inverted_lists[word]) - 1]:
                            self.inverted_lists[word].append(record_id)

    def intersect(self, list1, list2):
        """ Returns the intersection of two lists
        >>> ii=InvertedIndex()
        >>> list1=[1,2,3]
        >>> list2=[1,2]
        >>> ii.intersect(list1,list2)
        [1, 2]
        """
        i = 0
        j = 0
        intersected_list = []
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                intersected_list.append(list1[i])
                i += 1
                j += 1
            elif list1[i] > list2[j]:
                j += 1
            else:
                i += 1
        return intersected_list

    def search(self, words_list):
        """ Returns the indices of matching query """

        if words_list[0] not in self.inverted_lists:
            return []
        intersected_list = self.inverted_lists[words_list[0]]
        i = 1
        while i < len(words_list):
            if words_list[i] not in self.inverted_lists:
                return []
            intersected_list = self.intersect(
                                intersected_list,
                                self.inverted_lists[words_list[i]])
            i += 1
        return intersected_list

if __name__ == "__main__":
    """ Output the lenghts of the inverted lists (= frequencies of the words) of
    the given file. """
    # Parse command line arguments.
    if len(sys.argv) != 2:
        print("Usage: python3 inverted_index.py <file>")
        sys.exit()
    file_name = sys.argv[1]
    # Output the lengths.
    ii = InvertedIndex()
    ii.read_from_file(file_name)
    file = open(file_name)
    lines = file.readlines()
    while True:
        query = input("Enter your query: ")
        keyWords = re.split("\W+", query)
        results = ii.search(keyWords)
        results = results[:3]
        if len(results) == 0:
            print("                     ", query, " not found in file")
        else:
            for i in results:
                print(lines[i - 1])
