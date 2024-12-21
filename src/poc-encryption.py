import os
import base64
import json
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1


def generate_random_password(length=32):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz$&+#"
    return "".join(chars[os.urandom(1)[0] % len(chars)] for _ in range(length))


def rsa_encrypt_password(password, public_key_pem):
    rsa_key = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_password = cipher.encrypt(password.encode("utf-8"))
    return base64.b64encode(encrypted_password).decode("utf-8")


def aes_encrypt(plaintext, password):
    # Generate random IV and salt
    iv = os.urandom(16)
    salt = os.urandom(16)

    # Derive AES key via PBKDF2
    key = PBKDF2(password, salt, dkLen=16, count=1000, hmac_hash_module=SHA1)

    # PKCS#7 padding
    block_size = 16
    plaintext_bytes = plaintext.encode("utf-8")
    padding_len = block_size - (len(plaintext_bytes) % block_size)
    padded_plaintext = plaintext_bytes + bytes([padding_len]) * padding_len

    # AES-CBC encrypt
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(padded_plaintext)

    # Format: iv_hex::salt_hex::ciphertext_b64
    iv_hex = iv.hex()
    salt_hex = salt.hex()
    ciphertext_b64 = base64.b64encode(ciphertext).decode("utf-8")
    combined_str = f"{iv_hex}::{salt_hex}::{ciphertext_b64}"

    # Final output is base64-encoded combined_str
    return base64.b64encode(combined_str.encode("utf-8")).decode("utf-8")


def aes_decrypt(encrypted_value_b64, password):
    # Base64 decode the outer layer
    decoded = base64.b64decode(encrypted_value_b64).decode("utf-8")
    # Split by "::"
    iv_hex, salt_hex, ciphertext_b64 = decoded.split("::")

    # Convert iv and salt from hex
    iv = bytes.fromhex(iv_hex)
    salt = bytes.fromhex(salt_hex)
    # Decode the ciphertext
    ciphertext = base64.b64decode(ciphertext_b64)

    # Derive the key using the same parameters
    key = PBKDF2(password, salt, dkLen=16, count=1000, hmac_hash_module=SHA1)

    # Decrypt with AES-CBC
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    plaintext_padded = cipher.decrypt(ciphertext)

    # Remove PKCS#7 padding
    pad_len = plaintext_padded[-1]
    plaintext_bytes = plaintext_padded[:-pad_len]

    return plaintext_bytes.decode("utf-8")


if __name__ == "__main__":
    # RSA keys (for demonstration purposes only):
    # In a real scenario, the server holds the private key and the client has the public key.
    # You can generate your own keys using OpenSSL or PyCryptodome.

    public_key_pem = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAl6g7wvj+fxKlksLzSeURkbEDUWz87SI9PTI9tCRd6G38Vnsu3FnSCrNciYr8N1IkOWMMGlzabMB4NUziHo0Z8VlaBuS8rk6q5Np03WeOVydnProlt1YIC620NkI45FbV0fuGKdzr4Tpj4YYQnkihps5pvtCdu5G+eXfGo6pktL5EnDZVD2hqOib8iwCmdKC6nKJzAguF9GfavmTEbMysBtt3URQh6VhE+wK7ImJ5F7bodNl/9Lgfl8X71S1tFIvC8p0/VTXyK3imxkj1g5DuSvQUKUTuHkEO/V3w25bgCUhBR5KLuSWusnUZT2bxFjjyj7cC28mjQ5OReo//7rCxepu7z7smNAKWqqVazBYSV9BPLCxZUBE5MplwPLvV2/V021kyEd620x3MU3jKEt9dEEtfidUUI95KVccQLTQ5xdC1eajJqKwPu4gOErr07EsJ/vJQddrL5zalhtn3k4c71+C+t/fo4pAhoFe5xGCcYZUFl2z3EKjyHW/TYKz40GE0TXGqb3V+OoGWJLtvb2hm1fYY84ElYlrZid1VWEtS+uMPTtomo87EjOfEErRTiw3WnB4KFkvWlVOB9GqRv/1ABx5DZ4uZ/YfMYDO5aiTvlhH38mtaj8aPOzblg/vNf5VY97PtixhCKD3GGGo2Iwpig8XkoFMmkewgoL1uVriteQ0CAwEAAQ==
-----END PUBLIC KEY-----
"""

    # The data you want to send securely
    data = {
        "citizen": "test",
        "password": "test",
        "grant_type": "password",
        "reqDtm": "2024/12/20 20:16:00",
    }

    # CLIENT SIDE (Encryption):
    # 1. Generate random AES password
    r = generate_random_password(32)

    # 2. RSA encrypt this AES password with the server's public key
    o = rsa_encrypt_password(r, public_key_pem)

    # 3. AES encrypt the data using that random password
    a = aes_encrypt(json.dumps(data), r)

    # The client sends this JSON to the server:
    request_body = {"key": o, "value": a}

    print("Encrypted Request Body:")
    print(json.dumps(request_body, indent=2))

    # 4. AES-decrypt the value using the recovered AES password
    decrypted_data = aes_decrypt(a, r)

    print("\nDecrypted Data:")
    print(decrypted_data)  # Should match the original plaintext JSON
