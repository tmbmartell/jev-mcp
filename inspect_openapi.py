import json, re

d = json.load(open('/tmp/oa.json'))
sch = d['components']['schemas']

print("### SCHEMAS relevantes")
for n in sorted(sch):
    if any(k in n for k in ('Decisions', 'Question', 'Answer')):
        print("=" * 70)
        print("SCHEMA:", n)
        print(json.dumps(sch[n], indent=2)[:2500])

raw = json.dumps(d)
ids = sorted(set(re.findall(r'typesafe/[a-z0-9.\-]+', raw)))
print("\n### model ids typesafe no openapi:", ids)
