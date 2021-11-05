# -*- coding: utf-8 -*-


import json
# if you are using python 3, you should 
import urllib.request 
from urllib.parse import quote


# change the url according to your own corename and query
#inurl = 'http://localhost:8983/solr/corename/select?q=*%3A*&fl=id%2Cscore&wt=json&indent=true&rows=20'
core = 'BM25_2'
ip = '3.137.137.240'
file1 = open('queries.txt', 'r',encoding='utf-8')
Lines = file1.readlines()
file1.close()
inputlines = []
for line in Lines:
    #text = line.split(' ')
    text = ''
    for i in range(4,len(line)):
        text = text + line[i]
    inputlines.append(text)


count = 0
#input1 = ['Anti-Refugee Rally in Dresden','Syrian civil war','Assad und ISIS auf dem Vormarsch','Russische Botschaft in Syrien von Granaten getroffen','Бильд. Внутренний документ говорит, что Германия примет 1,5 млн беженцев в этом году']
for line in inputlines:
    count = count + 1
    encoded_input = quote(line)
    print(line)
    #inurl = f'http://{ip}:8983/solr/{core}/select?q=text_en:{encoded_input}%20OR%20text_de:{encoded_input}%20OR%20text_ru:{encoded_input}&fl=id%2Cscore&wt=json&indent=true&rows=20'
    inurl = f'http://{ip}:8983/solr/{core}/select?q={encoded_input}&q.op=OR&defType=edismax&qf=text_en%20text_ru%20text_de&fl=id%2Cscore&wt=json&indent=true&rows=20'
    print(inurl)
    outfn = 'q1.txt'
    if count > 9:
        qid = '0' + str(count)
    else:
        qid = '00' + str(count)

    IRModel='bm25' #either bm25 or vsm
    outf = open(outfn, 'a+')
    data = urllib.request.urlopen(inurl)

    docs = json.load(data)['response']['docs']
    rank = 1
    for doc in docs:
        outf.write(qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + IRModel + '\n')
        rank += 1
    outf.close()
