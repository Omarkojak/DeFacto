import json
import spacy
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Get a subject or object from mappings line 
def get_resource(line):
    array = line.split()
    resource = ""
    i = 1
    while i < len(array):
        resource += " " + array[i]
        i += 1
    return resource

# This function extract labels from instance json
def find_label(judgments):
    yes_labels = 0
    no_labels = 0
    for judgment in judgments:
        if judgment["judgment"] == "yes":
            yes_labels += 1
        elif judgment["judgment"] == "no":
            no_labels += 1
    
    if yes_labels >= 0.8 * len(judgments):
        return 0
    if no_labels >= 0.8 * len(judgments):
        return 1
    return 2


# Has NER feature part
def has_NER(evidence, nlp):
	# Load English tokenizer, tagger, parser, NER and word vectors

	# Process whole documents
	doc = nlp(evidence)

	if len(doc.ents) > 0:
		return 1
	else:
		return 0


# Has predicate feature
def has_predicate(evidence, predicate):

    keywords = []

    if predicate == "birth-place" or predicate == "birth-date":
        keywords = ["born", "birth"]
    
    if predicate == "institution":
        keywords = ["graduated", "graduate", "study", "studies", "studied", "eduacted", "taught", "student", "joins", 
        "joined", "joining", "attends", "attended", "enter", "enters", "entered", "enrolls", "enrolled"]
    
    if predicate == "education-degree":
        keywords = ["degree", "receives", "received", "receiving", "graduates", "graduated", "graduating"]
    
    if predicate == "death-place":
        keywords = ["die", "dies", "died", "passed away", "death"]

    i = 0
    while i < len(keywords):
        if evidence.find(keywords[i]) != -1:
            return 1
        i += 1
    
    return 0

# Has subject feature
def has_subject(evidence, url, subject):
    names = subject.split()
    firstName = names[0]
    lastName = names[len(names) - 1]
    if evidence.find(subject) != -1 or evidence.find(firstName) != -1 or evidence.find(lastName) != -1 or url.find(firstName) != -1 or url.find(lastName) != -1:
        return 1
    else:
        return 0

# has object feature
def has_object(evidence, object):
    if evidence.find(object) != -1:
        return 1
    else:
        return 0

# This function to find the has object feature but for educational degrees,
# as every educational degree have alot of abbreviations

