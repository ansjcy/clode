import math

def inverse(u, v):
    """inverse(u:long, v:long):long
    Return the inverse of u mod v.
    """
    u3, v3 = int(u), int(v)
    u1, v1 = 1, 0
    while v3 > 0:
        q=divmod(u3, v3)[0]
        u1, v1 = v1, u1 - v1*q
        u3, v3 = v3, u3 - v3*q
    while u1<0:
        u1 = u1 + v
    return u1