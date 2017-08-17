import numpy as np

try:
    b = np.sum(np.zeros((3,3)))
    a = 1.0/b
except ZeroDivisionError:
    a = 2
    print("tat")
print(a)