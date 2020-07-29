from nltk.corpus import wordnet
import csv

TDW_models_csv = "/Users/leonard/Desktop/coco/TDW_models_list.csv"
COCO_categories_csv = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/" \
                      "objects_changing_positions/COCO_categories.csv"
nouns = {x.name().split('.', 1)[0] for x in wordnet.all_synsets('n')}


def get_TDW_models():
    TDW_models = []
    with open(TDW_models_csv) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            TDW_models.append(row)

    return TDW_models


def get_COCO_categories():
    COCO_categories = []
    with open(COCO_categories_csv) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            COCO_categories.append(row[0])

    return COCO_categories


def get_hyponyms(synset):
    hyponyms = set()
    for hyponym in synset.hyponyms():
        hyponyms |= set(get_hyponyms(hyponym))
    # Return empty set if no hyponyms
    return hyponyms | set(synset.hyponyms())


def get_COCO_TDW_mapping():
    TDW_models = get_TDW_models()
    COCO_categories = get_COCO_categories()

    # Building dictionary mapping COCO objects to TDW models
    COCO_to_TDW = dict()
    for category in COCO_categories:
        # Dealing with categories that have no synsets
        # print("Category:", category)
        if len(wordnet.synsets(category)) == 0:
            # Just sets the last word of category as category
            category = category.split()[-1]
        # Getting all hyponyms (sub-words) of category
        # print("Synsets of Category:", wordnet.synsets(category))
        i = 0
        while (i + 1 < len(wordnet.synsets(category)) is not None and
               len(get_hyponyms(wordnet.synsets(category)[i])) == 0):
            i += 1
        cat_hyponyms = list(get_hyponyms(wordnet.synsets(category)[i]))
        cat_synonyms = wordnet.synsets(category)
        # print("Cat hyponyms:", cat_hyponyms)
        # print("Cat Synonyms:", cat_synonyms)
        cat_related = cat_synonyms + cat_hyponyms
        # print("All related words:", cat_related)

        # Getting all TDW model synsets:
        for model in TDW_models:
            # Dealing with unequal model columns
            if len(model) == 2:
                model_name = model[1]
                if len(wordnet.synsets((model[1]))) == 0:
                    # Just sets the last word of model as model
                    model_name = model[1].split()[-1]
                model_synsets = wordnet.synsets(model_name)
            elif len(model) == 3:
                model_name = model[2]
                if len(wordnet.synsets((model[2]))) == 0:
                    # Just sets the last word of model as model
                    model_name = model[2].split()[-1]
                model_synsets = wordnet.synsets(model_name)

            model_synsets = set(model_synsets)
            # print("Model synsets:", model_synsets)

            # Checking if TDW model is related to COCO category hyponyms
            if len(model_synsets & set(cat_related)) > 0:
                # How related is TDW model to COCO category?
                # print(list(model_synsets)[0])
                # print(list(cat_synonyms)[0])
                # print((list(model_synsets)[0]).path_similarity(list(cat_synonyms)[0]))
                if (model_name) in nouns and (category) in nouns and \
                        wordnet.synset('%s.n.01' % model_name).path_similarity(wordnet.synset('%s.n.01' % category)) \
                        is not None and \
                        wordnet.synset('%s.n.01' % model_name).path_similarity(
                            wordnet.synset('%s.n.01' % category)) >= 0.35:
                    if category in COCO_to_TDW:
                        # Converting set to list
                        COCO_to_TDW[category].append(model)
                    else:
                        COCO_to_TDW[category] = [model]

    return COCO_to_TDW


def write_to_csv():
    # Writing dictionary to CSV file
    COCO_to_TDW = get_COCO_TDW_mapping()
    with open('COCO_to_TDW.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in COCO_to_TDW.items():
            writer.writerow([key, value])


if __name__ == "__main__":
    mapping = get_COCO_TDW_mapping()
    print("Mappings")
    print(mapping['table'])
    print(mapping['chair'])
    print(mapping['bed'])
    print(mapping['couch'])
    print(mapping['bench'])
    write_to_csv()