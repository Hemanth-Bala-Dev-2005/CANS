"""
Educational Cryptography Lab - DES and AES Visualizer
Implemented from scratch without external crypto libraries
"""

from flask import Flask, render_template, request, jsonify
import json
import os

# Configure template folder
template_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=template_dir)

# ==================== UTILITY FUNCTIONS ====================

def string_to_binary(text):
    """Convert string to binary string"""
    return ''.join(format(ord(c), '08b') for c in text)

def binary_to_string(binary):
    """Convert binary string to string"""
    chars = []
    for i in range(0, len(binary), 8):
        chars.append(chr(int(binary[i:i+8], 2)))
    return ''.join(chars)

def hex_to_binary(hex_str):
    """Convert hex to binary string"""
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)

def binary_to_hex(binary):
    """Convert binary to hex string"""
    return hex(int(binary, 2))[2:].upper().zfill(len(binary) // 4)

def xor_strings(a, b):
    """XOR two binary strings"""
    result = ''
    for i in range(len(a)):
        result += '1' if a[i] != b[i] else '0'
    return result

def permute(data, table):
    """Apply permutation table to data"""
    return ''.join(data[p - 1] for p in table)

def rotate_left(binary, n):
    """Rotate binary string left by n bits"""
    return binary[n:] + binary[:n]

# ==================== DES CONSTANTS ====================

# Initial Permutation (IP)
IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Final Permutation (IP^-1)
FP_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Expansion Permutation (E-bit)
EXPANSION_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Permutation (P-box)
P_TABLE = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# S-boxes (8 boxes, each 4x16)
S_BOXES = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    # S2
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    # S3
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    # S4
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 9, 14, 5, 6, 3, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    # S5
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    # S6
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    # S7
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [11, 12, 14, 4, 6, 9, 8, 1, 3, 5, 0, 10, 13, 2, 7, 15]],
    # S8
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]

# Permuted Choice 1 (for key schedule)
PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]

# Permuted Choice 2 (for key schedule)
PC2_TABLE = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

# Left shift schedule
SHIFT_TABLE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


def des_sbox_substitution(data):
    """Apply S-box substitution"""
    result = ''
    for i in range(8):
        block = data[i * 6:(i + 1) * 6]
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        value = S_BOXES[i][row][col]
        result += format(value, '04b')
    return result


# ==================== DES FUNCTIONS ====================

def des_key_schedule(key):
    """Generate 16 subkeys for DES"""
    steps = []
    
    # Step 1: Initial key permutation
    permuted_key = permute(key, PC1_TABLE)
    steps.append({
        "step": "1. Initial Permutation (PC-1)",
        "description": "Apply PC-1 permutation to 64-bit key",
        "input": key,
        "output": permuted_key,
        "details": f"Key: {key[:8]}_{key[8:]} → PC-1: {permuted_key[:8]}_{permuted_key[8:]}"
    })
    
    # Split into C and D
    C = permuted_key[:28]
    D = permuted_key[28:]
    
    subkeys = []
    
    for round_num in range(16):
        # Step 2: Left shift
        C = rotate_left(C, SHIFT_TABLE[round_num])
        D = rotate_left(D, SHIFT_TABLE[round_num])
        
        combined = C + D
        
        # Step 3: Permutation choice 2
        subkey = permute(combined, PC2_TABLE)
        subkeys.append(subkey)
        
        steps.append({
            "step": f"Round {round_num + 1} Key Generation",
            "description": f"Generate subkey K{round_num + 1}",
            "after_shift": f"C: {C}, D: {D}",
            "output": subkey,
            "details": f"After left shift by {SHIFT_TABLE[round_num]} → {subkey[:6]}_{subkey[6:]}"
        })
    
    return subkeys, steps


