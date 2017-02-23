"""
Copyright 2016 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import re
import sys
import math


class InvertedIndex:
    """ A simple inverted index, as explained in Lecture 1. """

    def __init__(self):
        """ Create an empty inverted index. """
        sys.setrecursionlimit(15000)
        self.inverted_lists = {}
        self.DL = {}
        self.AVDL = 0
        self.N = 0

    def read_from_file(self, file_name, k, b):
        """
        The method reads textfromthe file file_name and generates an
        inverted index, the variables k and b are for calculating the
        BM25 scores.
        >>> ii=InvertedIndex()
        >>> ii.read_from_file("example.txt",1.75,0.75)
        >>> sorted(ii.inverted_lists.items())
        [('docum', [[1, 0.0], [2, 0.0], [3, 0.0]]), \
('first', [[1, 1.885]]), ('second', [[2, 2.325]]), ('third', [[3, 2.521]])]
        """
        record_id = 0
        with open(file_name, encoding='utf8') as file:
            for line in file:
                record_id += 1
                self.DL[record_id] = 0
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 2:
                        self.DL[record_id] += 1
                        # If word seen first time, create inverted list.
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = []
                            self.inverted_lists[word].append([record_id, 1])
                        elif record_id != self.inverted_lists[word][len(
                                            self.inverted_lists[word]) - 1][0]:
                            self.inverted_lists[word].append([record_id, 1])
                        else:
                            self.inverted_lists[word][len(
                                        self.inverted_lists[word]) - 1][1] += 1
                self.AVDL += self.DL[record_id]
        self.AVDL /= record_id
        self.N = record_id
        self.BM25(k, b)

    def BM25(self, k, b):
        """
        The method calcuates the BM25 scores of the wordes
        in the inverted index.
        """
        for word in self.inverted_lists:
            df = len(self.inverted_lists[word])
            for element in self.inverted_lists[word]:
                tfS = element[1] * (k + 1) / (k * (
                    1 - b + b * self.DL[element[0]] / self.AVDL) + element[1])
                element[1] = round(tfS * math.log(self.N / df, 2), 3)

    def merge(self, list1, list2):
        """
        Given two lists the method returns the union of both lists,
        if a word is common the result score is the added score
        from both lists.
        >>> ii=InvertedIndex()
        >>> ii.merge([[2,0],[5,2],[7,7],[8,6]],[[4,1],[5,3],[6,3],[8,3],[9,8]])
        [[2, 0], [4, 1], [5, 5], [6, 3], [7, 7], [8, 9], [9, 8]]
        """
        i = 0
        j = 0
        intersected_list = []
        if len(list1) == 0:
            return list2
        while i < len(list1) and j < len(list2):
            if list1[i][0] == list2[j][0]:
                intersected_list.append([list1[i][0], list1[i][1] +
                                        list2[j][1]])
                i += 1
                j += 1
            elif list1[i] > list2[j]:
                intersected_list.append(list2[j])
                j += 1
            else:
                intersected_list.append(list1[i])
                i += 1
        if i < len(list1):
            intersected_list += list1[i:]
        if j < len(list2):
            intersected_list += list2[j:]
        return intersected_list

    def partialSort(self, l1, topk):
        """
        The method returns the highest topk values in the list l1
        >>> ii = InvertedIndex()
        >>> List = [[3, 5], [2, 2], [1, 7], [11, 9]]
        >>> ii.partialSort(List, 3)
        [[11, 9], [1, 7], [3, 5]]
        """
        if len(l1) < 2:
            return l1
        else:
            pivot = l1[int(len(l1) / 2)]
            left = []
            right = []
            i = 0
            while i < len(l1):
                if l1[i][1] >= pivot[1] and i != int(len(l1) / 2):
                    left.append(l1[i])
                elif l1[i][1] < pivot[1]:
                    right.append(l1[i])
                i += 1
            if len(left) >= topk:
                return self.partialSort(left, topk)
            elif len(left) == topk - 1:
                return self.partialSort(left, topk - 1) + [pivot]
            else:
                return self.partialSort(
                    left, len(left)) + [pivot] + self.partialSort(
                                        right, topk - len(left) - 1)

    def process_query(self, words_list, topk):
        """
        Returns the indices matching the query words_list
        >>> ii=InvertedIndex()
        >>> ii.read_from_file("example.txt", 1.75, 0.75)
        >>> ii.process_query(["docum", "third"], 3)
        [[3, 2.521], [1, 0.0], [2, 0.0]]
        """
        intersected_list = []
        i = 0
        while i < len(words_list):
            if words_list[i] in self.inverted_lists:
                intersected_list = self.merge(intersected_list,
                                              self.inverted_lists[
                                                words_list[i]])
            i += 1
        return self.partialSort(intersected_list, topk)


class EvaluateBenchmark:
    """ Class for evaluating a given benchmark """

    def __init__(self, inverted_index):
        """ Create a EvaluateBenchmark with inverted_index. """
        self.inverted_index = inverted_index

    def precision_at_k(self, result_ids, relevant_ids, k):
        """
        Given result_ids and relevant_ids returns the precisionat k
        >>> inverted_index = InvertedIndex()
        >>> EB = EvaluateBenchmark(inverted_index)
        >>> EB.precision_at_k([0, 1, 2, 5, 6], [0, 2, 5, 6, 7, 8], 4)
        0.75
        """
        result_k = result_ids[:k]
        precision = len(set(relevant_ids) & set(result_k)) / k
        return precision

    def average_precision(self, result_ids, relevant_ids):
        """
        Given result_ids and relevant_ids returns the average precision
        >>> inverted_index = InvertedIndex()
        >>> EB = EvaluateBenchmark(inverted_index)
        >>> EB.average_precision([582,17,5666,10003,10],[10,582,877,10003])
        0.525
        """
        i = 0
        ap = 0
        intersection = 0
        while i < len(result_ids):
            j = 0
            while j < len(relevant_ids):
                if result_ids[i] == relevant_ids[j]:
                    ap += self.precision_at_k(result_ids, relevant_ids, i + 1)
                    intersection += 1
                j += 1
            i += 1
        return ap / len(relevant_ids)

    def evaluate_benchmark(self, file_name):
        """
        Given the name of the benchmark file the method
        calculates MP@3, MP@R and MAP
        """
        map = 0
        numberOfLines = 0
        numberOfRelevant = 0
        p3 = 0
        pr = 0
        with open(file_name, encoding='utf8') as file:
            for line in file:
                word = line.split("\t")
                query = re.split("\W+", word[0])
                relevant = [int(n) for n in word[1].split()]
                numberOfRelevant = len(relevant)
                result = self.inverted_index.process_query(
                                    query, numberOfRelevant)
                result = [row[0] for row in result]
                map += self.average_precision(result, relevant)
                p3 += self.precision_at_k(result, relevant, 3)
                pr += self.precision_at_k(result, relevant, numberOfRelevant)
                numberOfLines += 1
        return p3 / numberOfLines, pr / numberOfLines, map / numberOfLines

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
    k = 0.85
    b = 0.05
    ii.read_from_file(file_name, k, b)
    EB = EvaluateBenchmark(ii)
    print(EB.evaluate_benchmark('movies-benchmark.txt'))
