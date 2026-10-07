import os

p = r'D:\Zcode\裂缝检测'
n = 0
for root, dirs, files in os.walk(p):
    for f in files:
        n += 1
        print(os.path.join(root, f))
print('TOTAL FILES:', n)
