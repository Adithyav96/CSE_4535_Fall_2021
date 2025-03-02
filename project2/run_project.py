'''
@author: Sougata Saha
Institute: University at Buffalo
'''

from tqdm import tqdm
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()

    def _merge(self,pl1,pl2,isSkip):
        """ Implement the merge algorithm to merge 2 postings list at a time.
            Use appropriate parameters & return types.
            While merging 2 postings list, preserve the maximum tf-idf value of a document.
            To be implemented."""
        plList = LinkedList()
        com_count = 0
        l1 = pl1.start_node
        l2 = pl2.start_node
        while l1 is not None and l2 is not None:
            com_count = com_count + 1
            if l1.value == l2.value:
                if l1.score > l2.score:
                    plList.insert_at_end(l1.value,l1.score)
                else:
                    plList.insert_at_end(l2.value,l2.score)
                l1 = l1.next
                l2 = l2.next
            elif l1.value < l2.value:
                if isSkip:
                    if l1.skipPointer is not None and l1.skipPointer.value <= l2.value:
                        l1 = l1.skipPointer
                    else:
                        l1 = l1.next
                else:
                    l1 = l1.next
            else:
                if isSkip:
                    if l2.skipPointer is not None and l2.skipPointer.value <= l1.value:
                        l2 = l2.skipPointer
                    else:
                        l2 = l2.next
                else:
                    l2 = l2.next
        return plList,com_count

        #raise NotImplementedError

    def _daat_and(self,query,isSkip,isTf_idfSort):
        """ Implement the DAAT AND algorithm, which merges the postings list of N query terms.
            Use appropriate parameters & return types.
            To be implemented."""
        print("Query*******")
        print(query)
        index = self.indexer.get_index()
        number_of_terms = len(query)
        final_list = []
        final_pl_list = LinkedList()
        final_comparisions = 0
        pl = OrderedDict({})
        for term in query:
            pl[term] = index[term]
        sorted_terms = sorted(pl, key=lambda x:pl[x].length, reverse=False)
        pl1 = index[sorted_terms[0]]
        pl2 = index[sorted_terms[1]]
        term_index = 0
        while term_index < number_of_terms:
            com = 0
            term_index = term_index + 1
            if term_index == number_of_terms:
                break
            pl2 = index[sorted_terms[term_index]]
            final_pl_list,com = self._merge(pl1,pl2,isSkip)
            if isSkip:
                final_pl_list.add_skip_connections()
            pl1 = final_pl_list
            final_comparisions = final_comparisions + com 

        if isTf_idfSort == True:
            unsorted_dict = OrderedDict({})
            sorted_dict = OrderedDict({})
            pl_list = final_pl_list.start_node
            while pl_list is not None:
                unsorted_dict[pl_list.value] = pl_list.score
                pl_list = pl_list.next

            sorted_keys = sorted(unsorted_dict.items(), key = lambda x: x[1],reverse=True)  # [1, 3, 2]
            print("Dictionary values before sorting--------------------")
            print(unsorted_dict)
            for item in sorted_keys:
                final_list.append(item[0])
            print("Dictionary values aftering sorting--------------------")
            print(unsorted_dict)

        else:
            final_list = final_pl_list.traverse_list()
        return final_list,final_comparisions
        #raise NotImplementedError

    def _get_postings(self,term,isSkipPosting):
        """ Function to get the postings list of a term from the index.
            Use appropriate parameters & return types.
            To be implemented."""
        postingslist = []
        index = self.indexer.get_index()
        if term not in index:
            return postingsList
        if isSkipPosting is False:
            postingsList = index[term].traverse_list()
        else:
            postingsList = index[term].traverse_skips()
        return postingsList
        #return self.indexer.get_postings_list(term,isSkipPosting)

    def _output_formatter(self, op):
        """ This formats the result in the required format.
            Do NOT change."""
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        """ This function reads & indexes the corpus. After creating the inverted index,
            it sorts the index by the terms, add skip pointers, and calculates the tf-idf scores.
            Already implemented, but you can modify the orchestration, as you seem fit."""
        count = 0
        with open(corpus, 'r',encoding = "utf-8") as fp:
            for line in tqdm(fp.readlines()):
                doc_id, document = self.preprocessor.get_doc_id(line)
                tokenized_document = self.preprocessor.tokenizer(document)
                self.indexer.generate_inverted_index(doc_id, tokenized_document)
                count += 1
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf(count)

    def sanity_checker(self, command):
        """ DO NOT MODIFY THIS. THIS IS USED BY THE GRADER. """

        index = self.indexer.get_index()
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.indexer)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].start_node),
                "node_type": str(type(index[kw].start_node)),
                "node_value": str(index[kw].start_node.value),
                "command_result": eval(command) if "." in command else ""}

    def run_queries(self, query_list, random_command):
        """ DO NOT CHANGE THE output_dict definition"""
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)
                       }
        #q_list = []
        for query in tqdm(query_list):
        #for query in q_list:
            """ Run each query against the index. You should do the following for each query:
                1. Pre-process & tokenize the query.
                2. For each query token, get the postings list & postings list with skip pointers.
                3. Get the DAAT AND query results & number of comparisons with & without skip pointers.
                4. Get the DAAT AND query results & number of comparisons with & without skip pointers, 
                    along with sorting by tf-idf scores."""
            #raise NotImplementedError

            input_term_arr = []  # Tokenized query. To be implemented.
            input_term_arr = self.preprocessor.tokenizer(query)

            for term in input_term_arr:
                postings, skip_postings = None, None
                postings = self._get_postings(term,False)
                #print("Postings list for the term: "+str(term))
                #print(postings)
                skip_postings = self._get_postings(term,True)
                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""

                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings

            and_op_no_skip, and_op_skip, and_op_no_skip_sorted, and_op_skip_sorted = None, None, None, None
            and_comparisons_no_skip, and_comparisons_skip, \
                and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = None, None, None, None
            """ Implement logic to populate initialize the above variables.
                The below code formats your result to the required format.
                To be implemented."""
            and_op_no_skip, and_comparisons_no_skip = self._daat_and(input_term_arr,False,False)
            and_op_skip, and_comparisons_skip = self._daat_and(input_term_arr,True,False)
            and_op_no_skip_sorted,and_comparisons_no_skip_sorted = self._daat_and(input_term_arr,False,True)
            and_op_skip_sorted,and_comparisons_skip_sorted = self._daat_and(input_term_arr,True,True)

            and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
            and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
            and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(and_op_no_skip_sorted)
            and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

            output_dict['daatAndTfIdf'][query.strip()] = {}
            output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]

    """ Running the queries against the pre-loaded index. """
    output_dict = runner.run_queries(queries, random_command)

    """ Dumping the results to a JSON file. """
    with open(output_location, 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    """ Driver code for the project, which defines the global variables.
        Do NOT change it."""

    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    parser.add_argument("--username", type=str,
                        help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
                             "DO NOT pass incorrect value here")

    argv = parser.parse_args()

    corpus = argv.corpus
    output_location = argv.output_location
    username_hash = hashlib.md5(argv.username.encode()).hexdigest()

    """ Initialize the project runner"""
    runner = ProjectRunner()

    """ Index the documents from beforehand. When the API endpoint is hit, queries are run against 
        this pre-loaded in memory index. """
    runner.run_indexer(corpus)
    #runner.run_queries([],"fsd")
    app.run(host="0.0.0.0", port=9999)
