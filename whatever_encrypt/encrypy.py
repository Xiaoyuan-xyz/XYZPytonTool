# 读取csv
import pandas as pd
import base64


class TrieNode:
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for i, char in enumerate(word):
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
            if current.is_end_of_word:
                return False
        if len(current.children) > 0:
            return False
        current.is_end_of_word = True
        return True


def check_prefix_code(string_list):
    trie = Trie()
    for string in string_list:
        if not trie.insert(string):
            return False, string
    return True, None


file_path = "./whatever_encrypt/code.csv"
df = pd.read_csv(file_path, header=None)
code = df.iloc[:, 0].tolist()

assert len(code) == len(set(code)), "Code list contains duplicate elements"
check_prefix_code_ret, check_prefix_code_conflict = check_prefix_code(code)
assert (
    check_prefix_code_ret
), f"Code list contains prefix conflicts: {check_prefix_code_conflict}"

base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
encryption_mapping = {base64_chars[i]: code[i] for i in range(len(base64_chars))}
decryption_mapping = {code[i]: base64_chars[i] for i in range(len(code))}


def encrypt(text, mapping=encryption_mapping):
    encrypted = []
    for char in text:
        if char in mapping:
            encrypted.append(mapping[char])
        else:
            raise (ValueError(f"Character {char} not in mapping"))
    return "".join(encrypted)


def decrypt(text, reverse_mapping=decryption_mapping):
    decrypted = []
    i = 0
    while i < len(text):
        matched = False
        for j in range(i + 1, len(text) + 1):
            substring = text[i:j]
            if substring in reverse_mapping:
                decrypted.append(reverse_mapping[substring])
                i = j
                matched = True
                break
        if not matched:
            raise (ValueError(f"No match found for substring {text[i:]}"))
    return "".join(decrypted)


def encrypt_text(text):
    base64_str = base64.b64encode(str.encode(text))
    encrypt_str = encrypt(str(base64_str, "utf-8").replace("=", ""))
    return encrypt_str


def decrypt_text(text):
    base64_str = decrypt(text)
    decrypt_str = base64.b64decode(base64_str + "=" * (4 - len(base64_str) % 4))
    return str(decrypt_str, "utf-8")


if __name__ == "__main__":
    text = "hello world"
    encrypted_text = encrypt_text(text)
    decrypted_text = decrypt_text(encrypted_text)
    print(f"Original text: {text}")
    print(f"Encrypted text: {encrypted_text}")
    print(f"Decrypted text: {decrypted_text}")
