import math

class SHA512Visualizer:
    def __init__(self):
        # Initial hash values (first 64 bits of fractional parts of square roots of first 8 primes)
        self.H = [
            0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
            0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
            0x510e527fade682d1, 0x9b05688c2b3e6c1f,
            0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
        ]
        
        # Round constants (first 80 prime numbers' cube roots)
        self.K = self._generate_K()
    
    def _generate_K(self):
        """Generate round constants K[0..79]"""
        K = []
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 
                  59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 
                  127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 
                  191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 
                  257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
                  331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397,
                  401, 409, 419, 421, 431, 433, 439]
        
        for p in primes:
            K.append(int((p ** (1/3)) * (2**64)) & 0xFFFFFFFFFFFFFFFF)
        
        return K
    
    def _rightrotate(self, x, n):
        """Right rotate operation"""
        return ((x >> n) | (x << (64 - n))) & 0xFFFFFFFFFFFFFFFF
    
    def _rightshift(self, x, n):
        """Right shift operation"""
        return x >> n
    
    def _ch(self, x, y, z):
        """Choice function: (x AND y) XOR (NOT x AND z)"""
        return (x & y) ^ (~x & z)
    
    def _maj(self, x, y, z):
        """Majority function: (x AND y) XOR (x AND z) XOR (y AND z)"""
        return (x & y) ^ (x & z) ^ (y & z)
    
    def _sigma0(self, x):
        """Sigma 0: ROTR(x,28) ^ ROTR(x,34) ^ ROTR(x,39)"""
        return self._rightrotate(x, 28) ^ self._rightrotate(x, 34) ^ self._rightrotate(x, 39)
    
    def _sigma1(self, x):
        """Sigma 1: ROTR(x,14) ^ ROTR(x,18) ^ ROTR(x,41)"""
        return self._rightrotate(x, 14) ^ self._rightrotate(x, 18) ^ self._rightrotate(x, 41)
    
    def _gamma0(self, x):
        """Gamma 0: ROTR(x,1) ^ ROTR(x,8) ^ SHR(x,7)"""
        return self._rightrotate(x, 1) ^ self._rightrotate(x, 8) ^ self._rightshift(x, 7)
    
    def _gamma1(self, x):
        """Gamma 1: ROTR(x,19) ^ ROTR(x,61) ^ SHR(x,6)"""
        return self._rightrotate(x, 19) ^ self._rightrotate(x, 61) ^ self._rightshift(x, 6)
    
    def compute_with_steps(self, message):
        """Compute SHA-512 with detailed step-by-step visualization"""
        steps = []
        
        # Step 1: Convert message to binary
        msg_bytes = message.encode('utf-8')
        original_length = len(msg_bytes) * 8
        steps.append({
            'step': 'Input',
            'description': 'Original message as bytes',
            'value': message,
            'hex': msg_bytes.hex(),
            'details': f'Length: {original_length} bits'
        })
        
        # Step 2: Padding
        padded = self._pad_message(msg_bytes)
        steps.append({
            'step': 'Padding',
            'description': 'Append padding bits to message',
            'value': padded.hex(),
            'details': f'Original: {original_length} bits -> Padded: {len(padded)*8} bits'
        })
        
        # Step 3: Parse into chunks
        chunks = [padded[i:i+64] for i in range(0, len(padded), 64)]
        steps.append({
            'step': 'Message Schedule',
            'description': f'Divide into {len(chunks)} 512-bit chunk(s)',
            'value': f'{len(chunks)} chunk(s)',
            'details': f'Each chunk is 512 bits (64 bytes)'
        })
        
        # Process each chunk
        for chunk_num, chunk in enumerate(chunks):
            # Prepare message schedule W[0..79]
            W = []
            for t in range(80):
                if t < 16:
                    # Convert 8 bytes to 64-bit word (big-endian)
                    w = int.from_bytes(chunk[t*8:(t+1)*8], 'big')
                    W.append(w)
                else:
                    # W[t] = gamma1(W[t-2]) + W[t-7] + gamma0(W[t-15]) + W[t-16]
                    val = (self._gamma1(W[t-2]) + W[t-7] + 
                           self._gamma0(W[t-15]) + W[t-16]) & 0xFFFFFFFFFFFFFFFF
                    W.append(val)
            
            if chunk_num == 0:  # Show detailed steps for first chunk only
                steps.append({
                    'step': f'Message Schedule - W[t]',
                    'description': 'First 16 words from chunk (shown as hex)',
                    'value': 'W[0..15]',
                    'details': ', '.join([f'W[{i}]={W[i]:016x}' for i in range(16)])
                })
                
                steps.append({
                    'step': 'W[t] Expansion (t=16..79)',
                    'description': 'W[t] = γ1(W[t-2]) + W[t-7] + γ0(W[t-15]) + W[t-16]',
                    'value': f'W[16]={W[16]:016x}',
                    'details': f'γ1({W[14]:016x}) + {W[9]:016x} + γ0({W[1]:016x}) + {W[0]:016x} = {W[16]:016x}'
                })
            
            # Initialize working variables
            a, b, c, d, e, f, g, h = self.H.copy()
            
            if chunk_num == 0:
                steps.append({
                    'step': 'Initial Hash Values',
                    'description': 'Starting hash values H0-H7',
                    'value': 'a, b, c, d, e, f, g, h',
                    'details': ', '.join([f'{v:016x}' for v in [a, b, c, d, e, f, g, h]])
                })
            
            # 80 rounds
            for t in range(80):
                T1 = (h + self._sigma1(e) + self._ch(e, f, g) + self.K[t] + W[t]) & 0xFFFFFFFFFFFFFFFF
                T2 = (self._sigma0(a) + self._maj(a, b, c)) & 0xFFFFFFFFFFFFFFFF
                
                h = g
                g = f
                f = e
                e = (d + T1) & 0xFFFFFFFFFFFFFFFF
                d = c
                c = b
                b = a
                a = (T1 + T2) & 0xFFFFFFFFFFFFFFFF
                
                if chunk_num == 0 and t in [0, 20, 40, 60, 79]:
                    steps.append({
                        'step': f'Round {t}',
                        'description': f'T1 = h + Σ1(e) + Ch(e,f,g) + K[t] + W[t]',
                        'value': f'T1={T1:016x}, T2={T2:016x}',
                        'details': f'a={a:016x} b={b:016x} c={c:016x} d={d:016x} e={e:016x} f={f:016x} g={g:016x} h={h:016x}'
                    })
            
            # Add chunk hash to current hash
            self.H = [(self.H[i] + [a, b, c, d, e, f, g, h][i]) & 0xFFFFFFFFFFFFFFFF 
                     for i in range(8)]
            
            if chunk_num == 0:
                steps.append({
                    'step': 'Update Hash Values',
                    'description': 'H[i] = H[i] + working variable',
                    'value': 'Final H0-H7 after chunk 0',
                    'details': ', '.join([f'{v:016x}' for v in self.H])
                })
        
        # Final hash
        final_hash = ''.join([f'{h:016x}' for h in self.H])
        
        steps.append({
            'step': 'Final Hash',
            'description': 'Concatenate all H values',
            'value': final_hash,
            'details': 'SHA-512 Output (128 hex characters = 512 bits)'
        })
        
        return {
            'algorithm': 'SHA-512',
            'input': message,
            'input_hex': msg_bytes.hex(),
            'input_bytes': len(msg_bytes),
            'padded_hex': padded.hex(),
            'final_hash': final_hash,
            'steps': steps
        }
    
    def _pad_message(self, message):
        """Add padding to message"""
        msg_len = len(message)
        bit_len = msg_len * 8
        
        # Append '1' bit (0x80)
        message += b'\x80'
        
        # Append zeros until length ≡ 896 mod 1024 (112 mod 128)
        while (len(message) % 128) != 112:
            message += b'\x00'
        
        # Append original length as 128-bit big-endian
        message += bit_len.to_bytes(16, 'big')
        
        return message