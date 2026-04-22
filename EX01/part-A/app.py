from flask import Flask, request, jsonify, send_from_directory
import re

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ============================================
# CAESAR CIPHER
# ============================================

def caesar_encrypt(plaintext, shift):
    """
    Encrypt using Caesar cipher with step-by-step output
    c = (p + k) mod 26
    """
    steps = []
    shift = int(shift) % 26
    
    # Clean and prepare plaintext
    plaintext = plaintext.upper()
    clean_text = re.sub(r'[^A-Z]', '', plaintext)
    
    steps.append({
        'step': 1,
        'title': 'Input Preparation',
        'description': f'Original text: "{plaintext}"\nShift value: {shift}',
        'detail': f'Cleaned text (letters only): "{clean_text}"'
    })
    
    # Step 2: Show each letter transformation
    transformations = []
    encrypted = []
    
    for i, char in enumerate(clean_text):
        if char == ' ':
            continue
        original_pos = ord(char) - ord('A')
        encrypted_pos = (original_pos + shift) % 26
        encrypted_char = chr(encrypted_pos + ord('A'))
        encrypted.append(encrypted_char)
        
        transformations.append({
            'letter': char,
            'position': original_pos,
            'shift': shift,
            'new_position': encrypted_pos,
            'result': encrypted_char
        })
    
    steps.append({
        'step': 2,
        'title': 'Letter Shifting Process',
        'description': 'For each letter: new_pos = (old_pos + shift) mod 26',
        'transformations': transformations
    })
    
    final_result = ''.join(encrypted)
    
    steps.append({
        'step': 3,
        'title': 'Final Encrypted Message',
        'description': f'Concatenating all shifted letters:',
        'detail': final_result
    })
    
    return {
        'original': clean_text,
        'encrypted': final_result,
        'shift': shift,
        'steps': steps
    }

# ============================================
# PLAYFAIR CIPHER
# ============================================

def create_playfair_matrix(key):
    """Create 5x5 Playfair matrix from key"""
    key = key.upper().replace('J', 'I')
    key = re.sub(r'[^A-Z]', '', key)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_key = []
    for char in key:
        if char not in seen:
            seen.add(char)
            unique_key.append(char)
    
    # Create alphabet (excluding J)
    alphabet = [chr(i) for i in range(ord('A'), ord('Z') + 1) if chr(i) != 'J']
    
    # Build matrix
    matrix_chars = unique_key + [c for c in alphabet if c not in seen]
    matrix = [matrix_chars[i:i+5] for i in range(0, 25, 5)]
    
    return matrix

def get_letter_coords(matrix, letter):
    """Get row and column of a letter in the matrix"""
    for row in range(5):
        for col in range(5):
            if matrix[row][col] == letter:
                return row, col
    return -1, -1

