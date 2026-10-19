baseline, current = {'code_queries': 0.9}, {'code_queries': 0.6}
print('investigate' if current['code_queries'] < baseline['code_queries']-0.1 else 'stable')
