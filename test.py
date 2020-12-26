from regex import compile, match

pattern = r'^\w$'

print(compile(pattern))
print(compile(pattern).nodes)
print(match(pattern, '1'))
print(match(pattern, '12'))