def has_object_degree(evidence, object):
    abbreviations = []
    
    if object.find("Bachelor of Science") != -1:
        abbreviations = ["Bc.", "B.S.", "BS", "B Sc", "B.Sc.", "BSc", "S.B", "SB", "Sc.B.", "S.B."]
    
    if object.find("Doctor of Philosophy") != -1:
        abbreviations = ["Ph.D.", "PhD", "D.Phil.", "DPhil", "Dr. phil."]
    
    if object.find("Bachelor of Arts") != -1:
        abbreviations = ["B.A.", "BA", "A.B.", "AB", "BA degree"]
    
    if object.find("Bachelor of Engineering") != -1:
        abbreviations = ["BE", "BEng", "B.Eng."]
    
    if object.find("master's degree") != -1:
        abbreviations = ["master degree", "masters degree", "master"]
    
    if object.find("Bachelor of Fine Arts") != -1:
        abbreviations = ["BFA"]
    
    if object.find("Master of Science") != -1:
        abbreviations = ["M.S.", "MSc", "MS", "M.Sc.", "M.Sci.", "MSci", "S.M.", "Sc.M.", "Sci.M."]

    if object.find("honorary degree") != -1:
        abbreviations = ["honoris causa", "ad honorem", "h.c."]

    if object.find("Master of Arts") != -1:
        abbreviations = ["MA", "M.A.", "A.M.", "AM"]
    
    if object.find("Bachelor of Business Administration") != -1:
        abbreviations = ["BBA", "B.B.A.", "BSBA"]
    
    if object.find("Juris Doctor") != -1:
        abbreviations = ["JD", "J.D.", "Doctor of Jurisprudence", "D.Jur.", "DJur"]

    if object.find("Master of Business Administration") != -1:
        abbreviations = ["MBA", "M.B.A.", "Masters of Business Administration", "Master's of Business Administration"]
    
    if object.find("Bachelor of Laws") != -1:
        abbreviations = ["LL.B.", "LLB", "B.L"]
    
    if object.find("Doctor of Letters") != -1:
        abbreviations = ["Doctor of Literature", "D.Litt.", "Litt.D.", "D. Lit.", "Lit. D."]
    
    if object.find("Doctor of Science") != -1:
        abbreviations = ["Sc.D.", "Sc. D.", "D.Sc.", "D. Sc.", "S.D.", "D.S.", "Dr.Sc.", "Dr. Sc."]
    
    if object.find("Doctor of Divinity") != -1:
        abbreviations = ["DD", "D.D.", "D. D.", "D. Div."]
    
    if object.find("Doctorate of Humane Letters") != -1:
        abbreviations = ["D. H. L.", "D.H.L.", "L. H. D.", "L.H.D.", "Litterarum humanarum doctor"]

    if object.find("Master of Fine Arts") != -1:
        abbreviations = ["MFA", "M.F.A."]

    if object.find("Doctor of Medicine") != -1:
        abbreviations = ["Medical doctor", "M.D.", "MD", "M. D.", "Doctorate of Medicine"]
    
    if object.find("Master of Divinity") != -1:
        abbreviations = ["Masters of Divinity", "magister divinitatis", "M.Div.", "MDiv"]
    
    if object.find("Doctor of Juridical Science") != -1:
        abbreviations = ["Doctor of the Science of Law", "Scientiae Juridicae Doctor" , "Doctor of Laws", "J.S.D.", "JSD", "S.J.D.", "SJD"]

    if object.find("Master of Public Administration") != -1:
        abbreviations = ["MPA", "M.P.A."]

    if object.find("Bachelor of Theology") != -1:
        abbreviations = ["B.Th."]
    
    if object.find("Master of Laws") != -1:
        abbreviations = ["LL.M", "LLM"]

    if object.find("Master of Philosophy") != -1:
        abbreviations = ["MPhil", "M.Phil.", "M.Phil"]

    abbreviations.append(object)

    i = 0
    while i <len(abbreviations):
        if evidence.find(abbreviations[i]) != -1:
            return 1
        i += 1
    return 0


# Feature indicating the lemmatization of subject exist in the evidence or not
def has_lemma_s(evidence, subject):
    lemmatizer = WordNetLemmatizer()
    lemma_s = lemmatizer.lemmatize(subject)
    if evidence.find(lemma_s) != -1:
        return 1
    else:
        return 0

# Feature indicating the lemmatization of object exist in the evidence or not
def has_lemma_o(evidence, object):
    lemmatizer = WordNetLemmatizer()
    lemma_o = lemmatizer.lemmatize(object)
    if evidence.find(lemma_o) != -1:
        return 1
    else:
        return 0


def sim_subject(evidence, subject, nlp):
    subject = nlp(subject)
    words = evidence.split()
    max_sim_subject = 0
    
    for word in words:    
        sim_subject = subject.similarity(nlp(word))
        max_sim_subject = max(max_sim_subject, sim_subject)
    
    return max_sim_subject


# This function generate features and labels for each instance in the dataset

