PORT = 9000
FILE = cities.txt

SearchServerMain.jar:
	ant jar
	make start

start: SearchServerMain.jar
	java -jar SearchServerMain.jar $(FILE) $(PORT)