def des_f_function(R, subkey):
    """DES Feistel function f(R, K)"""
    steps = []
    
    # Step 1: Expansion
    expanded = permute(R, EXPANSION_TABLE)
    steps.append({
        "step": "1. Expansion Permutation",
        "description": "Expand 32-bit R to 48 bits",
        "input": R,
        "output": expanded,
        "details": f"32-bit → 48-bit: {expanded[:6]}_{expanded[6:12]}_{expanded[12:18]}_{expanded[18:24]}_{expanded[24:30]}_{expanded[30:]}"
    })
    
    # Step 2: XOR with subkey
    xor_result = xor_strings(expanded, subkey)
    steps.append({
        "step": "2. XOR with Subkey",
        "description": "R ⊕ K (48-bit XOR)",
        "input": expanded,
        "key": subkey,
        "output": xor_result,
        "details": f"Expanded: {expanded[:6]}_{expanded[6:]}\nSubkey: {subkey[:6]}_{subkey[6:]}\nXOR: {xor_result[:6]}_{xor_result[6:]}"
    })
    
    # Step 3: S-box substitution
    sbox_result = des_sbox_substitution(xor_result)
    steps.append({
        "step": "3. S-Box Substitution",
        "description": "8 S-boxes transform 48-bit to 32-bit",
        "input": xor_result,
        "output": sbox_result,
        "details": f"48-bit input → 32-bit output using 8 S-boxes"
    })
    
    # Step 4: P-box permutation
    final = permute(sbox_result, P_TABLE)
    steps.append({
        "step": "4. P-Box Permutation",
        "description": "Final permutation on 32-bit output",
        "input": sbox_result,
        "output": final,
        "details": f"S-box output permuted to produce final 32-bit result"
    })
    
    return final, steps


def des_encrypt_block(plaintext, key, detailed_steps=None):
    """Encrypt a single 64-bit block with DES"""
    if detailed_steps is None:
        detailed_steps = []
    
    steps = []
    
    # Step 1: Initial Permutation
    ip_result = permute(plaintext, IP_TABLE)
    steps.append({
        "step": "1. Initial Permutation (IP)",
        "description": "Rearrange bits according to IP table",
        "input": plaintext,
        "output": ip_result,
        "details": f"Input: {plaintext[:8]}_{plaintext[8:]}\nOutput: {ip_result[:8]}_{ip_result[8:]}"
    })
    
    detailed_steps.append({"title": "Initial Permutation", "details": steps.copy()})
    
    # Split into L and R
    L = ip_result[:32]
    R = ip_result[32:]
    
    round_steps = []
    subkeys, key_steps = des_key_schedule(key)
    round_steps.append({"title": "Key Schedule", "details": key_steps})
    
    for round_num in range(16):
        L_prev = L
        
        # Feistel function
        f_output, f_steps = des_f_function(R, subkeys[round_num])
        
        # L = previous R
        L = R
        
        # R = previous L ⊕ f(R, K)
        R = xor_strings(L_prev, f_output)
        
        round_steps.append({
            "title": f"Round {round_num + 1}",
            "details": [
                {"step": "L_i = R_(i-1)", "output": L},
                {"step": "R_i = L_(i-1) ⊕ f(R_(i-1), K{i+1})", "output": R, "details": f"L_prev: {L_prev}, f: {f_output}"}
            ]
        })
    
    detailed_steps.append({"title": "16 Feistel Rounds", "details": round_steps})
    
    # Final permutation (swap L and R first)
    combined = R + L
    final = permute(combined, FP_TABLE)
    
    final_steps = [{
        "step": "Final Permutation (IP⁻¹)",
        "description": "Apply inverse of initial permutation",
        "input": combined,
        "output": final,
        "details": f"R16 || L16: {combined[:8]}_{combined[8:]}\nFinal: {final[:8]}_{final[8:]}"
    }]
    detailed_steps.append({"title": "Final Permutation", "details": final_steps})
    
    return final, detailed_steps


def pad_pkcs7(data, block_size=8):
    """PKCS7 padding"""
    padding = block_size - (len(data) % block_size)
    return data + chr(padding) * padding


def unpad_pkcs7(data):
    """Remove PKCS7 padding"""
    padding = ord(data[-1])
    return data[:-padding]


