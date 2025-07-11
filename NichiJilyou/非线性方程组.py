from scipy.optimize import fsolve
import numpy as np
def equations(vars):
    x, y, z = vars
    eq1 = 2*x + 3*y**2 + z**2 - 8
    eq2 = 2*x**2 + 3*y + 5*z
    eq3 = x - 2*y - 5*z**2 - 3
    return [eq1, eq2, eq3]
initial_guess = [1, 1, 1]
solution = fsolve(equations, initial_guess)
result = np.round(solution, 2)
print(f"方程组的解为：x = {result[0]}, y = {result[1]}, z = {result[2]}")