def playfair_encrypt(plaintext, key):
    """
    Encrypt using Playfair cipher with step-by-step output
    """
    steps = []
    
    # Step 1: Key processing
    key_processed = key.upper().replace('J', 'I')
    key_processed = re.sub(r'[^A-Z]', '', key_processed)
    
    steps.append({
        'step': 1,
        'title': 'Key Processing',
        'description': f'Original key: "{key}"',
        'detail': f'Processed key (uppercase, J→I, no spaces): "{key_processed}"'
    })
    
    # Step 2: Create matrix
    matrix = create_playfair_matrix(key)
    
    # Create coordinate map
    coord_map = {}
    for r in range(5):
        for c in range(5):
            coord_map[matrix[r][c]] = (r, c)
    
    matrix_display = []
    for r in range(5):
        row_data = []
        for c in range(5):
            row_data.append({'letter': matrix[r][c], 'row': r, 'col': c})
        matrix_display.append(row_data)
    
    steps.append({
        'step': 2,
        'title': 'Playfair Matrix Creation',
        'description': 'Key letters (no duplicates) + remaining alphabet (skip J)',
        'matrix': matrix_display
    })
    
    # Step 3: Prepare plaintext - create digraphs
    plaintext = plaintext.upper().replace('J', 'I')
    clean_text = re.sub(r'[^A-Z]', '', plaintext)
    
    # Split into digraphs, handling double letters
    digraphs = []
    i = 0
    while i < len(clean_text):
        if i + 1 < len(clean_text) and clean_text[i] == clean_text[i + 1]:
            # Double letter - insert X
            digraphs.append([clean_text[i], 'X'])
            i += 1
        elif i + 1 < len(clean_text):
            digraphs.append([clean_text[i], clean_text[i + 1]])
            i += 2
        else:
            # Odd length - pad with X
            digraphs.append([clean_text[i], 'X'])
            i += 1
    
    padding_info = []
    for d in digraphs:
        padding_info.append({'pair': f'{d[0]}{d[1]}', 'note': 'Added X' if d[1] == 'X' and len(clean_text) % 2 != 0 and d == digraphs[-1] else ''})
    
    steps.append({
        'step': 3,
        'title': 'Digraph Formation',
        'description': f'Split text into pairs, add X for doubles or odd length',
        'digraphs': padding_info
    })
    
    # Step 4: Encrypt each digraph
    encryptions = []
    encrypted = []
    
    for pair in digraphs:
        a, b = pair[0], pair[1]
        r1, c1 = coord_map[a]
        r2, c2 = coord_map[b]
        
        rule = ''
        new_a, new_b = '', ''
        
        if r1 == r2:
            # Same row - wrap around
            new_a = matrix[r1][(c1 + 1) % 5]
            new_b = matrix[r2][(c2 + 1) % 5]
            rule = 'Same row → shift right (wrap)'
        elif c1 == c2:
            # Same column - wrap around
            new_a = matrix[(r1 + 1) % 5][c1]
            new_b = matrix[(r2 + 1) % 5][c2]
            rule = 'Same column → shift down (wrap)'
        else:
            # Rectangle - corner swap
            new_a = matrix[r1][c2]
            new_b = matrix[r2][c1]
            rule = 'Rectangle → opposite corners'
        
        encrypted.append(new_a + new_b)
        
        encryptions.append({
            'pair': f'{a}{b}',
            'a_coords': f'({r1},{c1})',
            'b_coords': f'({r2},{c2})',
            'rule': rule,
            'result': f'{new_a}{new_b}'
        })
    
    steps.append({
        'step': 4,
        'title': 'Encryption Rules Applied',
        'description': 'Same row: right shift | Same column: down shift | Rectangle: corner swap',
        'encryptions': encryptions
    })
    
    final_result = ''.join(encrypted)
    
    steps.append({
        'step': 5,
        'title': 'Final Encrypted Message',
        'description': 'Concatenating all encrypted pairs:',
        'detail': final_result
    })
    
    return {
        'original': clean_text,
        'encrypted': final_result,
        'key': key,
        'steps': steps
    }

# ============================================
# HILL CIPHER
# ============================================

def matrix_multiply_mod26(matrix, vector, mod=26):
    """Multiply matrix by vector, return result modulo mod"""
    result = []
    for row in matrix:
        value = sum(row[i] * vector[i] for i in range(len(vector))) % mod
        result.append(value)
    return result

def mod_inverse(a, m):
    """Find modular multiplicative inverse"""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return -1

def matrix_inverse_2x2(matrix, mod=26):
    """Find inverse of 2x2 matrix modulo 26"""
    det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % mod
    det_inv = mod_inverse(det, mod)
    
    if det_inv == -1:
        return None
    
    inv = [
        [matrix[1][1], -matrix[0][1]],
        [-matrix[1][0], matrix[0][0]]
    ]
    
    for i in range(2):
        for j in range(2):
            inv[i][j] = ((inv[i][j] % mod) + mod) % mod
    
    for i in range(2):
        for j in range(2):
            inv[i][j] = (inv[i][j] * det_inv) % mod
    
    return inv

