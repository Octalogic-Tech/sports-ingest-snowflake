import json
d = json.load(open('race.json','rb'))
paths = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + [k])
    elif isinstance(o, list):
        if o and isinstance(o[0], dict):
            paths.append((p, len(o), list(o[0].keys())[:15]))
        for i, v in enumerate(o):
            walk(v, p + [str(i)])
walk(d, [])
for p, n, k in paths:
    print('/'.join(p), n, k)
