
// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Authors: Hannah Bast <bast@cs.uni-freiburg.de>,
// Co-Author: Louay Abdelgawad <lo2aayyguc@gmail.com>,
//            Omar Kassem <omar.kassem67@gmail.com>

import org.junit.Test;
import org.junit.Assert;
import java.io.IOException;
import java.util.TreeMap;
import java.util.ArrayList;

/**
 * One unit test for each non-trivial method in the QGramIndex class.
 */
public class QGramIndexTest {

  @Test
  public void buildFromFile() throws IOException {
    QGramIndex qgi = new QGramIndex(3);
    qgi.buildFromFile("example.txt");
    Assert.assertEquals(16, qgi.invertedLists.size());
    Assert.assertEquals(4, qgi.invertedLists.get("$fo").size());
    Assert.assertEquals(3, qgi.invertedLists.get("oot").size());
    Assert.assertEquals(2, qgi.invertedLists.get("tba").size());
  }

  @Test
  public void qGrams() {
    QGramIndex qgi = new QGramIndex(3);
    Assert.assertEquals("[$$l, $li, lir, iru, rum]", 
      qgi.getQGrams("lirum").toString());
  }

  @Test
  public void checkPrefixEditDistance() {
    QGramIndex qgi = new QGramIndex(3);
    Assert.assertEquals(0, qgi.checkPrefixEditDistance("foo", "foo", 0));
    Assert.assertEquals(0, qgi.checkPrefixEditDistance("foo", "foo", 10));
    Assert.assertEquals(0, qgi.checkPrefixEditDistance("foo", "foot", 0));
    Assert.assertEquals(1, qgi.checkPrefixEditDistance("foot", "foo", 1));
    Assert.assertEquals(1, qgi.checkPrefixEditDistance("foo", "fotbal", 1));
    Assert.assertEquals(3, qgi.checkPrefixEditDistance("foo", "bar", 3));

    Assert.assertEquals(1, qgi.checkPrefixEditDistance("perf", "perv", 1));
    Assert.assertEquals(1, qgi.checkPrefixEditDistance("perv", "perf", 1));
    Assert.assertEquals(1, qgi.checkPrefixEditDistance("perf", "peff", 1));

    Assert.assertEquals(1, qgi.checkPrefixEditDistance("foot", "foo", 0));
    Assert.assertEquals(1, qgi.checkPrefixEditDistance("foo", "fotbal", 0));
    Assert.assertEquals(3, qgi.checkPrefixEditDistance("foo", "bar", 2));
  }

  @Test
  public void sortResult() {
    QGramIndex qgi = new QGramIndex(3);
    ArrayList<ArrayList<Integer>> data = new ArrayList<ArrayList<Integer>>();
    ArrayList<Integer> x = new ArrayList<Integer>();
    ArrayList<Integer> w = new ArrayList<Integer>();
    ArrayList<Integer> y = new ArrayList<Integer>();
    ArrayList<Integer> q = new ArrayList<Integer>();
    ArrayList<Integer> z = new ArrayList<Integer>();
    x.add(1);
    x.add(3);
    x.add(3);
    y.add(2);
    y.add(2);
    y.add(4);
    z.add(3);
    z.add(6);
    z.add(1);
    w.add(4);
    w.add(3);
    w.add(2);
    q.add(5);
    q.add(6);
    q.add(5);
    data.add(x);
    data.add(y);
    data.add(z);
    data.add(w);
    data.add(q);
    ArrayList<ArrayList<Integer>> data1 = new ArrayList<ArrayList<Integer>>();
    data1.add(y);
    data1.add(x);
    data1.add(w);
    data1.add(q);
    data1.add(z);
    Assert.assertEquals(data1, qgi.sortResult(data));
  }

  @Test
  public void computeUnion() {
    QGramIndex qgi = new QGramIndex(3);
    ArrayList<ArrayList<Integer>> data = new ArrayList<ArrayList<Integer>>();
    ArrayList<Integer> x = new ArrayList<Integer>();
    x.add(1);
    x.add(4);
    x.add(6);
    ArrayList<Integer> y = new ArrayList<Integer>();
    y.add(2);
    y.add(4);
    y.add(6);
    y.add(9);
    y.add(9);
    data.add(x);
    data.add(y);
    TreeMap<Integer, Integer> union = new TreeMap<Integer, Integer>();
    union.put(1, 1);
    union.put(2, 1);
    union.put(4, 2);
    union.put(6, 2);
    union.put(9, 2);
    Assert.assertEquals(union, qgi.computeUnion(data));
  }

  @Test
  public void findMatches() throws IOException {
    QGramIndex qgi = new QGramIndex(3);
    qgi.buildFromFile("example.txt");
    ArrayList<ArrayList<Integer>> data = new ArrayList<ArrayList<Integer>>();
    ArrayList<Integer> x = new ArrayList<Integer>();
    x.add(0);
    x.add(0);
    x.add(3);
    ArrayList<Integer> y = new ArrayList<Integer>();
    y.add(1);
    y.add(1);
    y.add(1);
    ArrayList<Integer> z = new ArrayList<Integer>();
    z.add(2);
    z.add(0);
    z.add(2);
    ArrayList<Integer> w = new ArrayList<Integer>();
    w.add(3);
    w.add(0);
    w.add(1);
    data.add(x);
    data.add(y);
    data.add(z);
    data.add(w);
    Assert.assertEquals(data, qgi.findMatches("foot", 1));
    ArrayList<ArrayList<Integer>> data2 = new ArrayList<ArrayList<Integer>>();
    data2.add(y);
    Assert.assertEquals(data2, qgi.findMatches("woob", 1));
  }
}