def generate_features_labels(claims_path, mappings_path, predicate, output_path):
    nlp = spacy.load('en_core_web_lg')

    claims_file = open(claims_path, 'r')
    mappings_file = open(mappings_path, 'r')
    output_file = open(output_path, 'a')
    cnt = 1
    line = claims_file.readline()

    while line:
        # if cnt == 1584 or cnt == 4803 or cnt == 6921 or cnt == 13051:
        #     line = claims_file.readline()
        #     cnt += 1
        #     continue
        
        print(cnt)
        instance = json.loads(line.strip())

        subject = get_resource(mappings_file.readline())
        object = instance["obj"]
        if predicate != "birth-date":
            object = get_resource(mappings_file.readline())
        
        instance_label = find_label(instance["judgments"])
        if subject == "None" or object == "None":
            instance_label = 2

        for evidence in instance["evidences"]:
            snippet = evidence["snippet"]
            f1 = has_NER(snippet, nlp)
            f2 = has_subject(snippet, evidence["url"], subject)
            f3 = has_predicate(snippet, predicate)

            f4 = has_object(snippet, object)
            if predicate == "education-degree":
                f4 = has_object_degree(snippet, object)

            f5 = has_lemma_s(snippet, subject)
            f6 = has_lemma_o(snippet, object)
            f7 = sim_subject(snippet, subject, nlp)

            instance_features = [f1, f2, f3, f4, f5, f6, f7]
            i = 0
            while i < 7:
                output_file.write(str(instance_features[i]) + " ")
                i += 1
            
            output_file.write(str(instance_label))
            output_file.write("\n")

        line = claims_file.readline()
        cnt += 1
    
    mappings_file.close()
    claims_file.close()
    output_file.close()
    # return features, labels


def model(feature_labels_path):

    file = open(feature_labels_path, 'r')
    features = []
    labels = []

    line = file.readline()
    cnt = 1
    class0 = 0
    class1 = 0
    class2 = 0
    while(line):

        features_labels = line.split()

        features.append([int(features_labels[0]), int(features_labels[1]), int(features_labels[2]), 
        int(features_labels[3]), int(features_labels[4]), int(features_labels[5]), float(features_labels[6])])
        label = int(features_labels[7])
        labels.append(label)

        if label == 0:
            class0 += 1
        if label == 1:
            class1 += 1
        if label == 2:
            class2 += 1
        
        line = file.readline()
        cnt += 1

    print(class0, class1, class2)
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.33, random_state=32)

    clf1 = SVC()
    clf2 = MultinomialNB()
    clf3 = DecisionTreeClassifier()

    clf1.fit(X_train, y_train)
    clf2.fit(X_train, y_train)
    clf3.fit(X_train, y_train)

    svm_predections = clf1.predict(X_test)
    nb_predections = clf2.predict(X_test)
    decision_trees_predections = clf3.predict(X_test)

    target_names = ['class 0', 'class 1', 'class 2']
    print("SVM")
    print(classification_report(y_test, svm_predections, target_names=target_names))
    print("\n")

    print("NB")
    print(classification_report(y_test, nb_predections, target_names=target_names))
    print("\n")

    print("Decision Trees")
    print(classification_report(y_test, decision_trees_predections, target_names=target_names))
    print("\n")
    
    print(confusion_matrix(y_test, svm_predections))
    print(confusion_matrix(y_test, nb_predections))
    print(confusion_matrix(y_test, decision_trees_predections))

    i = 0
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0

    while i < len(y_test):
        if svm_predections[i] == y_test[i]:
            cnt1 += 1

        if nb_predections[i] == y_test[i]:
            cnt2 += 1

        if decision_trees_predections[i] == y_test[i]:
            cnt3 += 1

        i += 1
    print(cnt1, len(y_test))
    print(cnt2, len(y_test))
    print(cnt3, len(y_test))




# This method is for generating features and labels to each predicate 
def generate():
    claims_path = "./relation-extraction-corpus/20131104-date_of_birth.json"
    mappings_path = "./mappings/birth_date_mappings.txt"
    # birth-place birth-date institution education-degree death-place
    predicate = "birth-date"
    output_path = "./features-labels/birth_date_v1.txt"
    generate_features_labels(claims_path, mappings_path, predicate, output_path)

if __name__ == "__main__":
    # generate()
    model("./features-labels/education_degree_v1.txt")


