
// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Authors: Hannah Bast <bast@cs.uni-freiburg.de>,
// Co-Author: Louay Abdelgawad <lo2aayyguc@gmail.com>,
//            Omar Kassem <omar.kassem67@gmail.com>

import java.io.IOException;
import java.util.Scanner;
import java.util.ArrayList;

/**
 *
 */
public class FuzzySearchMain {

  public static void main(String[] args) throws IOException {
    // Parse command line arguments.
    if (args.length != 1) {
      System.out.println("Usage: FuzzySearchMain <entities file>");
      System.exit(1);
    }
    String fileName = args[0];

    System.out.print("Reading strings and building index...");

    // Build q-gram index.
    QGramIndex qgi = new QGramIndex(3);
    qgi.buildFromFile(fileName);

    System.out.print(" done.\n");
    Scanner sc = new Scanner(System.in);
    ArrayList<ArrayList<Integer>> result = new ArrayList<ArrayList<Integer>>();
    while (true) {
      System.out.println(" \n Please enter an input: ");
      String s = sc.nextLine();
      long time1 = System.nanoTime();
      s = QGramIndex.normalizeString(s);
      result = qgi.findMatches(s, s.length() / 4);
      result = qgi.sortResult(result);
      System.out.print("#PED = " + qgi.noPED + "  ");
      System.out.println("#RES = " + result.size());
      for (int i = 0; i < Math.min(5, result.size()); i++) {
        System.out.println(qgi.originalWords.get(result.get(i).get(0)) 
          + "   " + result.get(i).get(1) + "   "
            + result.get(i).get(2));
      }
      long time2 = System.nanoTime();
      long timediff = (time2 - time1) / 1000000;
      System.out.println("Time taken is: " + timediff + "ms");
    }
  }
}
