import numpy as np

b = np.array([[1,2],[3,4],[5,6]])

filter_arr = []
for i in b:
     if(i[0] + i[1] < 5):
             filter_arr.append(True)
     else:
            filter_arr.append(False)

a = b[filter_arr]

print(a)
print(a.shape)