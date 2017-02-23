
// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Authors: Hannah Bast <bast@cs.uni-freiburg.de>,
// Co-Author: Louay Abdelgawad <lo2aayyguc@gmail.com>,
//            Omar Kassem <omar.kassem67@gmail.com>

import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.TreeMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

/**
 * First steps towards a q-gram index, written during class.
 */
public class QGramIndex {

  /**
   * Create an empty QGramIndex.
   */
  public QGramIndex(int q) {
    this.invertedLists = new TreeMap<String, ArrayList<Integer>>();
    this.q = q;
    this.padding = new String(new char[q - 1]).replace("\u0000", "$");
    this.scores = new ArrayList<Integer>();
    this.words = new ArrayList<String>();
    this.originalWords = new ArrayList<String>();
    this.noPED = 0;
  }

  /**
   * Build index from given list of entites (one line per entity, columns are:
   * entity name, score, ...).
   */
  public void buildFromFile(String fileName) throws IOException {
    FileReader fileReader = new FileReader(fileName);
    BufferedReader bufferedReader = new BufferedReader(fileReader);
    String line;
    int entityId = 0;
    while ((line = bufferedReader.readLine()) != null) {
      String name = line.split("\t")[0];
      for (String qGram : getQGrams(name)) {
        if (!invertedLists.containsKey(qGram)) {
          invertedLists.put(qGram, new ArrayList<Integer>());
        }
        invertedLists.get(qGram).add(entityId);
      }
      scores.add(Integer.parseInt(line.split("\t")[1]));
      words.add(this.normalizeString(name));
      originalWords.add(name);
      entityId++;
    }
  }

  /**
   * Compute q-grams for padded, normalized version of given string.
   */
  public ArrayList<String> getQGrams(String name) {
    name = padding + name.toLowerCase().replaceAll("\\W", "");
    ArrayList<String> result = new ArrayList<String>();
    for (int i = 0; i < name.length() - q + 1; i++) {
      result.add(name.substring(i, i + q));
    }
    return result;
  }

  // Finds matches between a prefix and the words in the file
  public ArrayList<ArrayList<Integer>> findMatches(String prefix, int delta) {
    prefix = this.normalizeString(prefix);
    ArrayList<String> qGrams = this.getQGrams(prefix);
    ArrayList<ArrayList<Integer>> matches = new ArrayList<ArrayList<Integer>>();
    for (int i = 0; i < qGrams.size(); i++) {
      matches.add(this.invertedLists.get(qGrams.get(i)));
    }
    int repitition;
    int lengthY;
    int threshold;
    int ped;
    this.noPED = 0;
    ArrayList<ArrayList<Integer>> res = new ArrayList<ArrayList<Integer>>();
    TreeMap<Integer, Integer> candidate = this.computeUnion(matches);
    for (int key : candidate.keySet()) {
      repitition = candidate.get(key);
      lengthY = this.words.get(key).length();
      threshold = prefix.length() - delta * this.q;
      ArrayList<Integer> temp = new ArrayList<Integer>();
      if (repitition >= threshold) {
        ped = this.checkPrefixEditDistance(prefix, this.words.get(key), delta);
        this.noPED++;
        if (ped <= delta) {
          temp.add(key);
          temp.add(ped);
          temp.add(this.scores.get(key));
          res.add(temp);
        }
      }
    }
    return res;
  }

  // Removes whitespace and turns string to lower case
  public static String normalizeString(String name) {
    name = name.toLowerCase().replaceAll("\\W", "");
    return name;
  }

  // Sorts an Array list of Array lists according to 
  // score - ped
  public ArrayList<ArrayList<Integer>> 
    sortResult(ArrayList<ArrayList<Integer>> res) {
    Collections.sort(res, new Comparator<ArrayList<Integer>>() {
      @Override
      public int compare(ArrayList<Integer> o1, ArrayList<Integer> o2) {
        int score1 = o1.get(2) - o1.get(1);
        int score2 = o2.get(2) - o2.get(1);
        return Integer.compare(score2, score1);
      }
    });
    return res;
  }

  // Method for computing union of a list of arraylists
  public TreeMap<Integer, Integer> 
    computeUnion(ArrayList<ArrayList<Integer>> lists) {
    TreeMap<Integer, Integer> union = new TreeMap<Integer, Integer>();
    for (int i = 0; i < lists.size(); i++) {
      if (lists.get(i) != null) {
        for (int j = 0; j < lists.get(i).size(); j++) {
          if (!union.containsKey(lists.get(i).get(j))) {
            union.put(lists.get(i).get(j), 0);
          }
          union.put(lists.get(i).get(j), union.get(lists.get(i).get(j)) + 1);
        }
      }
    }
    return union;
  }

  // Method for calculating the PED between a prefix and a word
  public int checkPrefixEditDistance(String prefix, String word, int delta) {
    int[] lastLine = editDistance(prefix, word);
    int min = prefix.length() + delta + 1;
    int limit = Math.min(min, word.length());
    for (int i = 0; i < limit + 1; i++) {
      if (lastLine[i] < min) {
        min = lastLine[i];
      }
    }
    if (min <= delta) {
      return min;
    }
    return delta + 1;
  }

  // Helper Method to calculate the ED
  private int[] editDistance(String x, String y) {

    int[][] table = new int[x.length() + 1][y.length() + 1];
    for (int i = 0; i < x.length() + 1; i++) {
      table[i][0] = i;
    }

    for (int i = 0; i < y.length() + 1; i++) {
      table[0][i] = i;
    }
    for (int i = 1; i < x.length() + 1; i++) {
      for (int j = 1; j < y.length() + 1; j++) {
        if (x.charAt(i - 1) == y.charAt(j - 1)) {
          table[i][j] = table[i - 1][j - 1];
        } else {
          table[i][j] = Math.min(Math.min(table[i][j - 1], 
            table[i - 1][j]), table[i - 1][j - 1]) + 1;
        }
      }
    }
    return table[x.length()];
  }

  // The value of q.
  protected int q;

  // The padding (q - 1 times $).
  protected String padding;

  // The inverted lists.
  protected TreeMap<String, ArrayList<Integer>> invertedLists;

  // All the scores stored in this list
  protected ArrayList<Integer> scores;

  // The words after normalizing
  protected ArrayList<String> words;

  // The words before normalizing
  protected ArrayList<String> originalWords;

  // The number of PED calculations
  protected int noPED;
};
