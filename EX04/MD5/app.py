"""
MD5 Hashing Process Demonstration - Flask Backend
Implements MD5 algorithm with detailed intermediate step logging
"""

import struct
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


class MD5Demonstrator:
    """Complete MD5 implementation with detailed step-by-step demonstration"""
    
    # Initial hash values (little-endian)
    INITIAL_HASH = [
        0x67452301,
        0xEFCDAB89,
        0x98BADCFE,
        0x10325476
    ]
    
    # Constants for 64 operations
    K = [
        0xD76AA478, 0xE8C7B756, 0x242070DB, 0xC1BDCEEE,
        0xF57C0FAF, 0x4787C62A, 0xA8304613, 0xFD469501,
        0x698098D8, 0x8B44F7AF, 0xFFFF5BB1, 0x895CD7BE,
        0x6B901122, 0xFD987193, 0xA679438E, 0x49B40821,
        0xF61E2562, 0xC040B340, 0x265E5A51, 0xE9B6C7AA,
        0xD62F105D, 0x02441453, 0xD8A1E681, 0xE7D3FBC8,
        0x21E1CDE6, 0xC33707D6, 0xF4D50D87, 0x455A14ED,
        0xA9E3E905, 0xFCEFA3F8, 0x676F02D9, 0x8D2A4C8A,
        0xFFFA3942, 0x8771F681, 0x6D9D6122, 0xFDE5380C,
        0xA4BEEA44, 0x4BDECFA9, 0xF6BB4B60, 0xBEBFBC70,
        0x289B7EC6, 0xEAA127FA, 0xD4EF3085, 0x04881D05,
        0xD9D4D039, 0xE6DB99E5, 0x1FA27CF8, 0xC4AC5665,
        0xF4292244, 0x432AFF97, 0xAB9423A7, 0xFC93A039,
        0x655B59C3, 0x8F0CCC92, 0xFFEFF47D, 0x85845DD1,
        0x6FA87E4F, 0xFE2CE6E0, 0xA3014314, 0x4E0811A1,
        0xF7537E82, 0xBD3AF236, 0x2AD7D2BB, 0xEB86D391
    ]
    
    # Shift amounts for 64 operations
    SHIFTS = [
        7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21
    ]
    
    def __init__(self):
        self.steps = []
        
    def _add_step(self, title, description, values=None, binary=None, hex_values=None):
        """Add a step to the demonstration log"""
        step = {
            "title": title,
            "description": description,
            "values": values or [],
            "binary": binary or "",
            "hex_values": hex_values or []
        }
        self.steps.append(step)
        return step
    
    def _int_to_hex(self, n, bytes_count=4):
        """Convert integer to hex string"""
        return format(n, f'0{bytes_count*2}x').upper()
    
    def _left_rotate(self, x, n, bits=32):
        """Left rotate a 32-bit value"""
        x = x & ((1 << bits) - 1)
        return ((x << n) | (x >> (bits - n))) & ((1 << bits) - 1)
    
    def _pad_message(self, message):
        """Pad message according to MD5 specification"""
        msg_bytes = list(message.encode('utf-8'))
        original_bit_length = len(msg_bytes) * 8
        
        # Add single '1' bit (0x80)
        padded = msg_bytes[:]
        padded.append(0x80)
        
        # Calculate padding needed to reach 64 bytes less than a multiple of 512 bits
        while len(padded) % 64 != 56:
            padded.append(0x00)
        
        # Add original length in bits as 64-bit little-endian
        length_bytes = struct.pack('<Q', original_bit_length)
        padded.extend(length_bytes)
        
        return padded, original_bit_length
    
    def hash(self, message):
        """Main hash function with step-by-step demonstration"""
        self.steps = []
        
        # ===== STEP 1: Input Message =====
        self._add_step(
            "Step 1: Input Message",
            f"The original input message from the user.\n\nMessage: \"{message}\"\nLength: {len(message)} characters ({len(message.encode('utf-8'))} bytes)",
            values=[f"Input: \"{message}\"", f"Character length: {len(message)}", f"Byte length: {len(message.encode('utf-8'))}"]
        )
        
        # ===== STEP 2: Convert to Bytes =====
        message_bytes = list(message.encode('utf-8'))
        byte_repr = ' '.join(f'{b:02x}' for b in message_bytes)
        
        self._add_step(
            "Step 2: Convert to Bytes",
            "Convert each character to its ASCII/UTF-8 byte representation.\nEach character becomes an 8-bit byte.",
            values=[f"Total bytes: {len(message_bytes)}", f"First 16 bytes: {byte_repr[:47]}"],
            hex_values=[f"Byte hex: {byte_repr}"]
        )
        
        # ===== STEP 3: Padding =====
        padded_message, original_bit_length = self._pad_message(message)
        padding_bytes = len(padded_message) - len(message_bytes)
        
        self._add_step(
            "Step 3: Message Padding",
            f"Add padding bits to make message length congruent to 448 mod 512.\n\n"
            f"Original length: {original_bit_length} bits ({original_bit_length // 8} bytes)\n"
            f"After padding: {len(padded_message)} bytes ({len(padded_message) * 8} bits)\n"
            f"Padding added: {padding_bytes} bytes",
            values=[
                f"Original bits: {original_bit_length}",
                f"Padded bits: {len(padded_message) * 8}",
                f"Padding bytes: {padding_bytes}",
                f"512-bit blocks: {len(padded_message) // 64}"
            ],
            hex_values=[f"Padded (first 64 bytes): {' '.join(f'{b:02x}' for b in padded_message[:64])}"]
        )
        
        # ===== STEP 4: Initialize Hash Values =====
        hash_values = list(self.INITIAL_HASH)
        
        self._add_step(
            "Step 4: Initialize Hash Values (IV)",
            "Four 32-bit words are initialized with specific constant values (in little-endian):\n\n"
            "A = 0x67452301\n"
            "B = 0xEFCDAB89\n"
            "C = 0x98BADCFE\n"
            "D = 0x10325476\n\n"
            "These values will be updated through each 512-bit block processing.",
            values=[
                f"A = {self._int_to_hex(hash_values[0])}",
                f"B = {self._int_to_hex(hash_values[1])}",
                f"C = {self._int_to_hex(hash_values[2])}",
                f"D = {self._int_to_hex(hash_values[3])}"
            ]
        )
        
        # ===== STEP 5: Process Each 512-bit Block =====
        num_blocks = len(padded_message) // 64
        
        for block_num in range(num_blocks):
            block_start = block_num * 64
            block = padded_message[block_start:block_start + 64]
            
            # Convert to 16 32-bit words (little-endian)
            M = []
            for i in range(16):
                word = int.from_bytes(block[i*4:i*4+4], byteorder='little')
                M.append(word)
            
            self._add_step(
                f"Step 5.{block_num + 1}: Block {block_num + 1} Division",
                f"Divide padded message into 512-bit (64-byte) blocks.\n\n"
                f"Processing block {block_num + 1} of {num_blocks}\n"
                f"Each block contains 16 32-bit words (M[0] to M[15])",
                values=[
                    f"Block {block_num + 1} words (M[0-7]): {' '.join(self._int_to_hex(m) for m in M[:8])}",
                    f"Block {block_num + 1} words (M[8-15]): {' '.join(self._int_to_hex(m) for m in M[8:])}"
                ]
            )
            
            # ===== STEP 6: Message Schedule =====
            # Prepare 64 words from 16 using XOR and left rotation
            W = M[:]
            for i in range(16, 64):
                prev = W[i-3] ^ W[i-8] ^ W[i-14] ^ W[i-16]
                W.append(self._left_rotate(prev, 1))
            
            self._add_step(
                f"Step 6.{block_num + 1}: Message Schedule Creation",
                f"Expand 16 words to 64 words using the formula:\n\n"
                f"W[t] = ROTL(W[t-3] XOR W[t-8] XOR W[t-14] XOR W[t-16], 1)\n\n"
                f"First 16 words are the original message words.\n"
                f"Words 16-63 are computed using XOR and left rotation.",
                values=[
                    f"W[0-7]:  {' '.join(self._int_to_hex(w) for w in W[:8])}",
                    f"W[8-15]: {' '.join(self._int_to_hex(w) for w in W[8:16])}",
                    f"W[16-23]: {' '.join(self._int_to_hex(w) for w in W[16:24])}"
                ]
            )
            
            # ===== STEP 7: Compression Function =====
            a, b, c, d = hash_values
            
            # Define round functions
            def F(x, y, z): return (x & y) | (~x & z)
            def G(x, y, z): return (x & z) | (y & ~z)
            def H(x, y, z): return x ^ y ^ z
            def I(x, y, z): return y ^ (x | ~z)
            
            round_functions = [F, G, H, I]
            round_names = ["Round 1 (F)", "Round 2 (G)", "Round 3 (H)", "Round 4 (I)"]
            
            # Process 4 rounds of 16 operations each
            for round_num in range(4):
                round_desc = ""
                sample_ops = []
                
                for i in range(16):
                    idx = round_num * 16 + i
                    
                    # Calculate g based on round
                    if round_num == 0:
                        g = i
                    elif round_num == 1:
                        g = (5 * i + 1) % 16
                    elif round_num == 2:
                        g = (3 * i + 5) % 16
                    else:
                        g = (7 * i) % 16
                    
                    # Current values
                    func = round_functions[round_num]
                    temp = (a + func(b, c, d) + W[g] + self.K[idx]) & 0xFFFFFFFF
                    temp = self._left_rotate(temp, self.SHIFTS[idx])
                    temp = (temp + b) & 0xFFFFFFFF
                    
                    # Save first operation of each round for display
                    if i == 0:
                        sample_ops = [
                            f"Operation {idx}: g={g}, K={self._int_to_hex(self.K[idx])}, shift={self.SHIFTS[idx]}",
                            f"Function: {['F', 'G', 'H', 'I'][round_num]}(B,C,D)"
                        ]
                        round_desc = f"Operations {idx}-{idx+15}: g = {g} for i=0"
                    
                    # Rotate variables: (a, b, c, d) = (d, temp, b, c)
                    a, b, c, d = d, temp, b, c
                
                self._add_step(
                    f"  {round_names[round_num]} - Block {block_num + 1}",
                    f"{round_names[round_num]} performs 16 operations using:\n\n"
                    f"• Round 1 (F): g = i\n"
                    f"• Round 2 (G): g = (5*i + 1) mod 16\n"
                    f"• Round 3 (H): g = (3*i + 5) mod 16\n"
                    f"• Round 4 (I): g = (7*i) mod 16\n\n"
                    f"Each operation computes:\n"
                    f"a = b + ROTL((a + F(b,c,d) + X[g] + T[i]) << s)",
                    values=sample_ops + [
                        f"After round: A={self._int_to_hex(a)}, B={self._int_to_hex(b)}, C={self._int_to_hex(c)}, D={self._int_to_hex(d)}"
                    ]
                )
            
            # Add to hash
            hash_values[0] = (hash_values[0] + a) & 0xFFFFFFFF
            hash_values[1] = (hash_values[1] + b) & 0xFFFFFFFF
            hash_values[2] = (hash_values[2] + c) & 0xFFFFFFFF
            hash_values[3] = (hash_values[3] + d) & 0xFFFFFFFF
            
            self._add_step(
                f"  Update Hash - Block {block_num + 1}",
                f"Add compressed block values to the running hash:\n\n"
                f"H0 = H0 + A\n"
                f"H1 = H1 + B\n"
                f"H2 = H2 + C\n"
                f"H3 = H3 + D",
                values=[
                    f"H0 += A: {self._int_to_hex(hash_values[0])}",
                    f"H1 += B: {self._int_to_hex(hash_values[1])}",
                    f"H2 += C: {self._int_to_hex(hash_values[2])}",
                    f"H3 += D: {self._int_to_hex(hash_values[3])}"
                ]
            )
        
        # ===== STEP 8: Final Hash =====
        # Convert to little-endian and concatenate
        result = b''
        for h in hash_values:
            result += h.to_bytes(4, byteorder='little')
        
        final_hash = result.hex()
        
        self._add_step(
            "Step 8: Final Hash Digest",
            f"Concatenate the four 32-bit hash values in little-endian order.\n\n"
            f"Final Hash = H0 || H1 || H2 || H3\n\n"
            f"Result: 128-bit hash value (32 hexadecimal characters)",
            values=[
                f"Final Hash: {final_hash}",
                f"Length: 128 bits (32 hex chars)"
            ],
            hex_values=[f"Hash breakdown: {self._int_to_hex(hash_values[0])} {self._int_to_hex(hash_values[1])} {self._int_to_hex(hash_values[2])} {self._int_to_hex(hash_values[3])}"]
        )
        
        return final_hash


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/hash', methods=['POST'])
def compute_hash():
    """API endpoint to compute MD5 hash with detailed steps"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        message = data.get('message', '')
        
        if message is None:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create MD5 demonstrator and compute
        md5_demo = MD5Demonstrator()
        hash_result = md5_demo.hash(message)
        
        # Prepare response
        response = {
            'message': message,
            'hash': hash_result,
            'steps': md5_demo.steps,
            'summary': {
                'original_length': len(message.encode('utf-8')) if message else 0,
                'padded_length': len(md5_demo.steps[2]['hex_values'][0].replace(' ', '')) // 2 if len(md5_demo.steps) > 2 else 0,
                'num_blocks': (len(message.encode('utf-8')) + 8 + 55) // 64 + 1 if message else 0
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Return example inputs for demonstration"""
    examples = [
        {"message": "abc", "description": "Three characters - known MD5"},
        {"message": "The quick brown fox jumps over the lazy dog", "description": "Famous pangram"},
        {"message": "message digest", "description": "MD5 original example"},
        {"message": "1234567890", "description": "Numbers only"},
    ]
    return jsonify(examples)


if __name__ == '__main__':
    print("=" * 60)
    print("MD5 Hashing Process Demonstration")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Open http://127.0.0.1:5000 in your browser\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)