import json
# if you are using python 3, you should 
import urllib.request
from urllib.parse import quote

# import urllib2

# declare parameters
AWS_IP = '3.137.137.240'
IRModel = ['BM25', 'VSM'] #either bm25 or vsm
f = open('test-queries.txt','r',encoding='utf-8')
documents = f.readlines()

for Model in IRModel:
    if Model == 'bm25':
        core = "BM25_2"
    else:
        core = "VSM_2"
    print(core)

    for index, document in enumerate(documents):
        qid = document[ 0 : 4 ]
        text = document[ 4 : -1 ]

        inputText = quote(text)
        inurl = f'http://{AWS_IP}:8983/solr/{core}/select?q=text_en:{inputText}%20OR%20text_de:{inputText}%20OR%20text_ru:{inputText}&fl=id%2Cscore&wt=json&indent=true&rows=20'

        outfn = f'{Model}/{index+1}.txt'

        print('MY OUTPUT FILE PATH>> ',outfn)       
        outf = open(outfn, 'a+')

        data = urllib.request.urlopen(inurl)

        docs = json.load(data)['response']['docs']
        # the ranking should start from 1 and increase
        rank = 1
        for doc in docs:
            outf.write(qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + Model + '\n')
            rank += 1
        outf.close()