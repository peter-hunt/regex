from regex import compile, fullmatch, match

pattern = r'12?'
str_1 = '1'
str_2 = '12'

print(compile(pattern))
print(compile(pattern).nodes)
print(fullmatch(pattern, str_1))
print(fullmatch(pattern, str_2))
print(match(pattern, str_1))
print(match(pattern, str_2))
