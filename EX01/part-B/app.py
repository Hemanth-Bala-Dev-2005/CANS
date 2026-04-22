from flask import Flask, request, jsonify, send_from_directory
import math

app = Flask(__name__)

# ============================================
# EULER'S TOTIENT FUNCTION & FACTORIZATION
# ============================================

def factorize(n):
    """Factorize n into prime factors with steps"""
    steps = []
    original_n = n
    factors = {}
    
    steps.append({
        'step': 1,
        'title': 'Starting Factorization',
        'description': f'Factorizing n = {n}'
    })
    
    # Handle factor 2
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    if count > 0:
        factors[2] = count
        steps.append({
            'step': len(steps) + 1,
            'title': f'Found Factor 2',
            'description': f'{2}^{count}',
            'detail': f'Dividing by 2, count = {count}, remaining n = {n}'
        })
    
    # Handle odd factors
    p = 3
    while p * p <= n:
        count = 0
        while n % p == 0:
            count += 1
            n //= p
        if count > 0:
            factors[p] = count
            steps.append({
                'step': len(steps) + 1,
                'title': f'Found Factor {p}',
                'description': f'{p}^{count}',
                'detail': f'Dividing by {p}, count = {count}, remaining n = {n}'
            })
        p += 2
    
    # If remaining n is > 1, it's a prime factor
    if n > 1:
        factors[n] = 1
        steps.append({
            'step': len(steps) + 1,
            'title': f'Found Factor {n}',
            'description': f'{n}^1',
            'detail': f'Remaining prime factor: {n}'
        })
    
    # Final result
    factor_str = ' × '.join([f'{p}^{exp}' if exp > 1 else str(p) for p, exp in factors.items()])
    steps.append({
        'step': len(steps) + 1,
        'title': 'Prime Factorization Complete',
        'description': f'{original_n} = {factor_str}',
        'detail': f'Prime factors: {list(factors.keys())}'
    })
    
    return factors, steps


def euler_phi(n):
    """Calculate Euler's totient function φ(n)"""
    if n == 1:
        return 1
    
    factors, _ = factorize(n)
    result = n
    for p in factors:
        result = result * (p - 1) // p
    return result


def mod_pow(base, exp, mod):
    """Modular exponentiation using fast exponentiation"""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result


def is_primitive_root(g, n, phi, prime_factors):
    """Check if g is a primitive root modulo n"""
    # Test g^(phi/p) mod n for each prime factor p of phi
    for p in prime_factors:
        exp = phi // p
        result = mod_pow(g, exp, n)
        if result == 1:
            return False, f'g^{{{phi}/{p}}} ≡ {result} (mod {n}) - Not a primitive root'
    return True, 'All tests passed'


# ============================================
# PRIMITIVE ROOTS MODULO N
# ============================================

