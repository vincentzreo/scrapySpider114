
#生成器
def myGen():
    yield 1
    yield 2
    yield 3
    return 4

def myfun():
    return 4

# for data in myGen():
#     print(data)
#可以停止的函数
mygen = myGen()
print(next(mygen))
print(next(mygen))
print(next(mygen))
print(next(mygen))