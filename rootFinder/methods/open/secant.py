import numpy as np

def secant_method(f, x0, x1, tol=0.001, max_iter=100):
    """
    Secant method implementation matching the example format exactly.
    """
    roots = []
    table_data = []
    
    # Initial values
    xi_prev = x0  # 0.5 in example
    xi = x1      # 5.0 in example
    
    for iteration in range(max_iter):
        # Calculate function values
        f_prev = f(xi_prev)
        f_curr = f(xi)
        
        # Avoid division by zero
        if abs(f_curr - f_prev) < 1e-10:
            break
            
        # Calculate next approximation
        xi_next = xi - f_curr * (xi - xi_prev) / (f_curr - f_prev)
        
        # Calculate error
        ea = abs((xi_next - xi)/xi_next) if xi_next != 0 else 0
        
        # Add data to table
        table_data.append({
            "Iteration Number": iteration + 1,
            "xi-1": round(xi_prev, 6),
            "xi": round(xi, 6),
            "xi+1": round(xi_next, 6),
            "ea": round(ea * 100, 3),
            "f(xi-1)": round(f_prev, 6),
            "f(xi)": round(f_curr, 6),
            "f(xi+1)": round(f(xi_next), 6)
        })
        
        # Check for convergence
        if ea < tol and abs(f(xi_next)) < tol:
            roots.append(round(xi_next, 6))
            break
            
        # Update values for next iteration
        xi_prev = xi
        xi = xi_next
        
        # Check if maximum iterations reached
        if iteration == max_iter - 1:
            table_data[-1]["Status"] = "Max iterations reached"
    
    return roots, table_data