def find_primitive_roots(n):
    """Find all primitive roots modulo n"""
    steps = []
    
    # Step 1: Validate n
    steps.append({
        'step': 1,
        'title': 'Input Validation',
        'description': f'Checking if n = {n} has primitive roots',
        'detail': 'Valid n must be: 1, 2, 4, p^k, or 2p^k where p is an odd prime'
    })
    
    if n == 1:
        return {'error': 'n=1 has no primitive roots'}, steps
    if n == 2:
        return {
            'n': n,
            'phi': 1,
            'primitive_roots': [1],
            'steps': steps + [{
                'step': 2,
                'title': 'Special Case: n = 2',
                'description': 'For n = 2, φ(2) = 1',
                'detail': 'g = 1 is the only primitive root (trivially)'
            }]
        }
    if n == 4:
        return {
            'n': n,
            'phi': 2,
            'primitive_roots': [3],
            'steps': steps + [{
                'step': 2,
                'title': 'Special Case: n = 4',
                'description': 'For n = 4, φ(4) = 2',
                'detail': 'g = 3 is the primitive root (3² ≡ 1 mod 4, but 3¹ ≠ 1)'
            }]
        }
    
    # Check if n is of valid form: p^k or 2*p^k where p is odd prime
    valid = False
    n_type = ''
    
    if n % 2 == 0:
        m = n // 2
        if m > 2:
            # Check if m is p^k (odd prime power)
            temp = m
            is_prime_power = True
            prime = None
            for p in range(3, int(math.sqrt(temp)) + 1, 2):
                if temp % p == 0:
                    while temp % p == 0:
                        temp //= p
                    if temp == 1:
                        prime = p
                        is_prime_power = True
                    else:
                        is_prime_power = False
                    break
            if temp > 1 and is_prime_power:
                is_prime_power = True
            elif temp > 1:
                is_prime_power = False
                
            # Simple check for 2p^k
            if is_prime_power and m % 2 == 1:
                valid = True
                n_type = f'2 × p^k form (n/2 = {m})'
    
    # Check for odd prime power
    temp_n = n
    is_ppower = False
    if n % 2 == 1:
        for p in range(3, int(math.sqrt(n)) + 1, 2):
            if n % p == 0:
                while n % p == 0:
                    n //= p
                if n == 1:
                    is_ppower = True
                    n_type = f'p^k form'
                    break
                else:
                    break
    
    if n % 2 == 1 and is_ppower:
        valid = True
    
    if not valid:
        return {'error': f'n = {temp_n} does not have primitive roots (n must be 1, 2, 4, p^k, or 2p^k where p is odd prime)'}, steps
    
    steps.append({
        'step': 2,
        'title': 'Valid n Type',
        'description': f'n = {temp_n} is of valid form: {n_type}',
        'detail': 'Primitive roots exist for this n'
    })
    
    # Step 2: Calculate φ(n)
    phi = euler_phi(temp_n)
    steps.append({
        'step': 3,
        'title': "Euler's Totient Function",
        'description': f'φ({temp_n}) = {phi}',
        'detail': 'Number of integers in [1,n-1] coprime to n'
    })
    
    # Step 3: Factorize φ(n)
    prime_factors, factor_steps = factorize(phi)
    for fs in factor_steps:
        fs['step'] += len(steps)
    steps.extend(factor_steps[1:])  # Skip first step to avoid duplication
    
    prime_factor_list = list(prime_factors.keys())
    steps.append({
        'step': len(steps) + 1,
        'title': 'Prime Factors of φ(n)',
        'description': f'φ(n) = {phi} has prime factors: {prime_factor_list}',
        'detail': f'p₁ = {prime_factor_list[0]}, p₂ = {prime_factor_list[1] if len(prime_factor_list) > 1 else "N/A"}'
    })
    
    # Step 4: Find primitive roots
    primitive_roots = []
    candidates_tested = []
    
    # For n=2, only 1
    if temp_n == 2:
        return {
            'n': temp_n,
            'phi': phi,
            'primitive_roots': [1],
            'steps': steps
        }
    
    # For n=4, only 3
    if temp_n == 4:
        return {
            'n': temp_n,
            'phi': phi,
            'primitive_roots': [3],
            'steps': steps
        }
    
    candidates = list(range(2, temp_n))
    # Limit testing for large n
    max_test = min(50, len(candidates))
    
    for i, g in enumerate(candidates[:max_test]):
        test_details = []
        all_passed = True
        
        for p in prime_factor_list:
            exp = phi // p
            result = mod_pow(g, exp, temp_n)
            test_details.append({
                'factor': p,
                'exp': exp,
                'result': result,
                'is_one': result == 1
            })
            if result == 1:
                all_passed = False
                break
        
        candidates_tested.append({
            'candidate': g,
            'tests': test_details,
            'is_primitive': all_passed
        })
        
        if all_passed:
            primitive_roots.append(g)
            if len(primitive_roots) >= 10:  # Limit found roots for display
                break
    
    # Add testing steps to output
    steps.append({
        'step': len(steps) + 1,
        'title': 'Testing Candidates',
        'description': f'Testing g from 2 to {temp_n-1}',
        'detail': f'For each g, calculate g^(φ(n)/p) mod n for each prime factor p of φ(n)'
    })
    
    # Add detailed test results
    for ct in candidates_tested[:15]:  # Limit display
        status = '✓ PRIMITIVE ROOT' if ct['is_primitive'] else '✗ Not a primitive root'
        steps.append({
            'step': len(steps) + 1,
            'title': f'Testing g = {ct["candidate"]}',
            'description': status,
            'tests': ct['tests']
        })
        if ct['is_primitive']:
            break
    
    # Final results
    steps.append({
        'step': len(steps) + 1,
        'title': 'Primitive Roots Found',
        'description': f'All primitive roots modulo {temp_n}:',
        'detail': str(primitive_roots) if primitive_roots else 'None found'
    })
    
    return {
        'n': temp_n,
        'phi': phi,
        'prime_factors': prime_factors,
        'primitive_roots': primitive_roots,
        'candidates_tested': len(candidates_tested),
        'steps': steps
    }


# ============================================
# EXTENDED EUCLIDEAN ALGORITHM
# ============================================

