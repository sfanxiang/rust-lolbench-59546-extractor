import json
import os
import sys

base_commit = sys.argv[1]

table = {}

for commit in os.listdir('output'):
    benches = {}
    for runner in os.listdir('output/%s' % commit):
        for bench in os.listdir('output/%s/%s/data-dir/run-plans' % (commit, runner)):
            with open('output/%s/%s/data-dir/run-plans/%s' % (commit, runner, bench), 'r') as f:
                content = json.load(f)
                key = content['key']['benchmark_key']
                binary_hash = content['contents']['Ok']
                benches[str(binary_hash)] = { 'key': key }
        for bench in os.listdir('output/%s/%s/data-dir/measurements' % (commit, runner)):
            with open('output/%s/%s/data-dir/measurements/%s' % (commit, runner, bench), 'r') as f:
                content = json.load(f)
                binary_hash = content['key']['binary_hash']
                mean_point_estimate = content['contents']['Ok']['nanoseconds']['Mean']['point_estimate']
                if 'mean_point_estimate' in benches[str(binary_hash)]:
                    raise Exception('Duplicate')
                benches[str(binary_hash)]['mean_point_estimate'] = mean_point_estimate

    benches2 = {}
    for (_, v) in benches.items():
        benches2[v['key']] = v['mean_point_estimate']
    table[commit] = benches2

commits = [base_commit] + [commit for commit in table.keys() if commit != base_commit]

output = '| Benchmark |'
for commit in commits:
    output += ' %s |' % commit
    if commit != base_commit:
        output += ' +% |'
output += '\n| --- |'
for commit in commits:
    output += ' --- |'
    if commit != base_commit:
        output += ' --- |'

incr = {}
for commit in commits:
    if commit != base_commit:
        incr[commit] = []

for (bench, _), _ in sorted(zip(table[commits[0]].items(), table[commits[-1]].items()), key=lambda v: v[1][1] / v[0][1]):
    output += '\n| `%s` |' % bench
    for commit in commits:
        output += ' %.5f |' % table[commit][bench]
        if commit != base_commit:
            incr_cur = (table[commit][bench] / table[base_commit][bench] - 1.0) * 100.0
            output += ' %s%% |' % ('{0:+.5f}'.format(incr_cur))
            incr[commit] += [incr_cur]
output += '\n| Mean +% |'

for commit in commits:
    if commit != base_commit:
        v = (sum(incr[commit]) / float(len(incr[commit])))
        output += ' | %s%% |' % ('{0:+.5f}'.format(v))
    else:
        output += ' |'
output += '\n'

print(output)
