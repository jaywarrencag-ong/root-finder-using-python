import numpy as np

def graphical_method(f, x_min=-2, x_max=2, step=0.2):
    """
    Graphical method for finding roots with periodic function detection.
    
    Args:
        f: Function to find roots for
        x_min: Starting x value
        x_max: Ending x value
        step: Step size between x values
    
    Returns:
        tuple: (roots, table_data, is_periodic)
    """
    if step <= 0:
        raise ValueError("Step size must be positive")
        
    x_vals = np.arange(x_min, x_max + step/2, step)  # step/2 ensures we include x_max
    y_vals = f(x_vals)
    roots = []
    table_data = []
    
    # Check for periodicity
    zero_crossings = []
    
    # Create table entries for each x value
    for i, x in enumerate(x_vals):
        fx = f(x)
        table_data.append({
            "x": round(x, 3),
            "f(x)": round(fx, 8)
        })
        
        # Check for sign changes between consecutive points
        if i > 0:
            if y_vals[i-1] * y_vals[i] <= 0:
                # Linear interpolation to find root
                x_root = x_vals[i-1] - y_vals[i-1] * (x_vals[i] - x_vals[i-1])/(y_vals[i] - y_vals[i-1])
                roots.append(round(x_root, 6))
                zero_crossings.append(i)
    
    # Analyze zero crossings for periodicity
    is_periodic = False
    period = None
    
    if len(zero_crossings) > 4:  # Need at least 5 roots to check periodicity
        intervals = np.diff(zero_crossings)
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # If standard deviation is small compared to average, likely periodic
        if std_interval < avg_interval * 0.1:
            is_periodic = True
            period = avg_interval * step
            
            # Add periodicity information to table
            table_data.append({
                "x": "Period",
                "f(x)": f"{period:.6f}"
            })
    
    return roots, table_data, is_periodic, period