# -*- coding: utf-8 -*-

"""
Copyright 2016 University of Freiburg
Hannah Bast <bast@cs.uni-freiburg.de>
Björn Buchhold <buchhold@cs.uni-freiburg.de>
Patrick Brosi <brosi@informatik.uni-freiburg.de>
Co-Author: Louay Abdelgawad <lo2aayyguc@gmail.com>,
            Omar Kassem <omar.kassem67@gmail.com>
"""

import re
import sys
import math
import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix


class InvertedIndex:
    """ A simple inverted index, as explained in the lecture.
        >>> np.set_printoptions(formatter={"float": lambda x: ("%.3f" % x)})
    """

    def __init__(self):
        """ Create an empty inverted index. """

        self.inverted_lists = dict()
        self.document_lengths = []
        self.avg_doc_length = 0

        # term document matrix
        self.td_matrix = None
        # maps a term to the row index of the document matrix
        self.term_matrix_indices = dict()

    def read_from_file(self, file_name, bm25_k=1.75, bm25_b=0.75):
        """
        Construct inverted index from given file. The format is one record per
        line.

        Documents are unique in postings lists.

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example2.txt")
        >>> [(elem[0],"%.3f"% elem[1]) for elem in ii.inverted_lists['web']]
        [(1, '0.944'), (3, '1.135'), (4, '0.705')]
        >>> [(elem[0],"%.3f"% elem[1]) for elem in ii.inverted_lists['beach']]
        [(4, '0.705'), (5, '1.135'), (6, '1.135')]
        >>> [(elem[0],"%.3f"% elem[1]) \
        for elem in ii.inverted_lists['internet']]
        [(1, '0.944'), (2, '1.135'), (4, '0.705')]
        >>> [(elem[0],"%.3f"% elem[1]) \
        for elem in ii.inverted_lists['surfing']]
        [(1, '0.000'), (2, '0.000'), (3, '0.000'), (4, '0.000'), \
(5, '0.000'), (6, '0.000')]
        """
        with open(file_name) as file:
            doc_id = 0
            for line in file:
                doc_id += 1
                self.document_lengths.append(0)
                for word in re.split("\W+", line):
                    word = word.lower()
                    if len(word) > 0:
                        self.document_lengths[-1] += 1
                        self.avg_doc_length += 1
                        """ If word seen for first time, create empty inverted
                        list for it. """
                        if word not in self.inverted_lists:
                            self.inverted_lists[word] = list()

                        """
                        A doc_id collision can only occur if the last
                        entry in the word's postings lists is the current
                        doc_id (postings list is implicitely sorted by the
                        increasing doc_id). """
                        if (len(self.inverted_lists[word]) == 0 or
                                self.inverted_lists[word][-1][0] != doc_id):
                            """ First occurence of this document for this word,
                            set term frequency (tf) to 1 """
                            self.inverted_lists[word].append((doc_id, 1))
                        elif self.inverted_lists[word][-1][0] == doc_id:
                            """ Document already stored for this word,
                                increment tf by 1 """
                            self.inverted_lists[word][-1] = \
                                (doc_id, self.inverted_lists[word][-1][1] + 1)

        """ (N == doc_id) """
        self.avg_doc_length = self.avg_doc_length / doc_id

        self.transform_to_bm25(bm25_k, bm25_b)

    def preprocess_vsm(self, m):
        """
        Exercise 08.01
        Construct the sparse term-document matrix.

        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> ii.read_from_file("example2.txt", 1.75, 0.75)
        >>> ii.preprocess_vsm(4)
        >>> l = sorted(ii.td_matrix.todense().tolist())
        >>> print(np.round(l, 3))
        [[0.000 0.000 0.000 0.000 0.000 0.000]
         [0.000 0.000 0.000 0.705 1.135 1.135]
         [0.944 0.000 1.135 0.705 0.000 0.000]
         [0.944 1.135 0.000 0.705 0.000 0.000]]
        """
        # print(self.inverted_lists, " \n \n")
        # self.inverted_lists =
        # sortedList = sorted(self.inverted_lists)
        self.values = sorted(self.inverted_lists.values(),
                             key=len, reverse=True)[:m]
        self.keys = sorted(self.inverted_lists,
                           key=lambda k: len(self.inverted_lists[k]),
                           reverse=True)[:m]
        rows = []
        cols = []
        vals = []
        self.matrix_indices_terms = dict()
        for ind, j in enumerate(self.values):
            self.term_matrix_indices[self.keys[ind]] = ind
            self.matrix_indices_terms[ind] = self.keys[ind]
            for pair in j:
                # row i is the term's row
                rows.append(ind)
                # col docId is the documents column
                cols.append(pair[0] - 1)
                # the entries of the term-doc matrix are the BM25 scores
                vals.append(pair[1])
        # use float values because of BM25 scores
        self.td_matrix = csr_matrix((vals, (rows, cols)), dtype=float)

    def preprocess_lsi(self, k):
        """
        Calculate SVD of the Td matrix

        >>> ii = InvertedIndex()
        >>> ii.td_matrix = [[1.0, 1.0, 0.0, 1.0, 0.0, 0.0],\
[1.0, 0.0, 1.0, 1.0, 0.0, 0.0],\
[1.0, 1.0, 1.0, 2.0, 1.0, 1.0],\
[0.0 ,0.0 ,0.0 ,1.0 ,1.0 ,1.0]]
        >>> ii.preprocess_lsi(2)
        >>> print(ii.Uk)
        [[-0.470 0.367]
         [-0.470 0.367]
         [0.122 0.785]
         [0.737 0.338]]
        >>> print(ii.UkSk)
        [[-0.726 1.397]
         [-0.726 1.397]
         [0.189 2.985]
         [1.140 1.285]]
        >>> print(ii.Vk)
        [[-0.529 -0.225 -0.225 0.027 0.556 0.556]
         [0.400 0.303 0.303 0.695 0.295 0.295]]
        """
        self.Uk, self.Sk, self.Vk = scipy.sparse.linalg.svds(self.td_matrix, k)
        self.UkSk = self.Uk * self.Sk

    def process_query_vsm(self, keywords):
        """
        Exercise 08.01
        Process query using VSM.

        >>> ii = InvertedIndex() # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        >>> ii.inverted_lists = {"bla": [(1, 0.2), (3, 0.6)],
        ... "blubb": [(2, 0.4), (3, 0.1), (4, 0.8)]}
        >>> ii.preprocess_vsm(4)
        >>> res = ii.process_query_vsm(["bla", "blubb"])
        >>> res[0][0]
        4
        >>> '%.3f' % res[0][1]
        '0.800'
        >>> res[1][0]
        3
        >>> '%.3f' % res[1][1]
        '0.700'
        >>> res[2][0]
        2
        >>> '%.3f' % res[2][1]
        '0.400'
        >>> res[3][0]
        1
        >>> '%.3f' % res[3][1]
        '0.200'
        >>> res = ii.process_query_vsm(["bla", "blubb", "bla", "blubb"])
        >>> res[0][0]
        4
        >>> '%.3f' % res[0][1]
        '1.600'
        >>> res[1][0]
        3
        >>> '%.3f' % res[1][1]
        '1.400'
        >>> res[2][0]
        2
        >>> '%.3f' % res[2][1]
        '0.800'
        >>> res[3][0]
        1
        >>> '%.3f' % res[3][1]
        '0.400'
        """
        # Initialize vector with size m (size of term-doc matrix)
        query_vector = np.zeros(len(self.term_matrix_indices))
        for kw in keywords:
            if kw not in self.term_matrix_indices:
                continue
            query_vector[self.term_matrix_indices[kw]] += 1

        # * means the dot product here, see
        # http://stackoverflow.com/a/31040219
        scores = query_vector * self.td_matrix

        ret = []

        for i in range(scores.shape[0]):
            if scores[i] > 0.0:
                ret.append(((i + 1), scores[i]))
        return sorted(ret, key=lambda x: x[1], reverse=True)

    def process_query_lsi(self, keywords):
        """
        Process Query using lsi

        >>> ii = InvertedIndex()
        >>> ii.read_from_file("example2.txt", 1.75, 0.75)
        >>> ii.preprocess_vsm(4)
        >>> ii.preprocess_lsi(2)
        >>> ii.process_query_lsi(['web', 'surfing'])
        [(1, '0.944'), (4, '0.705'), (3, '0.568'), (2, '0.568'),\
 (6, '0.000'), (5, '0.000')]
        """
        query_vector = np.zeros(len(self.term_matrix_indices))
        for kw in keywords:
            if kw not in self.term_matrix_indices:
                continue
            query_vector[self.term_matrix_indices[kw]] += 1
        query_vector = np.dot(query_vector.T, self.UkSk)
        res = np.dot(query_vector, self.Vk)
        res = np.round(res, 3)
        ret = []
        for i in range(res.shape[0]):
            if res[i] >= 0.0:
                ret.append(((i + 1), '%.3f' % (res[i] + 0)))
        return sorted(ret, key=lambda x: (x[1], x[0]), reverse=True)

    def transform_to_bm25(self, k=1.75, b=0.75):
        """
        Exercise 02.01
        Transform term frequencies to BM25 scores
        """

        for word, il in self.inverted_lists.items():
            idf = math.log(len(self.document_lengths) / len(il), 2)
            for i, docs in enumerate(il):
                denom = (k * (1 - b + b *
                              (self.document_lengths[docs[0]-1] /
                               self.avg_doc_length)) + docs[1])
                tf = docs[1]
                tf_star = tf * (k + 1) / denom
                il[i] = (docs[0], tf_star * idf)
                # il[i] = (docs[0], tf * idf)

    def render_output(self, file_name, qry, qry_res, max_res):
        """
        Output results. Load documents from HD to save memory.
        """

        outputted = 0
        doc_ids_res = [docs[0] for docs in qry_res]

        with open(file_name) as file:
            for i, line in enumerate(file):
                if i + 1 in doc_ids_res[:max_res]:
                    outputted += 1
                    print(re.sub('\\b(' + '|'.join(qry) + ')\\b',
                                 "\033[3;37;40m" + '\\1' + "\033[0;0m",
                                 line, flags=re.IGNORECASE))
                if outputted >= max_res:
                    """ Look no further after we reached the desired number
                    of results. """
                    break

    def precision_at_k(self, res_ids, rel_ids, k):
        """
        >>> ii = InvertedIndex()
        >>> a = [(0, 1), (1, 4), (2, 3), (5, 3.5), (6, 8)]
        >>> '%.3f' % ii.precision_at_k(a, {0, 2, 5, 6, 7, 8}, 4)
        '0.750'
        """

        c = 0

        for i in range(0, min(k, len(res_ids))):
            if res_ids[i][0] in rel_ids:
                c += 1
        return c / k

    def average_p(self, res_ids, rel_ids):
        """
        >>> ii = InvertedIndex()
        >>> a = [(582, 0), (17, 0), (5666, 0), (10003, 0), (10, 0)]
        >>> '%.3f' % ii.average_p(a, {10, 582, 877, 10003})
        '0.525'
        """

        acc_p = 0

        for i, r in enumerate(res_ids):
            if r[0] in rel_ids:
                acc_p += self.precision_at_k(res_ids, rel_ids, i+1)

        return acc_p / len(rel_ids)

    def run_benchmark(self, file_name, l):
        p_at_3_sumv = 0
        p_at_r_sumv = 0
        ap_sumv = 0
        p_at_3_suml = 0
        p_at_r_suml = 0
        ap_suml = 0
        c = 0
        with open(file_name) as file:
            for line in file:
                c += 1
                query, gt = line.strip().split('\t')
                print("Eval for query ", query)

                query = re.split("\W+", query.lower())
                gt = set([int(f_id) for f_id in gt.split(' ')])

                qry_resvsm = self.process_query_vsm(query)
                qry_reslsi = self.process_query_lsi(query)

                p_at_3v = self.precision_at_k(qry_resvsm, gt, 3)
                p_at_rv = self.precision_at_k(qry_resvsm, gt, len(gt))
                apv = self.average_p(qry_resvsm, gt)

                p_at_3_sumv += p_at_3v
                p_at_r_sumv += p_at_rv
                ap_sumv += apv

                p_at_3l = self.precision_at_k(qry_reslsi, gt, 3)
                p_at_rl = self.precision_at_k(qry_reslsi, gt, len(gt))
                apl = self.average_p(qry_reslsi, gt)

                p_at_3_suml += p_at_3l
                p_at_r_suml += p_at_rl
                ap_suml += apl

        p_at_3_sumtt = l * p_at_3_sumv + (1 - l) * p_at_3_suml
        p_at_r_sumtt = l * p_at_r_sumv + (1 - l) * p_at_r_suml
        ap_sumtt = l * ap_sumv + (1 - l) * ap_suml
        print("MP@3v: %.2f" % (p_at_3_sumv / c))
        print("MP@Rv: %.2f" % (p_at_r_sumv / c))
        print("MAPv: %.2f" % (ap_sumv / c))
        print("MP@3l: %.2f" % (p_at_3_suml / c))
        print("MP@Rl: %.2f" % (p_at_r_suml / c))
        print("MAPl: %.2f" % (ap_suml / c))
        print("MP@3t: %.2f" % (p_at_3_sumtt / c))
        print("MP@Rt: %.2f" % (p_at_r_sumtt / c))
        print("MAPt: %.2f" % (ap_sumtt / c))

    def related_term_pairs(self, k):
        """
        Calculates the Term-Term matrix and gets the most related terms
        >>> ii = InvertedIndex()
        >>> ii.inverted_lists = {"lirum": [(2, 0.1)], "larum": [(8, 0.8)], \
"spoon": [(1, 0.2), (3, 0.6), (4, 0.1)], "handle": [(2, 0.4), \
(3, 0.1), (4, 0.8)]}
        >>> ii.preprocess_vsm(4)
        >>> ii.preprocess_lsi(2)
        >>> result = ii.related_term_pairs(1)
        >>> 'handle' in result[0]
        True
        >>> 'spoon' in result[0]
        True
        >>> '0.285' in result[0]
        True
        """
        Uk, Sk, Vk = scipy.sparse.linalg.svds(self.td_matrix, k)
        Ukc = csr_matrix(Uk)
        Tk = Ukc * Ukc.transpose()
        Tt = np.sort(np.asarray(Tk.todense()), axis=None)
        Tt = np.unique(Tt)[::-1][:200]
        indices = []
        for i in Tt:
            indices.append(np.isclose(Tk.todense(), i).nonzero()[0])
        found = 0
        result = []
        for i, index in enumerate(indices):
            r = []
            if found == k:
                break
            if len(index) == 2:
                found += 1
                r.append('%.3f' % Tt[i])
                r.append(self.matrix_indices_terms[index[1]])
                r.append(self.matrix_indices_terms[index[0]])
                result.append(r)
        return result


if __name__ == "__main__":

    if len(sys.argv) < 6:
        print("Usage: python3 inverted_index.py<file>\
 <benchmark> <k> <m> <lambda>")
        sys.exit()
    print("yo")
    file_name = sys.argv[1]
    k = int(sys.argv[3])
    m = int(sys.argv[4])
    l = float(sys.argv[5])
    ii = InvertedIndex()
    ii.read_from_file(file_name)
    print("Building sparse term-document matrix...")
    ii.preprocess_vsm(m)
    ii.preprocess_lsi(k)
    print("Done.")

    if len(sys.argv) == 6:
        bm_file_name = sys.argv[2]
        ii.run_benchmark(bm_file_name, l)
        # ii.related_term_pairs(k)
    else:
        while (True):
            qry = input("Enter query: ")
            """ Use the same word matching approach (regex on "\W+") as above.
            Filter out empty (None) strings."""
            keywords = list(filter(None, re.split("\W+", qry.lower())))
            print()
            ii.render_output(file_name, keywords,
                             ii.process_query_vsm(keywords), 3)
