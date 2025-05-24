import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

# Import all methods
from methods.bracketing.bisection import bisection_method
from methods.bracketing.regula_falsi import regula_falsi
from methods.open.newton_raphson import newton_raphson
from methods.open.secant import secant_method
from methods.basic.graphical import graphical_method
from methods.basic.incremental import incremental_search

# Light theme colors - High Contrast Modern
BG_COLOR = '#FFFFFF'          # Pure white background
TEXT_COLOR = '#000000'        # Black text for maximum readability
BUTTON_COLOR = '#E3F2FD'      # Light blue buttons (soft)
PLOT_BG = '#FFFFFF'           # White plot background

# Table color scheme
TABLE_COLORS = {
    'header_bg': '#2196F3',   # Bright blue header
    'header_fg': '#FFFFFF',   # White text (high contrast)
    'normal_bg': '#FFFFFF',   # White cells
    'normal_fg': '#000000',   # Black text
    'root_bg': '#E3F2FD',     # Light blue highlight
    'root_fg': '#0D47A1',     # Dark blue text for roots
    'undefined_bg': '#FFEBEE', # Light red background for errors
    'undefined_fg': '#B71C1C', # Dark red text
    'tooltip_bg': '#424242',   # Dark gray tooltip
    'tooltip_fg': '#FFFFFF',   # White tooltip text
    'border': '#BDBDBD',       # Light gray border
    'hover': '#BBDEFB',        # Light blue hover
    'success': '#2E7D32',      # Dark green (success)
    'warning': '#FF8F00',      # Orange (warning)
    'error': '#C62828',        # Dark red (error)
}

class CustomToolbar(NavigationToolbar2Tk):
    """Custom toolbar with additional features"""
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        
        # Add custom buttons
        self.add_spacer()
        
        # Add reset view button
        self.reset_button = ttk.Button(self, text="Reset View", 
                                     command=self.reset_view)
        self.reset_button.pack(side=tk.LEFT, padx=2)
        
        # Add auto-update toggle
        self.auto_update_var = tk.BooleanVar(value=True)
        self.auto_update_check = ttk.Checkbutton(
            self, text="Auto-update", 
            variable=self.auto_update_var)
        self.auto_update_check.pack(side=tk.LEFT, padx=2)
    
    def add_spacer(self):
        """Add space between built-in and custom buttons"""
        separator = ttk.Frame(self, width=20)
        separator.pack(side=tk.LEFT)
    
    def reset_view(self):
        """Reset to original view"""
        self.canvas.figure.axes[0].autoscale()
        self.canvas.draw()

class RootFinderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Root Finder Toolkit")
        self.master.state('zoomed')
        self.master.configure(bg=BG_COLOR)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TEntry', fieldbackground='#333366')
        self.style.map('TButton', background=[('active', BUTTON_COLOR)])
        self.style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR)
        self.style.configure('TCombobox', fieldbackground='#333366', background=BUTTON_COLOR)
        
        # Custom button styles
        self.style.configure('Numpad.TButton', 
                           padding=5, 
                           width=8, 
                           font=('Helvetica', 10))
        self.style.configure('Function.TButton', 
                           padding=5, 
                           width=12, 
                           font=('Helvetica', 10))
        self.style.configure('Extra.TButton', 
                           padding=5, 
                           width=10, 
                           font=('Helvetica', 10))
        
        # Main container split into left and right
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for input and controls
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right frame for table
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable table frame
        self.table_container = ttk.Frame(self.right_frame)
        self.table_container.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.table_container)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = ttk.Scrollbar(self.table_container, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for scrolling
        self.table_canvas = tk.Canvas(self.table_container, bg=BG_COLOR,
                                    yscrollcommand=self.v_scrollbar.set,
                                    xscrollcommand=self.h_scrollbar.set)
        self.table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.v_scrollbar.config(command=self.table_canvas.yview)
        self.h_scrollbar.config(command=self.table_canvas.xview)
        
        # Create frame for table content
        self.table_frame = ttk.Frame(self.table_canvas)
        self.table_canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        
        # Move all input controls to left frame
        ttk.Label(self.left_frame, text="Enter Equation (use 'x' as variable):", 
                 font=('Helvetica', 12)).pack(pady=5)
        self.equation_entry = ttk.Entry(self.left_frame, width=50, font=('Helvetica', 12))
        self.equation_entry.pack(pady=5)
        
        # Create main input frame with better organization
        self.input_frame = ttk.Frame(self.left_frame)
        self.input_frame.pack(pady=10)

        # Function categories
        function_categories = {
            'Trigonometric': [
                ('sin(x)', 'Sine function'),
                ('cos(x)', 'Cosine function'),
                ('tan(x)', 'Tangent function'),
                ('π', 'Pi (3.14159...)')
            ],
            'Exponential & Log': [
                ('e^x', 'Exponential function'),
                ('ln(x)', 'Natural logarithm'),
                ('log(x)', 'Base-10 logarithm'),
                ('√x', 'Square root')
            ],
            'Power & Basic': [
                ('x^2', 'Square'),
                ('x^3', 'Cube'),
                ('x^n', 'Power n'),
                ('|x|', 'Absolute value')
            ]
        }

        # Create tabs for function categories
        self.function_tabs = ttk.Notebook(self.input_frame)
        self.function_tabs.pack(fill=tk.X, padx=5, pady=5)

        # Create function category tabs
        for category, functions in function_categories.items():
            category_frame = ttk.Frame(self.function_tabs)
            self.function_tabs.add(category_frame, text=category)
            
            for i, (func, tooltip) in enumerate(functions):
                btn = ttk.Button(
                    category_frame,
                    text=func,
                    command=lambda f=func: self.insert_function(f),
                    style='Function.TButton'
                )
                btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='nsew')
                self.create_tooltip(btn, tooltip)
            
            # Configure grid for even spacing
            for i in range(2):
                category_frame.grid_columnconfigure(i, weight=1)

        # Enhanced numpad layout
        self.numpad_frame = ttk.Frame(self.input_frame)
        self.numpad_frame.pack(pady=5)

        # Numpad configuration
        numpad_layout = [
            [('(', 'Left parenthesis'), (')', 'Right parenthesis'), ('C', 'Clear all'), ('⌫', 'Backspace')],
            [('7', 'Seven'), ('8', 'Eight'), ('9', 'Nine'), ('/', 'Division')],
            [('4', 'Four'), ('5', 'Five'), ('6', 'Six'), ('*', 'Multiplication')],
            [('1', 'One'), ('2', 'Two'), ('3', 'Three'), ('-', 'Subtraction')],
            [('0', 'Zero'), ('.', 'Decimal point'), ('x', 'Variable x'), ('+', 'Addition')],
            [('=', 'Calculate'), ('Plot', 'Plot function')]
        ]

        # Create numpad buttons with improved styling
        for i, row in enumerate(numpad_layout):
            for j, (symbol, tooltip) in enumerate(row):
                # Special styling for different button types
                if symbol in ['C', '⌫']:
                    btn_style = 'Clear.TButton'
                    btn_width = 3
                elif symbol in ['=', 'Plot']:
                    btn_style = 'Action.TButton'
                    btn_width = 6
                    # Make these buttons span two columns
                    colspan = 2
                else:
                    btn_style = 'Numpad.TButton'
                    btn_width = 3
                    colspan = 1
                
                btn = ttk.Button(
                    self.numpad_frame,
                    text=symbol,
                    style=btn_style,
                    width=btn_width,
                    command=lambda s=symbol: self.numpad_click(s)
                )
                btn.grid(
                    row=i, 
                    column=j if symbol not in ['=', 'Plot'] else j*2,
                    columnspan=colspan,
                    padx=2, pady=2,
                    sticky='nsew'
                )
                self.create_tooltip(btn, tooltip)

        # Configure numpad grid
        for i in range(4):
            self.numpad_frame.grid_columnconfigure(i, weight=1)

        # Update the styles
        self.style.configure('Function.TButton',
            padding=5,
            width=10,
            font=('Helvetica', 10)
        )

        self.style.configure('Numpad.TButton',
            padding=5,
            width=3,
            font=('Helvetica', 12, 'bold')
        )

        self.style.configure('Clear.TButton',
            padding=5,
            width=3,
            font=('Helvetica', 10),
            foreground=TABLE_COLORS['error']
        )

        self.style.configure('Action.TButton',
            padding=5,
            width=6,
            font=('Helvetica', 12, 'bold'),
            foreground=TABLE_COLORS['success']
        )

        # Method selection
        ttk.Label(self.left_frame, text="Select Method:", font=('Helvetica', 12)).pack(pady=5)
        self.method_var = tk.StringVar()
        self.method_combobox = ttk.Combobox(self.left_frame, textvariable=self.method_var,
                                          values=["Graphical", "Incremental", "Bisection",
                                                  "Regula Falsi", "Newton Raphson", "Secant"],
                                          font=('Helvetica', 12))
        self.method_combobox.pack(pady=5)
        self.method_combobox.bind('<<ComboboxSelected>>', self.on_method_change)
        
        # Parameters frame
        self.params_frame = ttk.Frame(self.left_frame)
        self.params_frame.pack(pady=5)
        
        # Graph limits frame
        self.limits_frame = ttk.Frame(self.params_frame)
        self.limits_frame.pack(pady=5)
        
        # X-axis limits
        self.x_limits_frame = ttk.Frame(self.limits_frame)
        self.x_limits_frame.pack(pady=2)
        ttk.Label(self.x_limits_frame, text="X-axis limits:", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        self.x_min_var = tk.StringVar(value="-10")
        self.x_max_var = tk.StringVar(value="10")
        ttk.Entry(self.x_limits_frame, textvariable=self.x_min_var, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(self.x_limits_frame, text="to", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=2)
        ttk.Entry(self.x_limits_frame, textvariable=self.x_max_var, width=6).pack(side=tk.LEFT, padx=2)
        
        # Y-axis limits
        self.y_limits_frame = ttk.Frame(self.limits_frame)
        self.y_limits_frame.pack(pady=2)
        ttk.Label(self.y_limits_frame, text="Y-axis limits:", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        self.y_min_var = tk.StringVar(value="-10")
        self.y_max_var = tk.StringVar(value="10")
        ttk.Entry(self.y_limits_frame, textvariable=self.y_min_var, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(self.y_limits_frame, text="to", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=2)
        ttk.Entry(self.y_limits_frame, textvariable=self.y_max_var, width=6).pack(side=tk.LEFT, padx=2)
        
        # Method parameters frame
        self.method_params_frame = ttk.Frame(self.params_frame)
        self.method_params_frame.pack(pady=5)
        
        # Step size input
        self.step_size_frame = ttk.Frame(self.method_params_frame)
        self.step_size_frame.pack(pady=2)
        ttk.Label(self.step_size_frame, text="Step Size:", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        self.step_size_var = tk.StringVar(value="0.1")
        self.step_size_entry = ttk.Entry(self.step_size_frame, textvariable=self.step_size_var, width=8)
        self.step_size_entry.pack(side=tk.LEFT, padx=5)
        
        # Tolerance input
        self.tolerance_frame = ttk.Frame(self.method_params_frame)
        self.tolerance_frame.pack(pady=2)
        ttk.Label(self.tolerance_frame, text="Tolerance:", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        self.tolerance_var = tk.StringVar(value="0.001")
        self.tolerance_entry = ttk.Entry(self.tolerance_frame, textvariable=self.tolerance_var, width=8)
        self.tolerance_entry.pack(side=tk.LEFT, padx=5)
        
        # Auto scale checkbox
        self.auto_scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.limits_frame, text="Auto-scale Y-axis", 
                       variable=self.auto_scale_var,
                       command=self.toggle_y_limits).pack(pady=2)
        
        # Buttons
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.pack(pady=10)
        
        self.plot_button = ttk.Button(self.button_frame, text="Plot", command=self.plot)
        self.plot_button.pack(side=tk.LEFT, padx=5)
        
        self.help_button = ttk.Button(self.button_frame, text="Instructions", command=self.show_instructions)
        self.help_button.pack(side=tk.LEFT, padx=5)
        
        self.samples_button = ttk.Button(self.button_frame, text="Sample Equations", command=self.show_samples)
        self.samples_button.pack(side=tk.LEFT, padx=5)
        
        self.back_button = ttk.Button(self.button_frame, text="Return", command=self.clear_plot)
        self.back_button.pack(side=tk.LEFT, padx=5)

        # Create matplotlib figure with larger size
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.patch.set_facecolor(PLOT_BG)
        
        # Create plot area with grid
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Create canvas and add toolbar
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.draw()
        
        # Add custom toolbar
        self.toolbar = CustomToolbar(self.canvas, self.right_frame)
        self.toolbar.update()
        
        # Pack canvas and toolbar
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Connect events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # Add zoom rectangle selector
        self.zoom_selector = SpanSelector(
            self.ax, self.on_zoom_select, 'horizontal',
            useblit=True, interactive=True, drag_from_anywhere=True,
            props=dict(alpha=0.3, facecolor='red'))
        
        # Status bar for coordinates
        self.status_bar = ttk.Label(self.right_frame, text="", 
                                  font=('Helvetica', 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store original view limits
        self.original_xlim = None
        self.original_ylim = None

    def parse_equation(self):
        x = sp.symbols('x')
        try:
            eq = self.equation_entry.get()
            # Replace pi symbol with numpy's pi
            eq = eq.replace('π', 'pi')
            
            # Handle absolute value notation
            # First, ensure balanced absolute value symbols
            if eq.count('|') % 2 != 0:
                eq += '|'  # Close any unclosed absolute value
            
            # Replace absolute value notation with abs() function
            while '|' in eq:
                start = eq.find('|')
                end = eq.find('|', start + 1)
                if end == -1:
                    break
                expr_inside = eq[start+1:end]
                eq = eq[:start] + f'abs({expr_inside})' + eq[end+1:]
            
            eq = eq.replace('^', '**').replace('ln', 'log').replace('e', 'E')
            # Handle implied multiplication
            eq = ''.join([f'*{c}' if i>0 and c in 'x(pi' and eq[i-1].isdigit() else c 
                         for i, c in enumerate(eq)])
            expr = sp.sympify(eq)
            f = sp.lambdify(x, expr, modules=['numpy', {
                'log': np.log, 
                'E': np.e, 
                'pi': np.pi,
                'abs': np.abs  # Explicitly include numpy's abs function
            }])
            df = sp.lambdify(x, sp.diff(expr, x)) if "Newton" in self.method_var.get() else None
            return f, df, expr, x
        except Exception as e:
            messagebox.showerror("Error", 
                f"Invalid equation format.\nExample valid inputs:\n"
                f"Polynomial: 2*x^3 - x + 1\n"
                f"Trigonometric: sin(x) + cos(2x)\n"
                f"With π: sin(π*x) or x + π\n"
                f"With absolute value: |x| or |x^2 - 4|\n"
                f"Exponential: e^x - 10\n"
                f"Logarithmic: log(x) - 1")
            return None, None, None, None

    def clear_plot(self):
        self.ax.clear()
        self.ax.axis('off')
        self.canvas.draw()

    def on_method_change(self, event=None):
        # Hide all parameter inputs first
        self.step_size_frame.pack_forget()
        
        # Show relevant parameters based on method
        if self.method_var.get() == "Graphical":
            self.step_size_frame.pack()

    def insert_function(self, func):
        """Enhanced function button handler"""
        if func == 'x^n':
            self.equation_entry.insert('end', '^')
        elif func == 'x^2':
            self.equation_entry.insert('end', '^2')
        elif func == 'x^3':
            self.equation_entry.insert('end', '^3')
        elif func == '√x':
            self.equation_entry.insert('end', 'sqrt(')
        elif func == '|x|':
            self.equation_entry.insert('end', 'abs(')
        elif func == 'π':
            self.equation_entry.insert('end', 'π')
        else:
            self.equation_entry.insert('end', func)
    
    def numpad_click(self, value):
        """Enhanced numpad click handler"""
        if value == 'C':
            self.equation_entry.delete(0, 'end')
        elif value == '⌫':
            current = self.equation_entry.get()
            # Delete more characters for functions
            if current.endswith(('sin(', 'cos(', 'tan(', 'log(', 'ln(')):
                self.equation_entry.delete(len(current)-4, 'end')
            else:
                self.equation_entry.delete(len(current)-1, 'end')
        elif value == '=':
            self.plot()  # Trigger the plot action
        elif value == 'Plot':
            self.plot()  # Alternative plot trigger
        elif value == '√x':
            self.equation_entry.insert('end', 'sqrt(')
        elif value == '|x|':
            self.equation_entry.insert('end', 'abs(')
        else:
            self.equation_entry.insert('end', value)
            
    def validate_equation(self, equation):
        """Validate the equation format"""
        try:
            # Basic validation - check for balanced parentheses and absolute value symbols
            if equation.count('(') != equation.count(')'):
                return False, "Unbalanced parentheses"
            if equation.count('|') % 2 != 0:
                return False, "Unbalanced absolute value symbols"
            
            # Check for invalid characters
            valid_chars = set('0123456789.+-*/^()x sincotaelgqrπb|')  # Added '|' for absolute value
            if not all(c in valid_chars for c in equation.lower().replace(' ', '')):
                return False, "Invalid characters in equation"
                
            return True, ""
        except Exception as e:
            return False, str(e)
            
    def update_table(self, columns, rows):
        """Update the table display with enhanced styling"""
        # Clear previous table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        # Configure modern table styles
        header_style = {
            'font': ('Helvetica', 10, 'bold'),
            'background': TABLE_COLORS['header_bg'],
            'foreground': TABLE_COLORS['header_fg'],
            'padx': 8,
            'pady': 4,
            'relief': 'raised',
            'borderwidth': 1
        }
        
        cell_style = {
            'font': ('Helvetica', 10),
            'padx': 8,
            'pady': 3,
            'relief': 'groove',
            'borderwidth': 1
        }
        
        # Column configurations for different methods
        method_columns = {
            'Incremental': {
                'i': {'width': 5, 'align': 'center'},
                'xi': {'width': 12, 'align': 'right'},
                'f(xi)': {'width': 12, 'align': 'right'},
                'f(xi)*f(xi+1)': {'width': 12, 'align': 'right'}
            },
            'Bisection': {
                'Iteration': {'width': 5, 'align': 'center'},
                'xl': {'width': 10, 'align': 'right'},
                'xr': {'width': 10, 'align': 'right'},
                'xu': {'width': 10, 'align': 'right'},
                'f(xl)': {'width': 12, 'align': 'right'},
                'f(xr)': {'width': 12, 'align': 'right'},
                'f(xu)': {'width': 12, 'align': 'right'},
                '|ea|%': {'width': 12, 'align': 'right'},
                'f(xl)·f(xu)': {'width': 12, 'align': 'center'},
                'Remark': {'width': 25, 'align': 'left'}
            },
            'Regula Falsi': {
                'No. of iteration': {'width': 5, 'align': 'center'},
                'xl': {'width': 12, 'align': 'right'},
                'xu': {'width': 12, 'align': 'right'},
                'xr': {'width': 12, 'align': 'right'},
                'ea': {'width': 12, 'align': 'right'},
                'f(xl)': {'width': 12, 'align': 'right'},
                'f(xu)': {'width': 12, 'align': 'right'},
                'f(xr)': {'width': 12, 'align': 'right'},
                'f(xl)·f(xr)': {'width': 12, 'align': 'center'},
                'Next Step': {'width': 25, 'align': 'left'}
            },
            'Newton Raphson': {
                'No. of iteration': {'width': 5, 'align': 'center'},
                'xi': {'width': 12, 'align': 'right'},
                'ea': {'width': 12, 'align': 'right'},
                'f(xi)': {'width': 12, 'align': 'right'},
                "f'(xi)": {'width': 12, 'align': 'right'},
                'Status': {'width': 30, 'align': 'left'}
            },
            'Secant': {
                'Iteration Number': {'width': 5, 'align': 'center'},
                'xi-1': {'width': 12, 'align': 'right'},
                'xi': {'width': 12, 'align': 'right'},
                'xi+1': {'width': 12, 'align': 'right'},
                'ea': {'width': 12, 'align': 'right'},
                'f(xi-1)': {'width': 12, 'align': 'right'},
                'f(xi)': {'width': 12, 'align': 'right'},
                'f(xi+1)': {'width': 12, 'align': 'right'}
            }
        }
        
        # Column tooltips for different methods
        method_tooltips = {
            'Incremental': {
                'i': "Iteration number",
                'xi': "Current x value",
                'f(xi)': "Function value at current x",
                'f(xi)*f(xi+1)': "Product of consecutive function values"
            },
            'Bisection': {
                'Iteration': "Current iteration number",
                'xl': "Left endpoint of the interval",
                'xr': "Middle point (current approximation)",
                'xu': "Right endpoint of the interval",
                'f(xl)': "Function value at left endpoint",
                'f(xr)': "Function value at middle point",
                'f(xu)': "Function value at right endpoint",
                '|ea|%': "Absolute relative approximate error (%)",
                'f(xl)·f(xu)': "Sign of the product f(xl)×f(xu)",
                'Remark': "Which subinterval contains the root"
            },
            'Regula Falsi': {
                'No. of iteration': "Current iteration number",
                'xl': "Left endpoint of the interval",
                'xu': "Right endpoint of the interval",
                'xr': "Predicted root location",
                'ea': "Approximate relative error",
                'f(xl)': "Function value at left endpoint",
                'f(xu)': "Function value at right endpoint",
                'f(xr)': "Function value at predicted root",
                'f(xl)·f(xr)': "Sign check for convergence",
                'Next Step': "Next action in the algorithm"
            },
            'Newton Raphson': {
                'No. of iteration': "Current iteration number",
                'xi': "Current approximation",
                'ea': "Absolute relative error",
                'f(xi)': "Function value at current approximation",
                "f'(xi)": "Derivative value at current approximation",
                'Status': "Convergence status and warnings"
            },
            'Secant': {
                'Iteration Number': "Current iteration number",
                'xi-1': "Previous point",
                'xi': "Current point",
                'xi+1': "Next approximation",
                'ea': "Absolute relative error",
                'f(xi-1)': "Function value at previous point",
                'f(xi)': "Function value at current point",
                'f(xi+1)': "Function value at next approximation"
            }
        }
        
        tooltips = method_tooltips.get(self.method_var.get(), {})
        
        # Create table header
        header_frame = ttk.Frame(self.table_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Add headers with specific configurations
        for j, col in enumerate(columns):
            config = method_columns.get(self.method_var.get(), {}).get(col, {'width': 10, 'align': 'center'})
            anchor = {'left': 'w', 'right': 'e', 'center': 'center'}[config['align']]
            
            label = tk.Label(
                header_frame,
                text=col,
                width=config['width'],
                anchor=anchor,
                **header_style
            )
            label.grid(row=0, column=j, sticky='nsew', padx=1)
            
            # Add tooltip
            if col in tooltips:
                self.create_tooltip(label, tooltips[col])
        
        # Create content frame
        content_frame = ttk.Frame(self.table_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Add data rows
        for i, row in enumerate(rows):
            row_style = cell_style.copy()
            
            # Create cells
            for j, col in enumerate(columns):
                value = row.get(col, '') if isinstance(row, dict) else row[j]
                config = method_columns.get(self.method_var.get(), {}).get(col, {'width': 10, 'align': 'center'})
                anchor = {'left': 'w', 'right': 'e', 'center': 'center'}[config['align']]
                
                # Format cell content
                if isinstance(value, (int, float)):
                    if col in ['i', 'Iteration']:
                        cell_text = str(value)
                    elif col == '|ea|%':
                        cell_text = f"{value:.7f}" if value != 0 else "0"
                    else:
                        cell_text = f"{value:.7f}"
                else:
                    cell_text = str(value)
                
                # Create cell with proper alignment
                cell_frame = ttk.Frame(content_frame)
                cell_frame.grid(row=i, column=j, sticky='nsew', padx=1, pady=1)
                
                label = tk.Label(
                    cell_frame,
                    text=cell_text,
                    width=config['width'],
                    anchor=anchor,
                    **row_style
                )
                label.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        for i in range(len(columns)):
            content_frame.grid_columnconfigure(i, weight=1)
        
        # Update scroll region
        self.table_frame.update_idletasks()
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

    def create_tooltip(self, widget, text, is_warning=False, is_success=False):
        """Create a modern tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Style the tooltip based on type
            bg_color = TABLE_COLORS['tooltip_bg']
            fg_color = TABLE_COLORS['tooltip_fg']
            if is_warning:
                bg_color = TABLE_COLORS['warning']
                fg_color = TABLE_COLORS['normal_bg']
            elif is_success:
                bg_color = TABLE_COLORS['success']
                fg_color = TABLE_COLORS['normal_bg']
            
            # Create tooltip with modern styling
            label = tk.Label(
                tooltip,
                text=text,
                justify=tk.LEFT,
                background=bg_color,
                foreground=fg_color,
                relief="solid",
                borderwidth=1,
                font=("Helvetica", 9),
                padx=8,
                pady=4
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)

    def toggle_y_limits(self):
        """Enable/disable Y-axis limit inputs based on auto-scale checkbox"""
        state = 'disabled' if self.auto_scale_var.get() else 'normal'
        for widget in self.y_limits_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.configure(state=state)

    def get_plot_limits(self):
        """Get plot limits with validation"""
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            y_min = float(self.y_min_var.get())
            y_max = float(self.y_max_var.get())
            
            if x_max <= x_min:
                raise ValueError("X-max must be greater than X-min")
            if not self.auto_scale_var.get() and y_max <= y_min:
                raise ValueError("Y-max must be greater than Y-min")
                
            return x_min, x_max, y_min, y_max
        except ValueError as e:
            if "must be greater than" in str(e):
                raise e
            raise ValueError("Invalid limit values. Please enter numbers only.")

    def find_appropriate_range(self, f, df=None, method=""):
        """Find appropriate x-range that includes all roots"""
        # Check if user has set custom range
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            if x_max > x_min:
                return x_min, x_max
        except ValueError:
            pass  # If custom range is invalid, proceed with automatic range finding
        
        # Start with a wide range to find potential roots
        wide_x_min, wide_x_max = -50, 50
        roots = []
        
        try:
            # Check for periodic behavior
            test_points = np.linspace(wide_x_min, wide_x_max, 1000)
            y_vals = f(test_points)
            
            # Look for repeating patterns in zero crossings
            zero_crossings = np.where(np.diff(np.signbit(y_vals)))[0]
            if len(zero_crossings) > 4:  # Need at least 5 roots to check periodicity
                intervals = np.diff(zero_crossings)
                avg_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                
                # If standard deviation is small compared to average, likely periodic
                is_periodic = std_interval < avg_interval * 0.1
                
                if is_periodic:
                    # For periodic functions, show 2-3 periods
                    period = avg_interval * (test_points[1] - test_points[0])
                    x_min = -period * 1.5
                    x_max = period * 1.5
                    
                    # Find roots in this range
                    if method == "Graphical":
                        step_size = float(self.step_size_var.get())
                        roots, _ = graphical_method(f, x_min=x_min, x_max=x_max, step=step_size)
                        # Only show periodic warning for Graphical method
                        self.show_periodic_warning()
                    elif method == "Incremental":
                        roots, _ = incremental_search(f, x_min, x_max, step=0.1)
                    else:
                        # For other methods, find roots near zero crossings in range
                        for x in test_points[zero_crossings]:
                            if x_min <= x <= x_max:
                                roots.append(x)
                    
                    return x_min, x_max
            
            # If not periodic, proceed with normal root finding
            if method == "Graphical":
                step_size = float(self.step_size_var.get())
                roots, _ = graphical_method(f, x_min=wide_x_min, x_max=wide_x_max, step=step_size)
            elif method == "Incremental":
                roots, _ = incremental_search(f, wide_x_min, wide_x_max, step=0.1)
            elif method == "Bisection":
                roots, _ = bisection_method(f, wide_x_min, wide_x_max)
            elif method == "Regula Falsi":
                roots, _ = regula_falsi(f, wide_x_min, wide_x_max)
            elif method == "Newton Raphson":
                if df is None:
                    raise ValueError("Newton-Raphson requires differentiable function")
                for x0 in np.linspace(wide_x_min, wide_x_max, 20):
                    try:
                        new_roots, _ = newton_raphson(f, df, x0)
                        roots.extend(new_roots)
                    except:
                        continue
            elif method == "Secant":
                for x0 in np.linspace(wide_x_min, wide_x_max, 10):
                    try:
                        new_roots, _ = secant_method(f, x0, x0 + 0.1)
                        roots.extend(new_roots)
                    except:
                        continue
            
            # Remove duplicates and sort roots
            roots = sorted(list(set([round(r, 6) for r in roots])))
            
            if not roots:
                return -10, 10
            
            # Add padding around the roots
            x_range = max(roots) - min(roots)
            padding = max(x_range * 0.2, 2)
            x_min = min(roots) - padding
            x_max = max(roots) + padding
            
            # Ensure minimum window size
            if x_max - x_min < 4:
                center = (x_max + x_min) / 2
                x_min = center - 2
                x_max = center + 2
            
            return x_min, x_max
            
        except Exception:
            return -10, 10

    def show_periodic_warning(self):
        """Show warning about periodic function"""
        messagebox.showinfo("Periodic Function Detected",
            "This function appears to have infinite roots that repeat periodically.\n\n"
            "The graph window has been adjusted to show 2-3 periods of the function.\n\n"
            "Note: There are infinitely many more roots beyond what is shown.")

    def on_click(self, event):
        """Handle mouse clicks on the plot"""
        if event.inaxes != self.ax:
            return
            
        if event.button == 3:  # Right click
            # Find nearest root
            if hasattr(self, 'current_roots'):
                x_click = event.xdata
                nearest_root = min(self.current_roots, 
                                 key=lambda r: abs(r - x_click))
                self.status_bar.config(
                    text=f"Nearest root: {nearest_root:.6f}")
    
    def on_motion(self, event):
        """Update coordinates in status bar"""
        if event.inaxes != self.ax:
            self.status_bar.config(text="")
            return
            
        x, y = event.xdata, event.ydata
        self.status_bar.config(
            text=f"x: {x:.6f}, y: {y:.6f}")
    
    def on_scroll(self, event):
        """Handle mouse scroll for zooming"""
        if event.inaxes != self.ax:
            return
            
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        
        if event.button == 'up':
            scale_factor = 0.9  # zoom in
        else:
            scale_factor = 1.1  # zoom out
            
        # Calculate new limits
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_xlim[0]) * scale_factor
        
        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_xlim[0])
        
        self.ax.set_xlim([xdata - new_width * (1-relx),
                         xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1-rely),
                         ydata + new_height * rely])
        
        if self.toolbar.auto_update_var.get():
            self.update_plot_for_zoom()
        else:
            self.canvas.draw_idle()
    
    def on_zoom_select(self, xmin, xmax):
        """Handle zoom selection"""
        if xmin == xmax:
            return
        self.ax.set_xlim(xmin, xmax)
        
        if self.toolbar.auto_update_var.get():
            self.update_plot_for_zoom()
        else:
            self.canvas.draw_idle()
    
    def update_plot_for_zoom(self):
        """Update plot data for current zoom level"""
        xlim = self.ax.get_xlim()
        if hasattr(self, 'current_f'):
            # Generate more points in visible range
            x_vals = np.linspace(xlim[0], xlim[1], 1000)
            y_vals = self.current_f(x_vals)
            
            # Clear and redraw
            self.ax.lines[0].set_data(x_vals, y_vals)
            self.canvas.draw_idle()
    
    def plot(self):
        # Add validation before processing
        equation = self.equation_entry.get()
        is_valid, error_msg = self.validate_equation(equation)
        if not is_valid:
            messagebox.showerror("Error", f"Invalid equation: {error_msg}")
            return
            
        method = self.method_var.get()
        f, df, expr, x_sym = self.parse_equation()
        if f is None:
            return

        try:
            # Check if user has set custom x-axis limits
            try:
                custom_x_min = float(self.x_min_var.get())
                custom_x_max = float(self.x_max_var.get())
                if custom_x_max <= custom_x_min:
                    raise ValueError("X-max must be greater than X-min")
                use_custom_range = True
            except ValueError:
                use_custom_range = False
            
            # Initialize variables for periodic detection
            is_periodic = False
            period = None
            
            # Get range based on user preference
            if use_custom_range:
                x_min, x_max = custom_x_min, custom_x_max
            else:
                x_min, x_max = self.find_appropriate_range(f, df, method)
            
            self.x_min_var.set(f"{x_min:.2f}")
            self.x_max_var.set(f"{x_max:.2f}")
            
            self.clear_plot()
            roots = []
            table_data = []
            x_vals = np.linspace(x_min, x_max, 400)
            y_vals = f(x_vals)

            try:
                # Get method parameters
                try:
                    step_size = float(self.step_size_var.get())
                    if step_size <= 0:
                        raise ValueError("Step size must be positive")
                except ValueError:
                    messagebox.showerror("Error", "Invalid step size. Please enter a positive number.")
                    return
                    
                try:
                    tolerance = float(self.tolerance_var.get())
                    if tolerance <= 0:
                        raise ValueError("Tolerance must be positive")
                except ValueError:
                    messagebox.showerror("Error", "Invalid tolerance. Please enter a positive number.")
                    return
                
                if method == "Graphical":
                    roots, table_data, is_periodic, period = graphical_method(f, x_min=x_min, x_max=x_max, step=step_size)
                elif method == "Incremental":
                    roots, table_data = incremental_search(f, x_min, x_max, step=step_size)
                elif method == "Bisection":
                    roots, table_data = bisection_method(f, x_min, x_max, tol=tolerance)
                elif method == "Regula Falsi":
                    roots, table_data = regula_falsi(f, x_min, x_max, tol=tolerance)
                elif method == "Newton Raphson":
                    roots, table_data = newton_raphson(f, df, x0=(x_min + x_max)/2, tol=tolerance)
                elif method == "Secant":
                    # Use step size to determine second initial point
                    x0 = x_min
                    x1 = x0 + step_size
                    roots, table_data = secant_method(f, x0, x1, tol=tolerance)
                
                # Update table with scrolling
                if table_data:
                    columns = list(table_data[0].keys())
                    rows = [list(row.values()) for row in table_data]
                    self.update_table(columns, rows)
                    
                # Auto-scale Y-axis if selected
                if self.auto_scale_var.get():
                    y_margin = (np.max(y_vals) - np.min(y_vals)) * 0.1
                    y_min = np.min(y_vals) - y_margin
                    y_max = np.max(y_vals) + y_margin
                    self.y_min_var.set(f"{y_min:.2f}")
                    self.y_max_var.set(f"{y_max:.2f}")
                else:
                    _, _, y_min, y_max = self.get_plot_limits()
                
                # Plot function and roots
                self.ax.plot(x_vals, y_vals, color='#00ff99', label='f(x)')
                self.ax.axhline(0, color=TEXT_COLOR, linewidth=0.5)
                self.ax.axvline(0, color=TEXT_COLOR, linewidth=0.5)
                self.ax.grid(color='#333366', linestyle='--')
                
                # Set axis limits
                self.ax.set_xlim(x_min, x_max)
                self.ax.set_ylim(y_min, y_max)
                
                # Format roots for display
                formatted_roots = [f"{root:.6f}" for root in roots]
                
                # Plot roots and update title
                for root in roots:
                    if x_min <= root <= x_max:
                        self.ax.plot(root, 0, 'ro', markersize=8)
                        self.ax.annotate(f'{root:.4f}', (root, 0), 
                                       xytext=(0, 15), textcoords='offset points',
                                       ha='center', va='bottom', fontsize=9, color='red',
                                       arrowprops=dict(arrowstyle="->", color='red', lw=1))
                
                # Update title based on periodicity
                if is_periodic and method == "Graphical":
                    title = f"{method} Method - Periodic Function (Period ≈ {period:.4f})"
                    if not hasattr(self, '_periodic_warning_shown'):
                        self.show_periodic_warning(period)
                        self._periodic_warning_shown = True
                else:
                    title = f"{method} Method - Found Roots: {', '.join(formatted_roots)}"
                
                self.ax.set_title(title, color=TEXT_COLOR)
                self.ax.legend(facecolor=PLOT_BG, edgecolor=TEXT_COLOR)
                self.canvas.draw()
                
                # Store function and roots for interactive features
                self.current_f = f
                self.current_roots = roots
                
                # Store original view limits if not already stored
                if self.original_xlim is None:
                    self.original_xlim = self.ax.get_xlim()
                    self.original_ylim = self.ax.get_ylim()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_periodic_warning(self, period):
        """Show warning about periodic function with period information"""
        messagebox.showinfo("Periodic Function Detected",
            f"This function appears to have infinite roots that repeat every {period:.4f} units.\n\n"
            f"The graph window has been adjusted to show 3 periods of the function.\n\n"
            "Note: There are infinitely many more roots beyond what is shown.\n"
            "The roots shown are representative of the pattern that continues infinitely.")

    def show_instructions(self):
        instructions = """INSTRUCTIONS:

1. Enter Equation:
   - Use 'x' as variable
   - Examples:
     • Polynomial: x^3 - 2x + 1
     • Trigonometric: sin(x) + cos(2x)
     • Exponential: e^x - 10
     • Logarithmic: ln(x) - 1

2. Select Method and Click Plot:
   - Graphical: Visual approximation
   - Bracketing: Needs sign change
   - Open: Needs initial guess

3. Results:
   - Roots marked in red
   - Table shows iterations"""
        messagebox.showinfo("User Guide", instructions)

    def show_samples(self):
        """Show sample equations menu"""
        samples_menu = tk.Menu(self.master, tearoff=0)
        
        # Polynomial Equations
        polynomials = {
            "Simple Quadratic": "x^2 - 4",
            "Cubic with Multiple Roots": "x^3 - x",
            "Higher Degree": "x^4 - 5x^2 + 4",
            "Complex Polynomial": "x^3 - 7x^2 + 14x - 8"
        }
        
        # Trigonometric Equations
        trigonometric = {
            "Basic Sine": "sin(x)",
            "Shifted Cosine": "cos(x) - 0.5",
            "Combined Trig": "sin(x) + cos(x)",
            "Modified Sine": "2*sin(x/2)",
            "Periodic Complex": "sin(x)*cos(x)"
        }
        
        # Exponential and Logarithmic
        exp_log = {
            "Simple Exponential": "e^x - 4",
            "Natural Log": "ln(x) - 1",
            "Combined Exp-Log": "e^x - ln(x) - 2",
            "Log Base 10": "log(x) - 1"
        }
        
        # Special Functions
        special = {
            "Absolute Value": "|x| - 2",
            "Square Root": "sqrt(x) - 2",
            "Rational Function": "1/(x-2) + 3",
            "Piecewise-like": "|x^2 - 4|"
        }
        
        # Challenging Examples
        challenging = {
            "Multiple Close Roots": "x^3 - 0.001x^2 - 0.1x + 0.001",
            "Periodic with Offset": "sin(π*x) + 0.1x",
            "Combined Functions": "sin(x^2) + ln(abs(x) + 1) - 1",
            "Oscillating": "sin(1/x) - 0.5"
        }
        
        # Create submenus
        categories = {
            "Polynomials": polynomials,
            "Trigonometric": trigonometric,
            "Exponential & Log": exp_log,
            "Special Functions": special,
            "Challenging": challenging
        }
        
        for category, equations in categories.items():
            submenu = tk.Menu(samples_menu, tearoff=0)
            samples_menu.add_cascade(label=category, menu=submenu)
            
            for name, eq in equations.items():
                submenu.add_command(
                    label=f"{name}: {eq}",
                    command=lambda e=eq: self.load_sample(e)
                )
        
        # Display the menu below the Sample Equations button
        x = self.samples_button.winfo_rootx()
        y = self.samples_button.winfo_rooty() + self.samples_button.winfo_height()
        samples_menu.post(x, y)
    
    def load_sample(self, equation):
        """Load a sample equation into the entry field"""
        self.equation_entry.delete(0, 'end')
        self.equation_entry.insert(0, equation)
        
        # Auto-adjust ranges for certain types of equations
        if 'sin' in equation or 'cos' in equation:
            if 'π' in equation:
                self.x_min_var.set("-2")  # For equations with π, use smaller range
                self.x_max_var.set("2")
            else:
                self.x_min_var.set("-6")
                self.x_max_var.set("6")
        elif 'ln' in equation or 'log' in equation:
            self.x_min_var.set("0.1")
            self.x_max_var.set("10")
        elif '1/x' in equation:
            self.x_min_var.set("-10")
            self.x_max_var.set("10")
        else:
            self.x_min_var.set("-5")
            self.x_max_var.set("5")

if __name__ == "__main__":
    root = tk.Tk()
    app = RootFinderApp(root)
    root.mainloop()