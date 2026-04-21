import hashlib
import hmac

class CMACVisualizer:
    def __init__(self):
        self.Rb = 0x87  # Polynomial for 128-bit block size
    
    def compute_with_steps(self, message, key):
        """Compute CMAC with detailed step-by-step visualization"""
        steps = []
        
        # Validate inputs
        if not message:
            message = b''
        if not key:
            key = 'defaultkey1234567'
        
        msg_bytes = message.encode('utf-8') if isinstance(message, str) else message
        key_bytes = key.encode('utf-8') if isinstance(key, str) else key
        
        # Ensure key is 16 bytes (128-bit)
        if len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\x00')
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        
        steps.append({
            'step': 'Input',
            'description': 'Original message and key',
            'value': f'Message: {message}, Key: {key}',
            'details': f'Message bytes: {len(msg_bytes)}, Key bytes: {len(key_bytes)}'
        })
        
        # Step 1: Generate subkeys K1 and K2
        L = self._aes_encrypt(key_bytes, b'\x00' * 16)
        steps.append({
            'step': 'L = AES(K, 0ⁿ)',
            'description': 'Encrypt zero block with key to generate L',
            'value': L.hex(),
            'details': 'If L < 128 (most significant bit is 0), use L << 1 for K1'
        })
        
        K1 = self._generate_subkey(L)
        steps.append({
            'step': 'Subkey K1',
            'description': 'Generate K1 from L using left shift and conditional XOR',
            'value': K1.hex(),
            'details': self._get_k1_details(L)
        })
        
        K2 = self._generate_subkey(K1)
        steps.append({
            'step': 'Subkey K2',
            'description': 'Generate K2 from K1',
            'value': K2.hex(),
            'details': self._get_k2_details(K1)
        })
        
        # Step 2: Pad message to block boundary
        block_size = 16
        blocks = self._split_into_blocks(msg_bytes, block_size)
        
        steps.append({
            'step': 'Message Blocks',
            'description': f'Split message into {len(blocks)} 128-bit block(s)',
            'value': f'{len(blocks)} block(s)',
            'details': f'Block size: {block_size} bytes'
        })
        
        # Step 3: Process blocks
        if len(blocks) == 0:
            # Empty message - use K2
            M_last = bytes([b ^ k for b, k in zip(K2, bytes(16))])
            subkey = K2
            steps.append({
                'step': 'Empty Message',
                'description': 'For empty message, use K2 as subkey',
                'value': 'M = 0ⁿ ⊕ K2',
                'details': f'M_last = {M_last.hex()}'
            })
        else:
            # Last block processing
            last_block = blocks[-1]
            
            if len(last_block) == block_size:
                # Complete block - XOR with K1
                M_last = bytes([b ^ k for b, k in zip(last_block, K1)])
                subkey = K1
                steps.append({
                    'step': 'Last Block (Complete)',
                    'description': 'Last block is complete (16 bytes) - XOR with K1',
                    'value': f'M_last = {last_block.hex()} ⊕ K1',
                    'details': f'Result: {M_last.hex()}'
                })
            else:
                # Incomplete block - padding needed
                padded_block = last_block + b'\x80' + b'\x00' * (block_size - len(last_block) - 1)
                M_last = bytes([b ^ k for b, k in zip(padded_block, K2)])
                subkey = K2
                steps.append({
                    'step': 'Last Block (Incomplete)',
                    'description': 'Pad last block and XOR with K2',
                    'value': f'Pad: {padded_block.hex()} ⊕ K2',
                    'details': f'Result: {M_last.hex()}'
                })
        
        # Step 4: CBC encryption
        X = bytes(16)  # Initial value (IV = 0)
        
        for i, block in enumerate(blocks[:-1]):
            X = self._aes_encrypt(key_bytes, bytes([x ^ b for x, b in zip(X, block)]))
            steps.append({
                'step': f'CBC Step {i+1}',
                'description': f'X = AES(K, X ⊕ M{i+1})',
                'value': f'M{i+1} = {block.hex()}',
                'details': f'X = {X.hex()}'
            })
        
        # Final block
        Y = self._aes_encrypt(key_bytes, M_last)
        steps.append({
            'step': 'Final Block',
            'description': 'Y = AES(K, M_last ⊕ X)',
            'value': f'M_last = {M_last.hex()}, X = {X.hex() if blocks else "0"*32}',
            'details': f'CMAC = Y = {Y.hex()}'
        })
        
        # Step 5: Truncate (output first 64 bits for this demo)
        cmac_result = Y[:8]  # First 64 bits
        
        steps.append({
            'step': 'CMAC Output',
            'description': 'Truncate to first 64 bits (for visualization)',
            'value': cmac_result.hex(),
            'details': 'Final CMAC authentication tag'
        })
        
        return {
            'algorithm': 'CMAC',
            'input': message,
            'key': key,
            'key_hex': key_bytes.hex(),
            'message_hex': msg_bytes.hex(),
            'L': L.hex(),
            'K1': K1.hex(),
            'K2': K2.hex(),
            'cmac': cmac_result.hex(),
            'steps': steps
        }
    
    def _aes_encrypt(self, key, block):
        """Simple AES-like encryption using HMAC-SHA256 as simulation"""
        # Using AES from cryptography library would be more accurate
        # For visualization, we simulate with SHA-256 based pseudo-AES
        import os
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(block) + encryptor.finalize()
    
    def _generate_subkey(self, L):
        """Generate subkey from L"""
        # Check if MSB of L is 1
        if L[0] & 0x80:
            # Shift left and XOR with Rb
            result = bytearray(16)
            carry = 0
            for i in range(15, -1, -1):
                new_carry = (L[i] & 0x80) >> 7
                result[i] = ((L[i] << 1) | carry) & 0xFF
                carry = new_carry
            result[15] ^= self.Rb
            return bytes(result)
        else:
            # Just shift left
            result = bytearray(16)
            carry = 0
            for i in range(15, -1, -1):
                new_carry = (L[i] & 0x80) >> 7
                result[i] = ((L[i] << 1) | carry) & 0xFF
                carry = new_carry
            return bytes(result)
    
    def _get_k1_details(self, L):
        msb = L[0] & 0x80
        if msb:
            return f'MSB(L)=1, so K1 = (L << 1) ⊕ 0x87 = {self._generate_subkey(L).hex()}'
        else:
            return f'MSB(L)=0, so K1 = (L << 1) = {self._generate_subkey(L).hex()}'
    
    def _get_k2_details(self, K1):
        msb = K1[0] & 0x80
        if msb:
            return f'MSB(K1)=1, so K2 = (K1 << 1) ⊕ 0x87'
        else:
            return f'MSB(K1)=0, so K2 = (K1 << 1)'
    
    def _split_into_blocks(self, data, block_size):
        """Split data into blocks"""
        return [data[i:i+block_size] for i in range(0, len(data), block_size)]