from cryptography import fernet

def gen_secret():
	fernet_key = fernet.Fernet.generate_key()
	secret_file = open('secret', 'wb')
	secret_file.write(fernet_key)
	secret_file.close()
	return fernet_key

def get_secret():
	try:
		secret_file = open('secret', 'rb')
		fernet_key = secret_file.read()
		secret_file.close()
		if len(fernet_key) == 0:
			fernet_key = gen_secret()
	except:
		fernet_key = gen_secret()
	finally:
		return fernet_key

if __name__ == '__main__':
	print(get_secret())
