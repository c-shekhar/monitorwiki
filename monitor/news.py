import goslate
import time
import mysql.connector
from random import randint
from mysql.connector import MySQLConnection, Error
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
gs = goslate.Goslate()
keys=['page_id','page_title','weight','lang','updated']
data=[]
try:
    conn = mysql.connector.connect(host='localhost',
                                   database='minor',
                                   user='root',
                                   password='password')
    print ("string1");
    if conn.is_connected():
        print('Connected to MySQL database')
        cursor = conn.cursor();
        cursor.execute("SELECT * FROM edits");
        row = cursor.fetchone();
        i=0; 
        while row is not None:
            page_id=row[0]
            page_title=row[1]
            weight=0
            lang=row[19]
            updated=row[18]
            value=[page_id,page_title,weight,lang,updated]
            data.append(dict(zip(keys,value)))
            row = cursor.fetchone()
except Error as e:
    print ("string5")
    print(e)
finally:
    cursor.close()        
    conn.close()
# print data[1]['page_title'];
i=0
print len(data);
compare=list();
k=374
l=0
for k in data:
    try:
        if k['lang']!='en':
            temp1=gs.translate(k['page_title'],'en')
            temp=temp1.lower();
            compare.append('temp')
        compare.append(k['page_title'])
        print k['page_title']
        l=l+1;
        if l>100:
             time.sleep(10*randint(1,9))
             l=0;
        i = i+1
        print i
    except:
        pass
print len(compare);

for x in range(len(compare)):
    for r in compare:
        temp1=fuzz.ratio(compare[x],r)
        fuzz.partial_ratio(compare[x],r)
        fuzz.token_sort_ratio(compare[x],r)
        process.extract(compare[x], compare, limit=2)
        print temp1
