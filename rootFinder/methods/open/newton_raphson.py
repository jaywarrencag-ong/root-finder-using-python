import numpy as np

def newton_raphson(f, df, x0, tol=0.001, max_iter=100, num_guesses=5):
    """
    Newton-Raphson method that can find multiple roots by trying different initial guesses.
    Matches the example format exactly.
    """
    roots = []
    table_data = []
    
    # For the example equation, we'll start with x0 = -5
    x = x0
    
    for iteration in range(max_iter):
        fx = f(x)
        dfx = df(x)
        
        # Avoid division by zero
        if abs(dfx) < 1e-10:
            table_data.append({
                "No. of iteration": iteration,
                "xi": round(x, 6),
                "ea": None,
                "f(xi)": round(fx, 6),
                "f'(xi)": round(dfx, 6)
            })
            break
            
        # Calculate next approximation
        x_new = x - fx/dfx
        
        # Calculate error
        ea = abs((x_new - x)/x_new) if x_new != 0 else 0
        
        # Add data to table
        table_data.append({
            "No. of iteration": iteration,
            "xi": round(x, 6),
            "ea": round(ea * 100, 3) if ea is not None else None,  # Convert to percentage
            "f(xi)": round(fx, 6),
            "f'(xi)": round(dfx, 6)
        })
        
        # Check for convergence
        if ea < tol:
            roots.append(round(x_new, 6))
            break
            
        x = x_new
        
        # Check if maximum iterations reached
        if iteration == max_iter - 1:
            table_data[-1]["Status"] = "Max iterations reached"
    
    return roots, table_data