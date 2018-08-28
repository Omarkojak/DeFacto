# import os
# from six.moves import urllib


# REPO_URL = "https://raw.githubusercontent.com/SmartDataAnalytics/FactBench/master/"

# TRAIN_TRIPLES_PATH = "train/correct/award/award_00000.ttl"
# TRAIN_TRIPLES_URL = REPO_URL + TRAIN_TRIPLES_PATH


# def fetch_train_triples(url=TRAIN_TRIPLES_URL, train_path=TRAIN_TRIPLES_PATH):
#     if not os.path.isdir(train_path):
# 	    os.makedirs(train_path)
#     urllib.request.urlretrieve(url, train_path)

# fetch_train_triples()

import os
import rdflib

# Path to FactBench Triple files
TRAIN_TRIPLES_CORRECT = "./train/correct/"
# TRAIN_TRIPLES_WRONG = "./train/wrong/"

# FactBench Relations
relations = ["award", "birth", "death", "foundationPlace", "leader", "nbateam",
"publicationDate", "spouse", "starring", "subsidiary"]

# Triples in FactBench files
triples = []


# This method reads all the FactBench correct triples.
def read_triples_files():
    for relation in relations:
        i = 0
        while i <= 150:
            filepath = "{}/{}/{}_{:05d}.ttl".format(TRAIN_TRIPLES_CORRECT, relation, relation, i)
            if not os.path.isfile(filepath):
                break
            extract_triples(filepath, relation)
            i += 2

# This method extract triples from a file
def extract_triples(filepath, relation):
    triples_file = open(filepath, 'r')
    file_text = triples_file.read()

    # construct rdf graph for the file to extract the resources
    g=rdflib.Graph()
    g.parse(filepath, format='turtle')

    term1 = ""  # either the subject resource link or the object resource link
    term2 = ""  # either the subject resource link or the object resource link
    term1_labels = []  # term1 other similiare labels
    term2_labels = []  # term2 other similar labels
    predicate_from = ""  # timespan/timepoint from part 
    predicate_to = ""  # timespan/timepoint to part 
    subject_num = -1  # indicator which of term1 & term2 is the subject

    for t1,t2,t3 in g:
        term_type = ""
        t1 = str(t1)
        t2 = str(t2)
        t3 = str(t3)

        # This part get whether this triple is an explanation for the predicate or if it's
        # an indicator for the subject or it neither
        if relation == "award":
            term_type = handle_award_triple(t2)
        if relation == "birth":
            term_type = handle_birth_triple(t2)
        if relation == "death":
            term_type = handle_death_triple(t2)
        if relation == "foundationPlace":
            term_type = handle_foundation_triple(t2)
        if relation == "leader":
            term_type = handle_leader_triple(t2)
        if relation == "nbateam":
            term_type = handle_nbateam_triple(t2)
        if relation == "publicationDate":
            term_type = handle_publication_triple(t2)
        if relation == "spouse":
            term_type = handle_spouse_triple(t2)
        if relation == "starring":
            term_type = handle_starring_triple(t2)
        if relation == "subsidiary":
            term_type = handle_subsidiary_triple(t2)


        # This part to extract the timespan/timepoint details
        if term_type == "predicate":
            t2_end = t2[len(t2)-4:len(t2)]
            if t2_end == "from":
                predicate_from = t3
            elif t2_end[2:4] == "to":
                predicate_to = t3
        else:
            # This part to add the labels into the list with its language

            if t3.find("http") == -1:
                index = file_text.find('"'+t3+'"')
                if t1 == term1:
                    term1_labels.append((t3, file_text[index+len(t3)+3:index+len(t3)+5]))
                elif t1 == term2:
                    term2_labels.append((t3, file_text[index+len(t3)+3:index+len(t3)+5]))
                elif term1 == "":
                    term1 = t1
                    term1_labels.append((t3, file_text[index+len(t3)+3:index+len(t3)+5]))
                else:
                    term2 = t1
                    term2_labels.append((t3, file_text[index+len(t3)+3:index+len(t3)+5]))

            if term_type == "subject":
                if term1 == t1:
                    subject_num = 1
                else:
                    subject_num = 2
    

    # Loop for generates curtasian product between all different
    # labels for the subject and object
    for t1 in term1_labels:
        for t2 in term2_labels:
            # this condition check if the subject and object have the same language
            if t1[1] == t2[1]:
                # for testing if langauges problem is solved try with award 00000
                # if t1[1] == 'en':
                #     print("hello", t1[0], relation, t2[0], t1[1])
                if subject_num == 1:
                    triples.append((t1[0], relation, t2[0], t1[1]))
                else:
                    triples.append((t2[0], relation, t1[0], t1[1]))

    # Test lines
    # print(term1, term2, predicate_from, predicate_to, subject_num)
    # print(term1_labels)
    # print(term2_labels)
    # print("\n\n")
    # print(triples)
    # print(s,p,o, file=open("test0.txt", "a"))
    # print('\n', file=open("test0.txt", "a"))