def hill_encrypt(plaintext, key_str):
    """
    Encrypt using Hill cipher (2x2) with step-by-step output
    """
    steps = []
    
    # Parse key matrix
    key_values = [int(x.strip()) for x in key_str.split(',')]
    key_matrix = [[key_values[0], key_values[1]], [key_values[2], key_values[3]]]
    
    steps.append({
        'step': 1,
        'title': 'Key Matrix',
        'description': 'Using 2x2 key matrix:',
        'matrix': key_matrix,
        'detail': 'Matrix:\n[[a, b], [c, d]]'
    })
    
    # Validate determinant
    det = (key_matrix[0][0] * key_matrix[1][1] - key_matrix[0][1] * key_matrix[1][0]) % 26
    
    steps.append({
        'step': 2,
        'title': 'Determinant Calculation',
        'description': f'det = (a×d - b×c) mod 26',
        'detail': f'det = ({key_matrix[0][0]}×{key_matrix[1][1]} - {key_matrix[0][1]}×{key_matrix[1][0]}) = {det} (mod 26)'
    })
    
    # Prepare plaintext
    plaintext = plaintext.upper()
    clean_text = re.sub(r'[^A-Z]', '', plaintext)
    
    # Pad if necessary
    while len(clean_text) % 2 != 0:
        clean_text += 'X'
    
    steps.append({
        'step': 3,
        'title': 'Message Preparation',
        'description': f'Convert letters to numbers (A=0, B=1, ..., Z=25)',
        'detail': f'Original: "{plaintext}" → Clean: "{clean_text}"',
        'padding': 'Padded with X' if len(clean_text) != len(re.sub(r'[^A-Z]', '', plaintext.upper())) else ''
    })
    
    # Convert to numbers
    number_conversion = []
    for char in clean_text:
        number_conversion.append({'letter': char, 'number': ord(char) - ord('A')})
    
    steps.append({
        'step': 4,
        'title': 'Letter to Number Conversion',
        'description': 'Convert each letter to its alphabetical index (A=0)',
        'conversions': number_conversion
    })
    
    # Encrypt in blocks of 2
    encryptions = []
    encrypted_letters = []
    
    for i in range(0, len(clean_text), 2):
        block = [clean_text[i], clean_text[i + 1]]
        vector = [ord(c) - ord('A') for c in block]
        
        # Matrix multiplication
        result = matrix_multiply_mod26(key_matrix, vector)
        
        # Convert back to letters
        letters = [chr(r + ord('A')) for r in result]
        
        # Create step detail
        calc_detail = f'[{block[0]},{block[1]}] → [{vector[0]},{vector[1]}]'
        mult_detail = f'[{key_matrix[0][0]},{key_matrix[0][1]}] · [{vector[0]}] = {result[0]}'
        mult_detail += f'\n[{key_matrix[1][0]},{key_matrix[1][1]}] · [{vector[1]}] = {result[1]}'
        
        encryptions.append({
            'block': f'{block[0]}{block[1]}',
            'numbers': vector,
            'multiplication': mult_detail,
            'mod_result': result,
            'letters': ''.join(letters)
        })
        
        encrypted_letters.extend(letters)
    
    steps.append({
        'step': 5,
        'title': 'Matrix Multiplication',
        'description': 'For each 2-letter block: result = (key_matrix × vector) mod 26',
        'encryptions': encryptions
    })
    
    final_result = ''.join(encrypted_letters)
    
    steps.append({
        'step': 6,
        'title': 'Final Encrypted Message',
        'description': 'Convert numbers back to letters:',
        'detail': final_result
    })
    
    return {
        'original': clean_text,
        'encrypted': final_result,
        'key': key_matrix,
        'steps': steps
    }

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/caesar', methods=['POST'])
def caesar():
    data = request.json
    plaintext = data.get('plaintext', '')
    shift = data.get('shift', 3)
    
    if not plaintext:
        return jsonify({'error': 'Please enter plaintext'}), 400
    
    try:
        result = caesar_encrypt(plaintext, shift)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/playfair', methods=['POST'])
def playfair():
    data = request.json
    plaintext = data.get('plaintext', '')
    key = data.get('key', '')
    
    if not plaintext:
        return jsonify({'error': 'Please enter plaintext'}), 400
    if not key:
        return jsonify({'error': 'Please enter a key'}), 400
    
    try:
        result = playfair_encrypt(plaintext, key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/hill', methods=['POST'])
def hill():
    data = request.json
    plaintext = data.get('plaintext', '')
    key = data.get('key', '')
    
    if not plaintext:
        return jsonify({'error': 'Please enter plaintext'}), 400
    if not key:
        return jsonify({'error': 'Please enter a key'}), 400
    
    # Validate key format
    try:
        key_values = [int(x.strip()) for x in key.split(',')]
        if len(key_values) != 4:
            return jsonify({'error': 'Key must be 4 numbers (2x2 matrix): e.g., "3,2,1,5"'}), 400
    except:
        return jsonify({'error': 'Invalid key format. Use comma-separated numbers: "3,2,1,5"'}), 400
    
    try:
        result = hill_encrypt(plaintext, key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)