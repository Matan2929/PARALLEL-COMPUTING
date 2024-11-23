from hashlib import md5
import sys

CHUNK = 1000000
part = int(sys.argv[1])
target = sys.argv[2]
start = (part - 1) * CHUNK
for i in range(CHUNK):
    number_bytes = str(i+start).zfill(10).encode('utf-8')
    md5_hashed = md5(number_bytes).hexdigest()
    if md5_hashed == target:
        print(f"{str(start + i).zfill(10)}")