# This method classify whether the current triple for an award relation
# is describing a subject or a predicate or neither
def handle_award_triple(t2):
    t2_end = t2[len(t2)-5:len(t2)]
    type = "term"

    if t2_end == "award" or t2_end[1:5] == "from" or t2_end[3:5] == "to":
        type = "predicate"
    
    if t2_end == "Award":
        type = "subject"
    return type

# This method classify whether the current triple for a birth relation
# is describing a subject or a predicate or neither
def handle_birth_triple(t2):
    t2_end = t2[len(t2)-10:len(t2)]
    type = "term"

    if t2_end == "birthPlace" or t2_end[6:10] == "from" or t2_end[8:10] == "to":
        type = "predicate"
    
    if t2_end[5:10] == "birth":
        type = "subject"
    return type

# This method classify whether the current triple for a death relation
# is describing a subject or a predicate or neither
def handle_death_triple(t2):
    t2_end = t2[len(t2)-10:len(t2)]
    type = "term"

    if t2_end == "deathPlace" or t2_end[6:10] == "from" or t2_end[8:10] == "to":
        type = "predicate"
    
    if t2_end[5:10] == "death":
        type = "subject"
    return type

# This method classify whether the current triple for a foundation place relation
# is describing a subject or a predicate or neither
def handle_foundation_triple(t2):
    t2_end = t2[len(t2)-15:len(t2)]
    type = "term"

    if t2_end == "foundationPlace" or t2_end[11:15] == "from" or t2_end[13:15] == "to":
        type = "predicate"
    
    if t2_end[5:15] == "foundation":
        type = "subject"
    return type

# This method classify whether the current triple for a leader relation
# is describing a subject or a predicate or neither
def handle_leader_triple(t2):
    t2_end = t2[len(t2)-8:len(t2)]
    type = "term"

    if t2_end[2:8] == "office" or t2_end[4:8] == "from" or t2_end[6:8] == "to":
        type = "predicate"
    
    if t2_end == "inOffice":
        type = "subject"
    return type

# This method classify whether the current triple for a nbateam relation
# is describing a subject or a predicate or neither
def handle_nbateam_triple(t2):
    t2_end = t2[len(t2)-10:len(t2)]
    type = "term"

    if t2_end[6:10] == "team" or t2_end[6:10] == "from" or t2_end[8:10] == "to":
        type = "predicate"
    
    if t2_end == "playedTeam":
        type = "subject"
    return type

# This method classify whether the current triple for a publicationDate relation
# is describing a subject or a predicate or neither
def handle_publication_triple(t2):
    t2_end = t2[len(t2)-11:len(t2)]
    type = "term"

    if t2_end[5:11] == "author" or t2_end[7:11] == "from" or t2_end[9:11] == "to":
        type = "predicate"
    
    if t2_end == "publication":
        type = "subject"
    return type

# This method classify whether the current triple for a spouse relation
# is describing a subject or a predicate or neither
def handle_spouse_triple(t2):
    t2_end = t2[len(t2)-8:len(t2)]
    type = "term"

    if t2_end[2:8] == "spouse" or t2_end[4:8] == "from" or t2_end[6:8] == "to":
        type = "predicate"
    
    if t2_end == "marriage":
        type = "subject"
    return type

# This method classify whether the current triple for a starring relation
# is describing a subject or a predicate or neither
def handle_starring_triple(t2):
    t2_end = t2[len(t2)-10:len(t2)]
    type = "term"

    if t2_end[2:10] == "starring" or t2_end[6:10] == "from" or t2_end[8:10] == "to":
        type = "predicate"
    
    if t2_end == "isStarring":
        type = "subject"
    return type

# This method classify whether the current triple for a subsidiary relation
# is describing a subject or a predicate or neither
def handle_subsidiary_triple(t2):
    t2_end = t2[len(t2)-11:len(t2)]
    type = "term"

    if t2_end[1:11] == "subsidiary" or t2_end[7:11] == "from" or t2_end[9:11] == "to":
        type = "predicate"
    
    if t2_end == "acquisition":
        type = "subject"
    return type



# read_triples_files()
# print(len(triples))

subscription_key = "0ccd1e12a0be4bce8cb5a3c7f8771f81"
assert subscription_key
search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
search_term = ""

import requests

headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
params  = {"q": search_term, "textDecorations":True, "textFormat":"HTML"}
response = requests.get(search_url, headers=headers, params=params)
print(response.status_code)
print(response.json())
# response.raise_for_status()
# search_results = response.json()
# print(search_results)



## Wikipedia Module
# import wikipediaapi
# wiki_wiki = wikipediaapi.Wikipedia('en')
# page_py = wiki_wiki.page('Python_(programming_language)')
# print(page_py.text)

# from pysolr import *
# solr = Solr('http://localhost:8080/solr/core0/', timeout=10)
# solr.add([
#     {
#         "id": "1",
#         "title": page_py.text,
#     }
# ])



