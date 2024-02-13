import random
import time
import hashlib
from urllib.parse import urlparse


def encrypt_login(s: str):
    ascii_values = []
    for char in s:
        ascii_value = ord(char)
        if 0 <= ascii_value <= 127:
            ascii_values.append(ascii_value)
        elif 128 <= ascii_value <= 2047:
            ascii_values.append(192 | (31 & (ascii_value >> 6)))
            ascii_values.append(128 | (63 & ascii_value))
        elif (2048 <= ascii_value <= 55295) or (57344 <= ascii_value <= 65535):
            ascii_values.append(224 | (15 & (ascii_value >> 12)))
            ascii_values.append(128 | (63 & (ascii_value >> 6)))
            ascii_values.append(128 | (63 & ascii_value))
    for i in range(len(ascii_values)):
        ascii_values[i] &= 255
    hex_values = []
    for ascii_value in ascii_values:
        hex_values.append(hex(5 ^ ascii_value)[2:])
    return "".join(hex_values)

def generate_verify():
    characters = list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    num_characters = len(characters)

    timestamp = hex(int(time.time()))[2:]

    uuid = [''] * 36

    uuid[8] = uuid[13] = uuid[18] = uuid[23] = "_"
    uuid[14] = "4"

    for i in range(36):
        if not uuid[i]:
            random_index = random.randint(0, num_characters - 1)
            if i == 19:
                uuid[i] = characters[(3 & random_index) | 8]
            else:
                uuid[i] = characters[random_index]

    return "verify_" + timestamp + "_" + ''.join(uuid)

def extract_aweme_id(url: str):
    path = urlparse(url).path
    return path.split("/")[-1]

def generate_hashed_id(username: str):
    hashed_id = hashlib.sha256((username + "aDy0TUhtql92P7hScCs97YWMT-jub2q9").encode()).hexdigest()
    return hashed_id
