import json

x = {"name" : "tom",
     "Zug" : 1,
     "Regler" : 0.125}

y = json.dumps(x)

print(y)