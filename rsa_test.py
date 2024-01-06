import rsa

public_key, private_key = rsa.newkeys(1024)

# with open("public.pem", "wb") as f:
#     f.write(public_key.save_pkcs1("PEM"))

# with open("private.pem", "wb") as f:
#     f.write(private_key.save_pkcs1("PEM"))

message = "This is the non-encrypted message"

encrypted_msg = rsa.encrypt(message.encode(), public_key)
print(encrypted_msg)

decrypted_msg = rsa.decrypt(encrypted_msg, private_key)
print(decrypted_msg.decode())

new_message = "this is a signed message"


signature = rsa.sign(new_message.encode(), private_key, "SHA-256")

print(rsa.verify(new_message.encode(), signature, public_key))