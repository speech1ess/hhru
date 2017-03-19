import urllib
import requests
import sqlite3
import json
import ssl

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

print "Setting variables."
#base URL
baseurl = "https://api.hh.ru/"
#vacancies URL
vcnurl = baseurl+'vacancies?'
#areas URL
areas = baseurl+'areas'

headers = {'User-Agent': 'My User Agent 1.0'}
keyword = unicode(raw_input("Enter search keyword (default is 'python'): "), "utf-8")
if len(keyword) < 1 : keyword = 'python'
print "Search keyword is '"+keyword+"'."
vacancies = vcnurl+'text='+keyword

conn = sqlite3.connect('hhru.sqlite')
cur = conn.cursor()

print "Creating tables."
cur.executescript('''
DROP TABLE IF EXISTS Areas;
CREATE TABLE IF NOT EXISTS Areas (
    id INTEGER,
    parent_id INTEGER,
    name TEXT
);
DROP TABLE IF EXISTS Vacancies;
CREATE TABLE IF NOT EXISTS Vacancies (
    id INTEGER,
    salary_min INTEGER,
    salary_max INTEGER,
    name TEXT,
    area_id INTEGER,
    created TEXT
)''')

print "Opening URL: "+areas
uh = urllib.urlopen(areas)
data = uh.read()

try: js = json.loads(str(data))
except: js = None

#print json.dumps(js, indent=4)
for area in js:
    print "Retrieving area "+area['name']+" data."
    if area['parent_id'] == None:
        cur.execute('''INSERT OR IGNORE INTO Areas (id, name) VALUES ( ?, ? )''', (area['id'], area['name']))
        print area['id'], area['name']
        for i in area['areas']:
            cur.execute('''INSERT OR IGNORE INTO Areas (id, parent_id, name) VALUES ( ?, ?, ? )''', (i['id'], i['parent_id'], i['name']))
            #print i['id'], i['parent_id'], i['name']
            if i['areas'] != None:
                for x in i['areas']:
                    #print x['id'], x['name']
                    cur.execute('''INSERT OR IGNORE INTO Areas (id, parent_id, name) VALUES ( ?, ?, ? )''', (x['id'], x['parent_id'], x['name']))

pagecounter = 0
js = requests.get(vacancies+'&page='+str(pagecounter)+'&per_page=100', headers=headers)
pages = js.json()['pages']
print "Opening URL: "+vacancies+'&page='+str(pagecounter)+'&per_page=100'
print "Total pages: "+str(pages)
while pagecounter  < pages:
    print "Retrieving vacancies. Page "+str(pagecounter+1)+". \n Opening URL: "+vacancies+'&page='+str(pagecounter)+'&per_page=100'
    for item in js.json()['items']:
        if item['salary'] != None:
            #print item['id'], item['salary']['from'], item['salary']['to'], item['name'], item['area']['id'], item['created_at']
            cur.execute('''INSERT OR IGNORE INTO Vacancies (id, salary_min, salary_max, name, area_id, created) VALUES ( ?, ?, ?, ?, ?, ? )''', (item['id'], item['salary']['from'], item['salary']['to'], item['name'], item['area']['id'], item['created_at']))
        else:
            #print item['id'], item['name'], item['area']['id'], item['created_at']
            cur.execute('''INSERT OR IGNORE INTO Vacancies (id, name, area_id, created) VALUES ( ?, ?, ?, ? )''', (item['id'], item['name'], item['area']['id'], item['created_at']))
    pagecounter = pagecounter + 1
    js = requests.get(vacancies+'&page='+str(pagecounter)+'&per_page=100', headers=headers)

print "Writing changes to DB."
conn.commit()
