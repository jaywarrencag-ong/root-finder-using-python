def regula_falsi(f, a, b, tol=1e-6, max_iter=100, num_intervals=10):
    """
    Regula Falsi (False Position) method that can find multiple roots by scanning subintervals.
    
    Args:
        f: Function to find roots for
        a: Left boundary of interval
        b: Right boundary of interval
        tol: Tolerance for convergence
        max_iter: Maximum iterations per subinterval
        num_intervals: Number of subintervals to scan
    """
    roots = []
    table_data = []
    
    # Divide the main interval into subintervals
    subinterval_size = (b - a) / num_intervals
    
    for i in range(num_intervals):
        x1 = a + i * subinterval_size
        x2 = x1 + subinterval_size
        
        # Skip if no sign change in this subinterval
        if f(x1) * f(x2) >= 0:
            continue
            
        # Apply regula falsi to this subinterval
        left, right = x1, x2
        fl, fr = f(left), f(right)
        
        for iteration in range(max_iter):
            # Calculate the next approximation
            c = (left * fr - right * fl) / (fr - fl)
            fc = f(c)
            
            table_data.append({
                "Subinterval": f"[{x1:.2f}, {x2:.2f}]",
                "Iteration": iteration + 1,
                "a": round(left, 6),
                "b": round(right, 6),
                "c": round(c, 6),
                "f(c)": f"{fc:.4e}"
            })
            
            if abs(fc) < tol:
                # Check if this root is unique
                is_unique = True
                for existing_root in roots:
                    if abs(c - existing_root) < tol:
                        is_unique = False
                        break
                if is_unique:
                    roots.append(round(c, 6))
                break
                
            # Update the interval
            if fl * fc < 0:
                right = c
                fr = fc
            else:
                left = c
                fl = fc
                
            # Check if interval is too small
            if abs(right - left) < tol:
                break
                
    return roots, table_data