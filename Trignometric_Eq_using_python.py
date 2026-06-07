from IPython.display import display, Math
import sympy as sp

x= sp.Symbol('x')

equation=sp.Eq(sp.sin(x)**2 + sp.cos(x)**2, 1)
latex_equation=sp.latex(equation)
display(Math(latex_equation))