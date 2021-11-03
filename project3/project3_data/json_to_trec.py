# -*- coding: utf-8 -*-


import json
# if you are using python 3, you should 
import urllib.request 
from urllib.parse import quote
#import urllib2


# change the url according to your own corename and query
#inurl = 'http://localhost:8983/solr/corename/select?q=*%3A*&fl=id%2Cscore&wt=json&indent=true&rows=20'
core1 = ['VSM_1','BM25_1']
input1 = ['Anti-Refugee Rally in Dresden','Syrian civil war','Assad und ISIS auf dem Vormarsch','Russische Botschaft in Syrien von Granaten getroffen','Бильд. Внутренний документ говорит, что Германия примет 1,5 млн беженцев в этом году']
ip = '18.219.42.216'

for core in core1:
    encoded_input = quote(input)
    print(encoded_input)

    inurl = f'http://{ip}:8983/solr/{core}/select?q=text_en:{encoded_input}%20OR%20text_de:{encoded_input}%20OR%20text_ru:{encoded_input}&fl=id%2Cscore&wt=json&indent=true&rows=20'
    outfn = 'q3.txt'
input = 'Anti-Refugee Rally in Dresden'
encoded_input = quote(input)
print(inurl)


# change query id and IRModel name accordingly
qid = '001'
IRModel='vsm' #either bm25 or vsm
outf = open(outfn, 'a+')
#data = urllib2.urlopen(inurl)
# if you're using python 3, you should use
data = urllib.request.urlopen(inurl)

docs = json.load(data)['response']['docs']
# the ranking should start from 1 and increase
rank = 1
for doc in docs:
    outf.write(qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
    rank += 1
outf.close()