def extended_gcd_step(a, b, steps=None, depth=0):
    """Extended Euclidean Algorithm with step-by-step output"""
    if steps is None:
        steps = []
    
    indent = '  ' * depth
    
    if b == 0:
        steps.append({
            'step': len(steps) + 1,
            'title': f'Base Case (depth {depth})',
            'description': f'b = 0, so gcd(a, b) = a = {a}',
            'detail': f'{indent}gcd({a}, 0) = |a| = {abs(a)}',
            'depth': depth,
            'a': a,
            'b': b,
            'q': None,
            'r': None,
            'coefficients': {'x': 1, 'y': 0}
        })
        return abs(a), 1, 0, steps
    
    # Store initial values
    a0, b0 = a, b
    
    steps.append({
        'step': len(steps) + 1,
        'title': f'Division Step (depth {depth})',
        'description': f'Divide {a} by {b}',
        'detail': f'{indent}Finding quotient q and remainder r',
        'depth': depth,
        'a': a,
        'b': b
    })
    
    q = a // b
    r = a % b
    
    steps.append({
        'step': len(steps) + 1,
        'title': f'Calculate Quotient & Remainder (depth {depth})',
        'description': f'{a} = {q} × {b} + {r}',
        'detail': f'{indent}q = {q}, r = {r}',
        'depth': depth,
        'a': a,
        'b': b,
        'q': q,
        'r': r
    })
    
    # Recursive call
    gcd, x1, y1, steps = extended_gcd_step(b, r, steps, depth + 1)
    
    # Calculate coefficients
    x = y1
    y = x1 - q * y1
    
    steps.append({
        'step': len(steps) + 1,
        'title': f'Update Coefficients (depth {depth})',
        'description': f'x = {x1}, y = {y1} - {q} × {x1} = {y}',
        'detail': f'{indent}Bézout coefficients: x = {x}, y = {y}',
        'depth': depth,
        'a': a,
        'b': b,
        'q': q,
        'r': r,
        'coefficients': {'x': x, 'y': y, 'x1': x1, 'y1': y1}
    })
    
    return gcd, x, y, steps


def extended_gcd(a, b):
    """Extended Euclidean Algorithm wrapper"""
    steps = []
    
    # Handle negative numbers
    orig_a, orig_b = a, b
    a = abs(a)
    b = abs(b)
    
    # Ensure a >= b
    if a < b:
        a, b = b, a
        swapped = True
    else:
        swapped = False
    
    steps.append({
        'step': 1,
        'title': 'Initial Setup',
        'description': f'Finding gcd({orig_a}, {orig_b})',
        'detail': f'Using absolute values: gcd({a}, {b})'
    })
    
    if swapped:
        steps.append({
            'step': 2,
            'title': 'Swapping Values',
            'description': 'Ensuring a ≥ b',
            'detail': f'Swapped to: gcd({a}, {b})'
        })
    
    if b == 0:
        steps.append({
            'step': 3,
            'title': 'Base Case',
            'description': f'gcd({a}, 0) = {a}',
            'detail': f'Bézout identity: {a} × 1 + 0 × 0 = {a}'
        })
        return {
            'a': orig_a,
            'b': orig_b,
            'gcd': a,
            'x': 1 if not swapped else 0,
            'y': 0,
            'steps': steps
        }
    
    gcd, x, y, algorithm_steps = extended_gcd(a, b)
    
    # Adjust for original sign and swap
    if swapped:
        x, y = y, x
    
    # Handle negative original values
    if orig_a < 0:
        x = -x
    if orig_b < 0:
        y = -y
    
    # Offset step numbers
    for step in algorithm_steps:
        step['step'] += len(steps)
    
    steps.extend(algorithm_steps)
    
    # Final result
    steps.append({
        'step': len(steps) + 1,
        'title': 'Final Result',
        'description': f'gcd({orig_a}, {orig_b}) = {gcd}',
        'detail': f'Bézout identity: {orig_a} × ({x}) + {orig_b} × ({y}) = {gcd}',
        'coefficients': {'x': x, 'y': y}
    })
    
    return {
        'a': orig_a,
        'b': orig_b,
        'gcd': gcd,
        'x': x,
        'y': y,
        'steps': steps
    }


# ============================================
# FLASK ROUTES
# ============================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/primitive-roots', methods=['POST'])
def primitive_roots():
    data = request.json
    n = data.get('n', 0)
    
    if n < 1:
        return jsonify({'error': 'Please enter a positive integer n ≥ 1'}), 400
    
    try:
        result, _ = find_primitive_roots(n)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/extended-gcd', methods=['POST'])
def egcd():
    data = request.json
    a = data.get('a', 0)
    b = data.get('b', 0)
    
    try:
        result = extended_gcd(a, b)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)