def des_encrypt(plaintext, key_hex, detailed_steps=None):
    """Encrypt plaintext with DES"""
    if detailed_steps is None:
        detailed_steps = []
    
    # Convert key to binary
    key_binary = hex_to_binary(key_hex)
    
    # Pad plaintext to 8-byte blocks
    padded = pad_pkcs7(plaintext)
    
    steps = []
    steps.append({
        "step": "Key Preparation",
        "description": "Convert hex key to binary",
        "input": key_hex,
        "output": key_binary,
        "details": f"8 bytes (64 bits) key"
    })
    
    steps.append({
        "step": "Padding",
        "description": "Apply PKCS#7 padding",
        "input": plaintext,
        "output": padded,
        "details": f"Added {8 - len(plaintext) % 8} bytes"
    })
    
    detailed_steps.append({"title": "Preprocessing", "details": steps})
    
    ciphertext = ''
    
    for block_num in range(len(padded) // 8):
        block = padded[block_num * 8:(block_num + 1) * 8]
        block_binary = string_to_binary(block)
        
        encrypted, block_steps = des_encrypt_block(block_binary, key_binary)
        detailed_steps.append({"title": f"Block {block_num + 1}", "details": block_steps})
        
        ciphertext += encrypted
    
    return binary_to_hex(ciphertext), detailed_steps


# ==================== AES CONSTANTS ====================

# S-box for SubBytes
AES_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

# Inverse S-box for InvSubBytes
AES_INV_SBOX = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]

# MixColumns matrix
MIX_COLUMNS_MATRIX = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02]
]

# Inverse MixColumns matrix
INV_MIX_COLUMNS_MATRIX = [
    [0x0e, 0x0b, 0x0d, 0x09],
    [0x09, 0x0e, 0x0b, 0x0d],
    [0x0d, 0x09, 0x0e, 0x0b],
    [0x0b, 0x0d, 0x09, 0x0e]
]

# Galois Field multiplication
def gf_mul(a, b):
    """Galois Field multiplication in GF(2^8)"""
    result = 0
    for i in range(8):
        if b & 1:
            result ^= a
        high_bit = a & 0x80
        a = (a << 1) & 0xFF
        if high_bit:
            a ^= 0x1B  # AES irreducible polynomial
        b >>= 1
    return result


def gf_mult_matrix(matrix, state):
    """Multiply matrix with state column"""
    result = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            result[i] ^= gf_mul(matrix[i][j], state[j])
    return result


# ==================== AES FUNCTIONS ====================

def aes_sub_bytes(state, inv=False):
    """SubBytes transformation"""
    sbox = AES_INV_SBOX if inv else AES_SBOX
    steps = []
    
    new_state = []
    for i, byte in enumerate(state):
        row = (byte >> 4) & 0x0F
        col = byte & 0x0F
        new_byte = sbox[byte]
        new_state.append(new_byte)
        
        if i < 4:  # Show first few for clarity
            steps.append({
                "step": f"Byte {i+1}: {hex(byte).upper().zfill(4)} → {hex(new_byte).upper().zfill(4)}",
                "details": f"Row: {row}, Col: {col} → S-box[{row}][{col}] = {hex(new_byte).upper()}"
            })
    
    return new_state, steps


def aes_shift_rows(state, inv=False):
    """ShiftRows transformation"""
    steps = []
    
    if inv:
        # Inverse: shift right
        state[1] = state[1][-1:] + state[1][:-1]
        state[2] = state[2][-2:] + state[2][:-2]
        state[3] = state[3][-3:] + state[3][:-3]
        
        steps.append({
            "step": "InvShiftRows (right shift)",
            "details": f"Row 1: {state[1]}\nRow 2: {state[2]}\nRow 3: {state[3]}"
        })
    else:
        # Forward: shift left
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]
        
        steps.append({
            "step": "ShiftRows (left shift)",
            "details": f"Row 1: rotate 1 left → {state[1]}\nRow 2: rotate 2 left → {state[2]}\nRow 3: rotate 3 left → {state[3]}"
        })
    
    return state, steps


