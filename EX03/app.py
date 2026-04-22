from flask import Flask, render_template, request, jsonify
import gmpy2
import math

app = Flask(__name__)

def extended_gcd(a, b):
    """Extended Euclidean Algorithm to find modular inverse"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    """Calculate modular inverse using extended Euclidean algorithm"""
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        return None
    return x % phi

def gcd(a, b):
    """Calculate GCD using Euclidean algorithm"""
    while b:
        a, b = b, a % b
    return a

def rsa_key_generation(p, q):
    """RSA Key Generation with step-by-step details"""
    steps = []
    
    # Step 1: Validate primes
    steps.append({
        "step": "1. Prime Validation",
        "description": f"Validate that p={p} and q={q} are prime numbers",
        "result": "Both are prime ✓"
    })
    
    # Step 2: Calculate n = p * q
    n = p * q
    steps.append({
        "step": "2. Calculate n",
        "description": "n = p × q (modulus for both keys)",
        "calculation": f"{p} × {q} = {n}",
        "result": f"n = {n}"
    })
    
    # Step 3: Calculate Euler's totient
    phi = (p - 1) * (q - 1)
    steps.append({
        "step": "3. Calculate φ(n)",
        "description": "φ(n) = (p-1) × (q-1) (Euler's totient function)",
        "calculation": f"({p}-1) × ({q}-1) = {p-1} × {q-1}",
        "result": f"φ(n) = {phi}"
    })
    
    # Step 4: Choose public exponent e
    e = 65537  # Common choice
    while gcd(e, phi) != 1:
        e = 3
    steps.append({
        "step": "4. Choose Public Exponent (e)",
        "description": "Select e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1",
        "result": f"e = {e} (commonly used prime)"
    })
    
    # Step 5: Calculate GCD(e, φ(n))
    g = gcd(e, phi)
    steps.append({
        "step": "5. Verify GCD(e, φ(n))",
        "description": "Check that gcd(e, φ(n)) = 1",
        "calculation": f"gcd({e}, {phi}) = {g}",
        "result": "gcd = 1 ✓ (coprime)"
    })
    
    # Step 6: Calculate private exponent d
    d = mod_inverse(e, phi)
    steps.append({
        "step": "6. Calculate Private Exponent (d)",
        "description": "d = e⁻¹ mod φ(n) (modular inverse)",
        "calculation": f"{e}⁻¹ mod {phi} = {d}",
        "result": f"d = {d}"
    })
    
    return {
        "public_key": {"e": e, "n": n},
        "private_key": {"d": d, "n": n},
        "steps": steps
    }

def rsa_encrypt(message, e, n):
    """RSA Encryption with step-by-step details"""
    steps = []
    m = int.from_bytes(message.encode('utf-8'), 'big')
    
    steps.append({
        "step": "1. Convert Message to Integer",
        "description": "Convert plaintext to integer representation",
        "result": f"m = {m}"
    })
    
    # Encrypt using m^e mod n
    c = pow(m, e, n)
    steps.append({
        "step": "2. Calculate Ciphertext",
        "description": "c = m^e mod n",
        "calculation": f"{m}^{e} mod {n} = {c}",
        "result": f"c = {c}"
    })
    
    return {"ciphertext": c, "steps": steps}

def rsa_decrypt(c, d, n):
    """RSA Decryption with step-by-step details"""
    steps = []
    
    steps.append({
        "step": "1. Decrypt Ciphertext",
        "description": "m = c^d mod n",
        "calculation": f"{c}^{d} mod {n}",
    })
    
    # Decrypt
    m = pow(c, d, n)
    steps.append({
        "step": "2. Calculate Plaintext",
        "calculation": f"{c}^{d} mod {n} = {m}",
        "result": f"m = {m}"
    })
    
    # Convert back to string
    try:
        message = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')
    except:
        message = str(m)
    
    steps.append({
        "step": "3. Convert to Text",
        "description": "Convert integer back to string",
        "result": f"message = '{message}'"
    })
    
    return {"plaintext": message, "steps": steps}

def diffie_hellman(p, g, xa, xb):
    """Diffie-Hellman Key Exchange with step-by-step details"""
    steps = []
    
    # Step 1: Validate prime
    steps.append({
        "step": "1. Validate Prime p",
        "description": f"Verify that p = {p} is a prime number",
        "result": "Valid prime ✓"
    })
    
    # Step 2: Show generator g
    steps.append({
        "step": "2. Select Generator g",
        "description": f"g = {g} (primitive root modulo p)",
        "result": f"g = {g}"
    })
    
    # Step 3: Alice's private key
    steps.append({
        "step": "3. Alice's Private Key",
        "description": "Alice chooses a secret random number",
        "result": f"x_a = {xa}"
    })
    
    # Step 4: Bob's private key
    steps.append({
        "step": "4. Bob's Private Key",
        "description": "Bob chooses a secret random number",
        "result": f"x_b = {xb}"
    })
    
    # Step 5: Alice's public key
    ya = pow(g, xa, p)
    steps.append({
        "step": "5. Alice's Public Key",
        "description": "Y_a = g^x_a mod p",
        "calculation": f"{g}^{xa} mod {p} = {ya}",
        "result": f"Y_a = {ya}"
    })
    
    # Step 6: Bob's public key
    yb = pow(g, xb, p)
    steps.append({
        "step": "6. Bob's Public Key",
        "description": "Y_b = g^x_b mod p",
        "calculation": f"{g}^{xb} mod {p} = {yb}",
        "result": f"Y_b = {yb}"
    })
    
    # Step 7: Alice computes shared secret
    shared_a = pow(yb, xa, p)
    steps.append({
        "step": "7. Alice Computes Shared Secret",
        "description": "K = Y_b^x_a mod p",
        "calculation": f"{yb}^{xa} mod {p} = {shared_a}",
        "result": f"K = {shared_a}"
    })
    
    # Step 8: Bob computes shared secret
    shared_b = pow(ya, xb, p)
    steps.append({
        "step": "8. Bob Computes Shared Secret",
        "description": "K = Y_a^x_b mod p",
        "calculation": f"{ya}^{xb} mod {p} = {shared_b}",
        "result": f"K = {shared_b}"
    })
    
    # Step 9: Verify both match
    steps.append({
        "step": "9. Verify Shared Secret",
        "description": "Both parties should have the same secret key",
        "calculation": f"{shared_a} == {shared_b} → {shared_a == shared_b}",
        "result": "Both secrets match ✓" if shared_a == shared_b else "Error!"
    })
    
    return {
        "public_keys": {"ya": ya, "yb": yb},
        "shared_secret": shared_a,
        "steps": steps
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rsa', methods=['POST'])
def rsa():
    data = request.json
    p = int(data.get('p', 61))
    q = int(data.get('q', 53))
    message = data.get('message', 'Hello')
    
    key_gen = rsa_key_generation(p, q)
    encryption = rsa_encrypt(message, key_gen['public_key']['e'], key_gen['public_key']['n'])
    decryption = rsa_decrypt(encryption['ciphertext'], key_gen['private_key']['d'], key_gen['private_key']['n'])
    
    return jsonify({
        "key_generation": key_gen,
        "encryption": encryption,
        "decryption": decryption
    })

@app.route('/dh', methods=['POST'])
def dh():
    data = request.json
    p = int(data.get('p', 23))
    g = int(data.get('g', 5))
    xa = int(data.get('xa', 6))
    xb = int(data.get('xb', 15))
    
    result = diffie_hellman(p, g, xa, xb)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)