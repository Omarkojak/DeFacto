
import json
import requests

kg_token = "AIzaSyCQ2nh5Yu7rzWP0Ix5hzmIMiP6dcbLBxFU"
kg_endpoint = "https://kgsearch.googleapis.com/v1/entities:search"

# This function for finding the name equivilant to google knowledge graph id
def find_entity(id):
	params  = {
		'ids': id,
		'limit': 1,
		'indent': True,
		'key': kg_token,
	}
	response = requests.get(kg_endpoint, headers={}, params=params)
	if response.status_code == 200:
		body = json.loads(response.content.decode('utf-8'))
		if len(body["itemListElement"]) == 1:
			if("name" in body["itemListElement"][0]["result"]):
				return body["itemListElement"][0]["result"]["name"]
			else:
				return "None"
		else:
			return "None"
	else:
		return "None"


# This function to save mappings between subject/objects ids and names
# # ## line 1584, 4803, 6921, 13051 problem institution file
def save_mappings(filepath):
	with open(filepath) as fp:
		line = fp.readline()
		cnt = 1
		while line:
			# if cnt == 1584 or cnt == 4803 or cnt == 6921 or cnt == 13051:
			# 	line = fp.readline()
			# 	cnt += 1
			# 	continue

			text = json.loads(line.strip())

			# if cnt == 1:
			# 	print(text)

			subject_name = find_entity(text["sub"])
			print(text["sub"])
			object_name = find_entity(text["obj"])
			print(text["obj"])
			mapping = text["sub"] + " " + subject_name + "\n" + text["obj"] + " " + object_name + "\n"
			# mapping = text["sub"] + " " + subject_name + "\n"
			mappings_file = open("./mappings5.txt", 'a')
			mappings_file.write(mapping)
			mappings_file.close()

			line = fp.readline()
			cnt += 1

# save_mappings("./relation-extraction-corpus/20130403-institution.json")
# save_mappings("./relation-extraction-corpus/20130403-place_of_birth.json")
# save_mappings("./relation-extraction-corpus/20131104-date_of_birth.json")
# save_mappings("./relation-extraction-corpus/20131104-education-degree.json")
# save_mappings("./relation-extraction-corpus/20131104-place_of_death.json")


# This function to check if no subject or object id was missed to be mapped 
def check_mappings(filepath):
	with open(filepath) as fp:
		mappings_file = open("./mappings2.txt", 'r')
		line = fp.readline()
		cnt = 1
		while line:
			# if cnt == 1584 or cnt == 4803 or cnt == 6921 or cnt == 13051:
			# 	line = fp.readline()
			# 	cnt += 1
			# 	continue

			text = json.loads(line.strip())


			mapping_line1 = mappings_file.readline().split()
			mapping_line2 = mappings_file.readline().split()

			if cnt == 1:
				print(text)
				print(mapping_line1[0], mapping_line2[0])

			if mapping_line1[0] != text["sub"] or mapping_line2[0] != text["obj"]:
				print(cnt, mapping_line1[0], mapping_line2[0])
				break;

			line = fp.readline()
			cnt += 1

# check_mappings("./relation-extraction-corpus/20130403-institution.json")
# check_mappings("./relation-extraction-corpus/20130403-place_of_birth.json")

# nb_clf = Pipeline([('vect', DictVectorizer()),('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, max_iter=5, random_state=42))])
