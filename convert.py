import base64
import zlib

def deconvert(s):
    b = base64.b64decode(s.encode('ascii'))
    return zlib.decompress(b).decode('utf-8')

def convert(s):
	b = zlib.compress(s.encode('utf-8'))
	return base64.b64encode(b).decode('ascii')

if __name__ == '__main__':
	print "EXAMPLE:"
	data = """"eJx9UktPg0AQvpPwC3qZkBLlVurJNiRiQCEpjxDEmJpMVBYhKawR1L/vbnmtWMqJYeZ7zXBD3nIKNMtkqSYNKIkbxQ/mDm0/MRCFClGRJVkqMkhJVlQkBQx21jARRoEXxnApS8CeI1X7yVBPzKmMSwNyqEmPYLwVbQbuv3RTymW4vFfaliYInhAyVEGwi9h1Fnt9pW+vr8ox5qPrt03ExX5VggCWpcj2wKLVRQNf3LYGDYWXb1qk8PFJXw+krOGnaHJoclJCUTGwGTvqmY09xU7gO4FnwztlXLZvuXcJr2cjDQgWa3jn7jYiuI0pDPfuZ50wo3zVkxv8nxF88loXj83q6al5/tFch+BGxtOftTSRW8/u5ah9Qm7dL6OzJ/zO6jPireujb3o24nZA/wL0gNga"""
	print "DATA:", data
	data_deconvert = deconvert(data)
	print "data_deconvert =", data_deconvert
	print "="* 120
	print "data_convert =", convert(data_deconvert)