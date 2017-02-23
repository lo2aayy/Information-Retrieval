
// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Authors: Hannah Bast <bast@cs.uni-freiburg.de>,
//          Patrick Brosi <brosi@informatik.uni-freiburg.de>.

import java.util.ArrayList;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;

/**
 * Code for intersecting two posting lists.
 */
public class Intersect {

  private BufferedReader bufferedReader;

  /**
   * Read posting list from file.
   */
  PostingList readPostingListFromFile(String fileName) throws IOException {
    // First read into two ArrayList objects docids and sores.
    FileReader fileReader = new FileReader(fileName);
    bufferedReader = new BufferedReader(fileReader);

    // get record count info
    String l = bufferedReader.readLine();
    int numRecords = Integer.parseInt(l);

    ArrayList<Integer> ids = new ArrayList<Integer>(numRecords);
    ArrayList<Integer> scores = new ArrayList<Integer>(numRecords);

    int i = 0;
    while (i < numRecords) {
      i++;
      String line = bufferedReader.readLine();
      if (line == null) {
        break;
      }
      String[] parts = line.split("\\W+");
      ids.add(Integer.parseInt(parts[0]));
      scores.add(Integer.parseInt(parts[1]));
    }
    return new PostingList(ids, scores);
  }

  /**
   * Intersect two posting lists using the simple "zipper" algorithm.
   */
  PostingList intersect(PostingList list1, PostingList list2) {
    int n1 = list1.ids.length;
    int n2 = list2.ids.length;
    int n = Math.min(n1, n2); // max result size.
    ArrayList<Integer> ids = new ArrayList<Integer>(n);
    ArrayList<Integer> scores = new ArrayList<Integer>(n);
    int i = 0;
    int j = 0;
    while (i < n1 && j < n2) {
      while (i < n1 && list1.ids[i] < list2.ids[j]) {
        i++;
      }

      if (i == n1) {
        break;
      }

      while (j < n2 && list2.ids[j] < list1.ids[i]) {
        j++;
      }

      if (j == n2) {
        break;
      }

      if (list1.ids[i] == list2.ids[j]) {
        ids.add(list1.ids[i]);
        scores.add(list1.scores[i] + list2.scores[j]);
        i++;
        j++;
      }
    }
    return new PostingList(ids, scores);
  }

  int binarySearch(PostingList l1, int id, int min, int max) {
    /* 
    This methods performs a binary search on the list
    l1 looking for the number id and returns its index if
    found else returns -1
    */
    int index = 0;
    while (min <= max) {
      index = min + (max - min) / 2;
      if (l1.ids[index] == id) {
        return index;
      } else if (l1.ids[index] > id) {
        max = index - 1;
      } else {
        min = index + 1;
      }
    }
    return -1;
  }

  PostingList intersectWithNative(PostingList list1, PostingList list2) {
    /*
    Same implementation of the intersect method
    but uses native arrays instead of ArrayLists
    */
    int n1 = list1.ids.length;
    int n2 = list2.ids.length;
    int n = Math.min(n1, n2); // max result size.
    int[] ids = new int[n];
    int[] scores = new int[n];
    int i = 0;
    int j = 0;
    int z = 0;
    while (i < n1 && j < n2) {
      while (i < n1 && list1.ids[i] < list2.ids[j]) {
        i++;
      }

      if (i == n1) {
        break;
      }

      while (j < n2 && list2.ids[j] < list1.ids[i]) {
        j++;
      }

      if (j == n2) {
        break;
      }

      if (list1.ids[i] == list2.ids[j]) {
        ids[z] = (list1.ids[i]);
        scores[z] = (list1.scores[i] + list2.scores[j]);
        i++;
        j++;
        z++;
      }
    }
    return new PostingList(ids, scores, z);
  }

  PostingList intersectGalloping(PostingList list1, PostingList list2) {
    /*
    The method returns intersection of the PostingLists
    using Galloping
    */
    int n1 = list1.ids.length;
    int n2 = list2.ids.length;
    PostingList shortl = new PostingList();
    PostingList longl = new PostingList();
    if (n1 < n2) {
      shortl = list1;
      longl = list2;
    } else {
      shortl = list2;
      longl = list1;
    }
    int n = Math.min(n1, n2);
    int[] ids = new int[n];
    int[] scores = new int[n];
    int i = 0;
    int j = 0;
    int z = 0;
    int index;
    int step = 1;
    while (i < shortl.size) {
      while (j + step < longl.size && longl.ids[j + step] < shortl.ids[i]) {
        j += step;
        step *= 2;
      }
      index = binarySearch(longl, shortl.ids[i], j, Math.min(j 
        + step, longl.size));
      if (index != -1) {
        ids[z] = shortl.ids[i];
        scores[z] = shortl.scores[i] + longl.scores[index];
        z++;
        i++;
      } else {
        i++;
      }
      step = 1;
    }
    return new PostingList(ids, scores, z);
  }

  PostingList intersectBinary(PostingList l1, PostingList l2) {
    /*
    The returns the intersection of both PostingLists
    using binary search
    */
    PostingList shortl = new PostingList();
    PostingList longl = new PostingList();
    if (l1.size < l2.size) {
      shortl = l1;
      longl = l2;
    } else {
      shortl = l2;
      longl = l1;
    }
    int n1 = l1.ids.length;
    int n2 = l2.ids.length;
    int n = Math.min(n1, n2);
    int[] ids = new int[n];
    int[] scores = new int[n];
    int z = 0;
    int min;
    int max;
    int index;
    for (int i = 0; i < shortl.size; i++) {
      max = longl.size - 1;
      min = 0;
      while (min <= max) {
        index = min + (max - min) / 2;
        if (shortl.ids[i] == longl.ids[index]) {
          ids[z] = shortl.ids[i];
          scores[z] = shortl.scores[i] + longl.scores[index];
          z++;
          break;
        } else if (shortl.ids[i] < longl.ids[index]) {
          max = index - 1;
        } else {
          min = index + 1;
        }
      }
    }
    return new PostingList(ids, scores, z);
  }

  PostingList intersectBinaryWithRemainder(PostingList l1, PostingList l2) {
    /*
    The method returns the intersection of the PostingLists
    using binary search and removing remainders of the long list
    */
    PostingList shortl = new PostingList();
    PostingList longl = new PostingList();
    if (l1.size < l2.size) {
      shortl = l1;
      longl = l2;
    } else {
      shortl = l2;
      longl = l1;
    }
    int n1 = l1.ids.length;
    int n2 = l2.ids.length;
    int n = Math.min(n1, n2);
    int[] ids = new int[n];
    int[] scores = new int[n];
    int min = 0;
    int max;
    int index;
    int remainder = 0;
    int z = 0;
    for (int i = 0; i < shortl.size; i++) {
      max = longl.size;
      min = remainder;
      while (min <= max) {
        index = min + (max - min) / 2;
        if (shortl.ids[i] == longl.ids[index]) {
          ids[z] = shortl.ids[i];
          scores[z] = (shortl.scores[i] + longl.scores[index]);
          remainder = index;
          z++;
          break;
        } else if (shortl.ids[i] < longl.ids[index]) {
          max = index - 1;
        } else {
          min = index + 1;
        }
      }
      remainder = min;
    }
    return new PostingList(ids, scores, z);
  }
}
