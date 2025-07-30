
str1 = "111233344455"

def remove_num(s):
    result = []
    for char in s:
        if len(result) >= 2 and result[-1] == char and result[-2] == char:
            continue
        result.append(char)
    return "".join(result)

print(remove_num(str1))