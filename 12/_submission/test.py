def bit(x, i):
    n = 15
    while n > i:
        # print(x - twoToThe[n])
        if x >= twoToThe[n]:
            x = x - twoToThe[n]
            # print(1, end="")
        # else:
        #     print(0, end="")
        n = n - 1
    return x >= twoToThe[n]

twoToThe = []
for i in range(16):
    twoToThe.append(2 ** i)

for i in range(16):
    print(f"{i}:{bit(13, i)}", end=", ")
# print(bit(13,0))