"""Getting file names for each library: model names, material names, scene names"""

from tdw.librarian import ModelLibrarian
import json

# Gets different Model Libraries
model_libraries = ModelLibrarian.get_library_filenames()
with open('models.txt', 'w') as f:
    for item in model_libraries:
        f.write(f"Model Library: {item} \n")

# Parsing models_full.json into Python
models_full = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/tdw/metadata_libraries/models_full.json"
models_list = {'Model': 'Category'}
with open(models_full) as json_file:
    data = json.load(json_file)

# Model is the key, with many, many values (including wcategory)
for model in data["records"]:
    models_list[model] = data["records"][model]["wcategory"]

# Writing list of models to csv
with open('models_list.csv', 'w') as f:
    for key in models_list.keys():
        f.write("%s,%s\n" % (key, models_list[key]))


# Gets different materials/textures - high quality 2048x2048
materials_json = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/tdw/metadata_libraries/materials_high.json"
materials_list = {'Material': ['Type', 'URL']}
with open(materials_json) as json_file:
    data = json.load(json_file)

for material in data["records"]:
    materials_list[material] = [data["records"][material]["type"],
                                data["records"][material]["urls"]["Darwin"]]

with open('materials_list.csv', 'w') as f:
    for key in materials_list.keys():
        f.write("%s,%s,%s\n" % (key, materials_list[key][0], materials_list[key][1]))


# Gets different scenes
scenes_json = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/tdw/metadata_libraries/scenes.json"
scenes_list = {'Scene': ['Description', 'HDRI', 'Location']}
with open(scenes_json) as json_file:
    data = json.load(json_file)

for scene in data["records"]:
    scenes_list[scene] = [data["records"][scene]["description"],
                          data["records"][scene]["hdri"],
                          data["records"][scene]["location"]]

with open('scenes_list.csv', 'w') as f:
    for key in scenes_list.keys():
        f.write("%s,%s,%s,%s\n" % (key, scenes_list[key][0], scenes_list[key][1], scenes_list[key][2]))



