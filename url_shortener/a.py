# a = 1
# st = ""
# while a < 10:
#     a = a + 1
#     st += f"{a} "
    


# a = 1
# for a in range(2, 10):
#     a = a + 1
#     st += f"{a} "

# a = 1
# for a in range(0, 20):
#     a = a + 1
#     if a > 1 and a < 11:
#         st += f"{a} "

# print(st)


import hashlib
m = hashlib.sha512()
hl = hashlib.pbkdf2_hmac('sha512',b'password', b'salt', 100,m.block_size) 
h2 = hashlib.pbkdf2_hmac('sha512',b'pass', b'salt', 100)
print (len(hl))
print (len(h2))
