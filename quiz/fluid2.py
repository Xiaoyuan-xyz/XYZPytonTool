import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# =========================
# ODE system
# y0 = f
# y1 = f'
# y2 = f''
# =========================
def ode(x, y):
    f, fp, fpp = y
    fppp = -0.5 * f * fpp
    return [fp, fpp, fppp]

# =========================
# Shooting: given s = f''(0),
# return f'(x_max) - 1
# =========================
def shoot(s, x_max=10.0):
    sol = solve_ivp(
        ode,
        (0, x_max),
        [0.0, 0.0, s],
        max_step=0.05
    )
    return sol.y[1, -1] - 1.0, sol

# =========================
# Bisection to find f''(0)
# =========================
s_left, s_right = 0.1, 2.0
for _ in range(40):
    s_mid = 0.5 * (s_left + s_right)
    val, _ = shoot(s_mid)
    if val > 0:
        s_right = s_mid
    else:
        s_left = s_mid

_, sol = shoot(s_mid)

# =========================
# Extract solution
# =========================
x = sol.t
f = sol.y[0]

# =========================
# Plot
# =========================
plt.figure(figsize=(7, 5))

# f(x)
plt.plot(x, f, linewidth=2, label=r"$f(x)$")

# y = C*sqrt(x)
x2 = np.linspace(0, x.max(), 400)
for C in [0.5, 1.0, 1.5, 2.0]:
    plt.plot(
        x2,
        C * np.sqrt(x2),
        linestyle="--",
        color="gray",
        label=rf"$y=C\sqrt{{x}},\ C={C}$"
    )

#plt.xlabel("x")
#plt.ylabel("y")
plt.xlim(left=-1)
plt.ylim(bottom=-1)
plt.grid(True)
# plt.legend()
plt.tight_layout()
plt.show()
