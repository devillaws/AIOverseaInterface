from collections import deque

# 定义队列
my_queue = deque([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# 取出最后5位数
b = 11
for i in range(1, 5):
    num = my_queue[-i]
    b -= num
    print(b)

