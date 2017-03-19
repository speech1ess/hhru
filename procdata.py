import sqlite3
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

conn = sqlite3.connect('hhru.sqlite')
cur = conn.cursor()

counter = dict()

def definecntr(area_id):
    cur.execute('SELECT * FROM Areas WHERE id=?', ( area_id, ))
    row = cur.fetchone()
    area_id = row[1]
    if area_id != None : definecntr(area_id)
    else:
        country = counter.get(row[2], None)
        if country is None:
            #print "Adding "+row[2]+" to counter."
            counter[row[2]] = 1
        else:
            #print counter[row[2]]
            counter[row[2]] += 1

cur.execute('SELECT id, name, area_id FROM Vacancies')
rows = cur.fetchall()
for row in rows:
    definecntr(row[2])

fhand = open('gpie.js','w')
fhand.write("gpie = [ ['Country', '% of vacancies'],")
for key, value in counter.items():
    fhand.write("\n['"+key+"', "+str(value)+"],")
    #print key, value
fhand.write("\n];\n")
print "Data written to gpie.js"
print "Open gpie.html in a browser to view"
