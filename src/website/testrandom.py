import binascii, hashlib
def sha256(string):
    hasher = hashlib.sha256()
    hasher.update(SECRET_KEY)
    return binascii.hexlify(hasher.digest())
with open("/dev/urandom", 'rb') as f:
    SECRET_KEY = binascii.hexlify(f.read(32))
#SECRET_KEY = "bd1437a6beb38740dab23ee1cf652b42b615466bd221e3bd25aec2267b70b67e"
HASH = sha256(SECRET_KEY)

print "RANDOM " + SECRET_KEY
print "HASH   " + HASH
print "    ", hex(int(SECRET_KEY, 16) ^ int(HASH, 16))
#hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000)
#hashlib.pbkdf2_hmac("sha256", "password", "ba13a9b1c0d8e06281151f184cb939b85e5daa84b143b330e74d609ea26843a2", 10000, dklen=None)

