// Copyright 2016, University of Freiburg,
// Chair of Algorithms and Data Structures.
// Author: Hannah Bast <bast@cs.uni-freiburg.de>.

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.util.ArrayList;


/**
 * Demo search server.
 */
public class SearchServerMain {

  public static String fuzzySearch(String query, QGramIndex qgi) {
    if (query.length() > 0) {
      ArrayList<ArrayList<Integer>> result = 
              new ArrayList<ArrayList<Integer>>();
      ArrayList<String> matches = new ArrayList<String>();
      query = QGramIndex.normalizeString(query);
      result = qgi.findMatches(query, query.length() / 4);
      result = qgi.sortResult(result);
      if (result.size() == 0) {
        return "";
      }
      String jsonResult = "[";
      for (int i = 0; i < Math.min(10, result.size()); i++) {
        jsonResult += "{ \"city\": \"" + qgi.originalWords.get(
              result.get(i).get(0)) + "\"";
        jsonResult += ", \"score\": " + result.get(i).get(2);
        jsonResult += ", \"ped\": " + result.get(i).get(1) + "},";
      }
      jsonResult = jsonResult.substring(0, jsonResult.length() - 1) + ']';
      return jsonResult;
    }
    return "";
  }

  public static void main(String[] args) throws IOException {

    // Parse the command line arguments.
    if (args.length < 2) {
      System.out.println("Usage: java -jar SearchServerMain.jar <file> <port>");
      System.exit(1);
    }
    String inputFile = args[0];
    int port = Integer.parseInt(args[1]);
    QGramIndex qgi = new QGramIndex(3);
    qgi.buildFromFile(inputFile);
    ServerSocket server = new ServerSocket(port);
    BufferedWriter out = null;

    while (true) {
      System.out.print("Waiting for query on port "
          + port +  " ...");
      Socket client = server.accept();

      BufferedReader requestReader = new BufferedReader(
          new InputStreamReader(client.getInputStream()));
      String request = requestReader.readLine();
      String content = "";
      String contentType = "text/plain";
      String status = "HTTP/1.1 200 ok";
      if (request != null) {
        if (!request.startsWith("GET /")) {
          System.out.println("Only get requests");
        } else {
          request = request.substring(5, request.indexOf(" HTTP/1.1"));
          if (request.equals("")) {
            request = "search.html";
          }
          if (request.startsWith("?q=")) {
            String query = request.substring(3, request.length());
            content = fuzzySearch(query, qgi);
            contentType = "text/plain";
          } else {
            File file = new File(request);
            if (file.canRead()) {
              FileInputStream fis = new FileInputStream(file);
              byte[] bytes = new byte[(int) file.length()];
              fis.read(bytes);
              content = new String(bytes, "UTF-8");
              if (request.endsWith(".html")) {
                contentType = "text/html";
              } else if (request.endsWith(".css")) {
                contentType = "text/css";
              } else if (request.endsWith(".js")) {
                contentType = "text/js";
              }
            } else {
              file = new File("fileNotFound404.html");
              status = "HTTP/1.1 404 File not found";
              contentType = "text/html";
              FileInputStream fis = new FileInputStream(file);
              byte[] bytes = new byte[(int) file.length()];
              fis.read(bytes);
              content = new String(bytes, "UTF-8");
            }
          }
        }
      }  
      DataOutputStream dos = new DataOutputStream(
        client.getOutputStream());
      StringBuilder response = new StringBuilder();
      response.append(status + "\r\n");
      response.append("Content-Length: " + content.getBytes("UTF-8").length 
            + "\r\n");
      response.append("Content-Type: " + contentType + "\r\n");
      response.append("\r\n");
      response.append(content);
      dos.write(response.toString().getBytes("UTF-8"));
      dos.close();
      client.close();
      System.out.println("");
    }
  }
}
