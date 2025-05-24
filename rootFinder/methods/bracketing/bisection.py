import numpy as np

def bisection_method(f, a, b, tol=0.5, max_iter=50):
    """
    Implements the bisection method for finding roots
    Parameters:
        f: function to find roots for
        a, b: interval endpoints
        tol: tolerance (default 0.5%)
        max_iter: maximum number of iterations (default 50)
    Returns:
        roots: list of found roots
        table_data: list of dictionaries containing iteration data
    """
    if f(a) * f(b) > 0:
        return [], []

    table_data = []
    roots = []
    iteration = 1
    x_old = None
    
    while iteration <= max_iter:
        c = (a + b) / 2  # Calculate midpoint
        fc = f(c)
        fa = f(a)
        fb = f(b)
        
        # Calculate absolute relative approximate error if possible
        error = 0
        if x_old is not None:
            error = abs((c - x_old) / c) * 100  # as percentage
        
        # Determine which subinterval contains the root
        remark = ""
        if fa * fc < 0:
            remark = "1st subinterval"
            b = c
        else:
            remark = "2nd subinterval"
            a = c
            
        # Add iteration data to table with proper column order
        table_data.append({
            "Iteration": iteration,
            "xl": round(a, 7),
            "xr": round(c, 7),
            "xu": round(b, 7),
            "f(xl)": round(fa, 7),
            "f(xr)": round(fc, 7),
            "f(xu)": round(fb, 7),
            "|ea|%": round(error, 7),
            "f(xl)·f(xu)": "< 0" if fa * fb < 0 else "> 0",
            "Remark": remark
        })
        
        # Check for convergence
        if error < tol and iteration > 1:
            roots.append(round(c, 7))
            break
            
        x_old = c
        iteration += 1
        
        # Check if root is found (function value is close to zero)
        if abs(fc) < 1e-10:
            roots.append(round(c, 7))
            break
    
    return roots, table_data