import numpy as np

def incremental_search(f, a, b, step=0.1):
    roots = []
    table_data = []
    x = a
    
    iteration = 1
    while x <= b:
        x_next = x + step
        try:
            fx = f(x)
            fx_next = f(x_next)
            
            # Handle undefined or infinite values in function evaluation
            if np.isnan(fx) or np.isinf(fx) or np.isnan(fx_next) or np.isinf(fx_next):
                product = None
                remark = "Function is undefined or infinite at this point"
            else:
                product = fx * fx_next
                remark = "No root in this interval" if product > 0 else "A root exists in this interval"
            
            table_data.append({
                "i": iteration,
                "xi": round(x, 3),
                "f(xi)": "Undefined or Infinite" if np.isnan(fx) or np.isinf(fx) else round(fx, 6),
                "f(xi)*f(xi+1)": "Undefined or Infinite" if product is None else round(product, 6),
                "Remark": remark
            })
            
            # Only try to find root if values are valid and sign changes
            if product is not None and product <= 0:
                try:
                    # Check for division by zero
                    denominator = fx_next - fx
                    if abs(denominator) < 1e-10:
                        root = (x + x_next) / 2  # Use midpoint if slope is too small
                    else:
                        root = x - step * fx/denominator
                    
                    # Verify the root is valid
                    if not (np.isnan(root) or np.isinf(root)):
                        roots.append(round(root, 6))
                except:
                    pass  # Skip if root calculation fails
                    
        except:
            # Handle any errors in function evaluation
            table_data.append({
                "i": iteration,
                "xi": round(x, 3),
                "f(xi)": "Unable to evaluate function",
                "f(xi)*f(xi+1)": "Unable to evaluate function",
                "Remark": "Function evaluation failed at this point"
            })
        
        x = x_next
        iteration += 1
    
    return roots, table_data