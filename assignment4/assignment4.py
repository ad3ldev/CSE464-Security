# -*- coding: utf-8 -*-
"""Assignment#4_security_RSA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r5uZLiDgMQalPnbAlYiu6AWMXZTHP1r7
"""

from random import randint
from PrimeGenerator import PrimeGenerator

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def multiplicative_inverse(e, phi):
    d = 0
    x1, x2 = 0, 1
    y1, y2 = 1, 0
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi // e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = y2 - temp1 * y1

        x2 = x1
        x1 = x
        y2 = y1
        y1 = y

    if temp_phi == 1:
        d = y2
    return d

# def extended_euclidean(a, b):
#     if a == 0:
#         return b, 0, 1
#     else:
#         gcd, x, y = extended_euclidean(b % a, a)
#         return gcd, y - (b // a) * x, x

# def multiplicative_inverse(e, phi):
#     gcd, x, _ = extended_euclidean(e, phi)
#     if gcd != 1:
#         raise ValueError("The multiplicative inverse does not exist.")
#     else:
#         while x < 0:
#             x += phi
#         return x

def generate_keypair(bitlength):
    p_generator = PrimeGenerator(bits=bitlength)
    q_generator = PrimeGenerator(bits=bitlength)

    p = p_generator.findPrime()
    q = q_generator.findPrime()
    n = p * q
    totient = (p-1) * (q-1)

    # Choosing e such that 1 < e < phi and gcd(e, phi) = 1
    e = randint(1, totient)
    while gcd(e, totient) != 1:
        e = randint(1, totient)
    # For convienece we use the e value in the lectures
    # e = 65537

    # Calculate d such that it satisfies d * e ≡ 1 (mod totient)
    d = multiplicative_inverse(e, totient)

    # Ensure d is positive
    while d < 0:
        d += totient

    return ((e, n), (d, n))

def encrypt(public_key, plaintext):
    e, n = public_key
    cipher = [pow(ord(char), e, n) for char in plaintext]
    return cipher

def decrypt(private_key, ciphertext):
    d, n = private_key
    plain = [chr(pow(char, d, n)) for char in ciphertext]
    return ''.join(plain)

import time
bitlength = 2048
start_time = time.time()
public_key, private_key = generate_keypair(bitlength)
# message = "Hello, RSA!"
with open("long_msg", 'r') as file:
        message = file.read()
# print("Original Message:", message)
encrypted_message = encrypt(public_key, message)
print("Encrypted Message:", encrypted_message)
decrypted_message = decrypt(private_key, encrypted_message)
print("Decrypted Message:", decrypted_message)
end_time = time.time()
total_time = end_time - start_time
print("Time for Our Implementation of RSA: ", total_time)

"""##Problem 2
###Testing using module pycrypto
"""

!pip install pycryptodome

from Crypto.PublicKey import RSA
from Crypto.Util import number
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES

def library_generator(bits):
    p = number.getPrime(bits)
    q = number.getPrime(bits)
    n = p * q
    totient = (p-1) * (q-1)
    # # Choosing e such that 1 < e < phi and gcd(e, phi) = 1
    # e = randint(1, totient)
    # while gcd(e, totient) != 1:
    #     e = randint(1, totient)
    # For convienece we use the e value in the lectures
    e = 65537
    # Calculate d such that it satisfies d * e ≡ 1 (mod totient)
    d = multiplicative_inverse(e, totient)
    # Ensure d is positive
    while d < 0:
        d += totient

    key = RSA.construct((n,e,d))
    public_key = key.public_key()
    private_key = key
    return public_key, private_key

def encrypt_module(public_key, message):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_module(private_key, encrypted_message):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()


start_time = time.time()
public_key, private_key = library_generator(1024)
print(public_key)
print(private_key)

message = "Hello, RSA!"
print("Original Message: ", message)

encrypted_message = encrypt_module(public_key, message)
print("Encrypted message:", encrypted_message)

decrypted_message = decrypt_module(private_key, encrypted_message)
print("Decrypted message:", decrypted_message)
end_time = time.time()
total_time_module = end_time - start_time
print("Time for RSA Module: ", total_time_module)

def test_RSA_module(message, nbits):
  start_time = time.time()
  public_key, private_key = library_generator(nbits)
  print(public_key)
  print(private_key)

  # print("Original Message: ", message)
  encrypted_message = encrypt_module(public_key, message)
  print("Encrypted message:", encrypted_message)

  decrypted_message = decrypt_module(private_key, encrypted_message)
  print("Decrypted message:", decrypted_message)
  end_time = time.time()
  total_time_module = end_time - start_time
  print("Time for RSA Module: ", total_time_module)

with open("long_msg", 'r') as file:
        message = file.read()
test_RSA_module(message, 2048)
