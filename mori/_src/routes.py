import ast, sys, json, glob, os
def V(n):
    if isinstance(n, ast.Str): return n.s
    if isinstance(n, ast.NameConstant): return n.value
    if isinstance(n, ast.Constant): return n.value
    return None
base = sys.argv[1]
out = []
for f in [base + '/server.py'] + sorted(glob.glob(base + '/routes/*.py')):
    tree = ast.parse(open(f, encoding='utf-8').read())
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
        for d in node.decorator_list:
            if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr in ('get','post','put','patch','delete')): continue
            if not (isinstance(d.func.value, ast.Name) and d.func.value.id in ('app','router')): continue
            if not d.args or not isinstance(V(d.args[0]), str): continue
            kw = {k.arg: k.value for k in d.keywords}
            tags = [V(e) for e in kw['tags'].elts] if 'tags' in kw and isinstance(kw['tags'], ast.List) else []
            schema = not ('include_in_schema' in kw and V(kw['include_in_schema']) is False)
            summary = V(kw['summary']) if 'summary' in kw and isinstance(V(kw['summary']), str) else ''
            doc = (ast.get_docstring(node) or '').strip().splitlines()
            out.append(dict(m=d.func.attr.upper(), p=V(d.args[0]), tags=tags, schema=schema, summary=summary, doc=doc[0] if doc else '', fn=node.name, file=os.path.basename(f)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'routes.json'),'w'), ensure_ascii=False, indent=0)
from collections import Counter
s=[r for r in out if r['schema']]
print('total', len(out), 'in schema', len(s), 'no tag', sum(1 for r in s if not r['tags']))
print(Counter(r['tags'][0] if r['tags'] else '-' for r in s))
print('with summary/doc', sum(1 for r in s if r['summary'] or r['doc']))
