
// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Authors: Hannah Bast <bast@cs.uni-freiburg.de>,
//          Patrick Brosi <brosi@informatik.uni-freiburg.de>..

import java.io.IOException;

/**
 * 
 */
public class IntersectMain {

  public static void main(String[] listNames) throws IOException {
    if (listNames.length < 2) {
      System.out.println("Usage IntersectMain.jar <posting lists>");
      System.exit(1);
    }

    // Read lists.
    int m = listNames.length;
    PostingList lists[] = new PostingList[m];
    Intersect is = new Intersect();
    System.out.println();
    for (int i = 0; i < listNames.length; i++) {
      System.out.print("Reading list \"" + listNames[i] + "\" ... ");
      System.out.flush();
      lists[i] = is.readPostingListFromFile(listNames[i]);
      System.out.println("done, size = " + lists[i].ids.length);
    }

    // Intersect all pairs.
    System.out.println();
    int totalRuns = 0;
    int totalTime = 0;
    for (int i = 0; i < m; i++) {
      for (int j = 0; j < i; j++) {
        int timeAverage = 0;
        int size = 0;
        totalRuns++;
        System.out.println("Intersecting " + listNames[i] 
          + " + " + listNames[j] + " ... ");
        System.out.flush();
        int x = 0;
        PostingList result = null;
        int n1 = lists[i].size;
        int n2 = lists[j].size;
        int diff = Math.max(n1, n2) / Math.min(n1, n2);
        long time1 = System.nanoTime();
        if (diff > 100) {
          while (x < 20) {
            result = is.intersectGalloping(lists[i], lists[j]);
            x++;
          }
        } else {
          while (x < 20) {
            result = is.intersectWithNative(lists[i], lists[j]);
            x++;
          }
        }
        long time2 = System.nanoTime();
        long time = (time2 - time1) / 20000;
        totalTime += time;
        timeAverage += time;
        size = result.size;
        System.out.println("result size = " + size + ", "
          + "time = " + timeAverage + "micros");
      }
    }

    System.out.println();

    int averageTime = totalTime / totalRuns;
    System.out.format("Average time = %d micros%n", averageTime);
  }
}
