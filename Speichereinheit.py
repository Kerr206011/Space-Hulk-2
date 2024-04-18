import json

# Data to be written to the JSON file
a = []
i = 0
while i < 9:
    a.append(1)
    a.append(3)
    i+=1
i = 0
while i<4:
    a.append(2)
    i+= 1
data = {
    "level": 1,
    "blipList" : a
}

# File path to save the JSON file
file_path = "level1.json"

# Writing data to the JSON file
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)

with open(file_path, 'r') as json_file:
    data = json.load(json_file)

# Printing loaded data
print(data)