def aes_mix_columns(state, inv=False):
    """MixColumns transformation"""
    steps = []
    matrix = INV_MIX_COLUMNS_MATRIX if inv else MIX_COLUMNS_MATRIX
    operation = "InvMixColumns" if inv else "MixColumns"
    
    new_state = [[0,0,0,0] for _ in range(4)]
    
    for col in range(4):
        column = [state[row][col] for row in range(4)]
        mixed = gf_mult_matrix(matrix, column)
        
        for row in range(4):
            new_state[row][col] = mixed[row]
        
        steps.append({
            "step": f"Column {col + 1}: GF(2⁸) matrix multiplication",
            "details": f"Input: {column}\nOutput: {mixed}"
        })
    
    return new_state, steps


def aes_add_round_key(state, round_key):
    """AddRoundKey transformation"""
    steps = []
    
    new_state = []
    for row in range(4):
        new_row = []
        for col in range(4):
            new_val = state[row][col] ^ round_key[row][col]
            new_row.append(new_val)
        new_state.append(new_row)
    
    steps.append({
        "step": "AddRoundKey: state ⊕ round_key",
        "details": "XOR each byte with corresponding round key byte"
    })
    
    return new_state, steps


def aes_key_expansion(key):
    """AES key expansion"""
    steps = []
    
    # Initial key
    w = [[key[col][row] for col in range(4)] for row in range(4)]
    steps.append({
        "step": "Initial Key Matrix",
        "description": "4x4 key matrix",
        "details": f"{key}"
    })
    
    Nk = 4  # Key length in 32-bit words (128-bit key)
    Nr = 10  # Number of rounds for 128-bit key
    Nb = 4  # Block size in 32-bit words
    
    Rcon = [
        [0x01, 0x00, 0x00, 0x00],
        [0x02, 0x00, 0x00, 0x00],
        [0x04, 0x00, 0x00, 0x00],
        [0x08, 0x00, 0x00, 0x00],
        [0x10, 0x00, 0x00, 0x00],
        [0x20, 0x00, 0x00, 0x00],
        [0x40, 0x00, 0x00, 0x00],
        [0x80, 0x00, 0x00, 0x00],
        [0x1b, 0x00, 0x00, 0x00],
        [0x36, 0x00, 0x00, 0x00]
    ]
    
    for i in range(Nk, Nb * (Nr + 1)):
        temp = w[i - 1]
        
        if i % Nk == 0:
            # RotWord
            temp = temp[1:] + temp[:1]
            # SubWord
            temp = [AES_SBOX[b] for b in temp]
            # XOR with Rcon
            temp = [temp[j] ^ Rcon[i // Nk - 1][j] for j in range(4)]
        
        w.append([w[i - Nk][j] ^ temp[j] for j in range(4)])
        
        if i < 6:  # Show first few keys
            steps.append({
                "step": f"Round Key {i - Nk + 1}",
                "description": f"Word {i}",
                "details": f"w[{i}]: {w[i]}"
            })
    
    return w, steps


def aes_encrypt_block(plaintext_hex, key_hex, detailed_steps=None):
    """Encrypt a 128-bit block with AES"""
    if detailed_steps is None:
        detailed_steps = []
    
    steps = []
    
    # Convert hex to state matrix
    pt_bytes = [int(plaintext_hex[i:i+2], 16) for i in range(0, len(plaintext_hex), 2)]
    state = [[pt_bytes[col * 4 + row] for col in range(4)] for row in range(4)]
    
    steps.append({
        "step": "Convert Plaintext to State Matrix",
        "description": "128-bit block → 4x4 matrix",
        "input": plaintext_hex,
        "output": str(state)
    })
    
    # Key expansion
    key_bytes = [int(key_hex[i:i+2], 16) for i in range(0, len(key_hex), 2)]
    key_matrix = [[key_bytes[col * 4 + row] for col in range(4)] for row in range(4)]
    round_keys, key_steps = aes_key_expansion(key_matrix)
    
    detailed_steps.append({"title": "Key Expansion", "details": key_steps})
    detailed_steps.append({"title": "Initial State", "details": steps})
    
    # Initial round: AddRoundKey
    state, ak_steps = aes_add_round_key(state, round_keys[0:4])
    detailed_steps.append({"title": "Initial AddRoundKey", "details": ak_steps})
    
    # Main rounds (10 for 128-bit key)
    for round_num in range(1, 10):
        round_title = f"Round {round_num}"
        round_details = []
        
        # SubBytes
        state, sb_steps = aes_sub_bytes(state)
        round_details.extend(sb_steps)
        
        # ShiftRows
        state, sr_steps = aes_shift_rows(state)
        round_details.extend(sr_steps)
        
        # MixColumns
        state, mc_steps = aes_mix_columns(state)
        round_details.extend(mc_steps)
        
        # AddRoundKey
        state, ak_steps = aes_add_round_key(state, round_keys[round_num * 4:(round_num + 1) * 4])
        round_details.extend(ak_steps)
        
        detailed_steps.append({"title": round_title, "details": round_details})
    
    # Final round (no MixColumns)
    final_round_title = "Round 10 (Final)"
    final_round_details = []
    
    state, sb_steps = aes_sub_bytes(state)
    final_round_details.extend(sb_steps)
    
    state, sr_steps = aes_shift_rows(state)
    final_round_details.extend(sr_steps)
    
    state, ak_steps = aes_add_round_key(state, round_keys[10 * 4:11 * 4])
    final_round_details.extend(ak_steps)
    
    detailed_steps.append({"title": final_round_title, "details": final_round_details})
    
    # Convert state back to hex
    ciphertext = ''.join(hex(state[row][col])[2:].zfill(2) for row in range(4) for col in range(4))
    
    return ciphertext.upper(), detailed_steps


def aes_encrypt(plaintext, key_hex, detailed_steps=None):
    """Encrypt plaintext with AES"""
    if detailed_steps is None:
        detailed_steps = []
    
    steps = []
    
    # Pad plaintext to 16 bytes
    padded = plaintext.encode('utf-8')
    padding = 16 - (len(padded) % 16)
    padded = padded + bytes([padding] * padding)
    
    steps.append({
        "step": "Padding",
        "description": "PKCS#7 padding to 16-byte boundary",
        "input": plaintext,
        "output": f"{len(padded)} bytes"
    })
    
    detailed_steps.append({"title": "Preprocessing", "details": steps})
    
    ciphertext = ''
    
    for block_num in range(len(padded) // 16):
        block = padded[block_num * 16:(block_num + 1) * 16]
        block_hex = ''.join(hex(b)[2:].zfill(2) for b in block)
        
        encrypted, block_steps = aes_encrypt_block(block_hex, key_hex)
        detailed_steps.append({"title": f"Block {block_num + 1} (128-bit)", "details": block_steps})
        
        ciphertext += encrypted
    
    return ciphertext, detailed_steps


# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    # Read and serve the HTML file directly
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/des', methods=['POST'])
def des():
    data = request.json
    plaintext = data.get('plaintext', '')
    key = data.get('key', '')
    
    # Default values
    if not plaintext:
        plaintext = 'Hello'
    if not key:
        key = '133457799BBCDFF1'  # Standard test key
    
    detailed_steps = []
    ciphertext, steps = des_encrypt(plaintext, key, detailed_steps)
    
    return jsonify({
        "ciphertext": ciphertext,
        "plaintext": plaintext,
        "key": key,
        "steps": steps
    })


@app.route('/aes', methods=['POST'])
def aes():
    data = request.json
    plaintext = data.get('plaintext', '')
    key = data.get('key', '')
    
    # Default values
    if not plaintext:
        plaintext = 'Hello World'
    if not key:
        key = '2b7e151628aed2a6abf7158809cf4f3c'  # Standard test key
    
    detailed_steps = []
    ciphertext, steps = aes_encrypt(plaintext, key, detailed_steps)
    
    return jsonify({
        "ciphertext": ciphertext,
        "plaintext": plaintext,
        "key": key,
        "steps": steps
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)