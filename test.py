import json
with open('./indiv_ranking_rev.json') as f:
    data = json.load(f)

print(data['5291'])

r = "Mech #8136"
guh  =(r.split('#')[1])
print(data[guh])