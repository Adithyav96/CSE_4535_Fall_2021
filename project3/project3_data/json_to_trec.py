import json
# if you are using python 3, you should 
import urllib.request
from urllib.parse import quote

# import urllib2

# declare parameters
ip = '3.137.137.240'
IRModel = ['bm25', 'vsm'] #either bm25 or vsm
f = open('test-queries.txt','r',encoding='utf-8')
documents = f.readlines()

for Model in IRModel:
    if Model == 'bm25':
        core = "BM25_2"
    else:
        core = "VSM_2"

    for index, document in enumerate(documents):
        qid = document[ 0 : 4 ]
        text = document[ 4 : -1 ]

        inputText = quote(text)
        inurl = f'http://{ip}:8983/solr/{core}/select?q={inputText}&q.op=OR&defType=dismax&qf=text_en%20text_ru%20text_de&fl=id%2Cscore&wt=json&indent=true&rows=20'

        if Model == 'bm25':
            outfn = f'BM25/{index+1}.txt'    
        else:
            outfn = f'VSM/{index+1}.txt'
        
        outf = open(outfn, 'a+')

        data = urllib.request.urlopen(inurl)

        docs = json.load(data)['response']['docs']
        # the ranking should start from 1 and increase
        rank = 1
        for doc in docs:
            outf.write(qid + ' ' + 'Q0' + ' ' + str(doc['id']) + ' ' + str(rank) + ' ' + str(doc['score']) + ' ' + Model + '\n')
            rank += 1
        outf.close()