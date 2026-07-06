import os
import numpy as np
import pandas as pd
from scipy.stats import chi2, fisher_exact
import matplotlib.pyplot as plt

# --- output folder ---
output_folder = r"G:\Edu\FJFI ČVUT\bakalarka\first_research\fishers"
os.makedirs(output_folder, exist_ok=True)  # vytvoří složku, pokud neexistuje

# --- data ---
observed5 = np.array([[5, 2], [2, 4]])        # <5
observed510 = np.array([[10, 4], [4, 8]])     # 5-10
observed10 = np.array([[1000, 1500], [1800, 2400]])   # >10

observed52 = np.array([[2, 5], [3, 4]])        # <5
observed5102 = np.array([[6, 9], [8, 5]])     # 5-10
observed102 = np.array([[21, 37], [36, 15]])   # >10

observed53 = np.array([[3984, 4356], [4698, 4123]])        # <5
observed5103 = np.array([[6, 8], [8, 7]])     # 5-10  data velmi blizko u sebe
observed103 = np.array([[18, 29], [23, 19]])   # >10

observed54 = np.array([[3, 5], [4, 4]])        # <5
observed5104 = np.array([[6, 8], [8, 7]])     # 5-10  data velmi blizko u sebe
observed104 = np.array([[20, 380], [6, 594]])   # >10

datasets = {
    "<5": observed54,
    "5-10": observed5104,
    ">10": observed104
}

# --- test functions ---
def chi_squared_test(observed):
    row_sum = observed.sum(axis=1).reshape(-1,1)
    col_sum = observed.sum(axis=0).reshape(1,-1)
    total_sum = observed.sum()
    expected = row_sum @ col_sum / total_sum
    chi2_stat = ((observed - expected) ** 2 / expected).sum()
    dof = (observed.shape[0]-1)*(observed.shape[1]-1)
    p_value = 1 - chi2.cdf(chi2_stat, dof)
    return chi2_stat, p_value

def fisher_test(observed):
    if observed.shape == (2,2):
        _, p_value = fisher_exact(observed)
        return p_value
    else:
        return None

def odds_ratio(observed):
    if observed.shape != (2, 2):
        return None

    a, b = observed[0, 0], observed[0, 1]
    c, d = observed[1, 0], observed[1, 1]

    # ochrana proti dělení nulou
    if b == 0 or c == 0:
        return np.inf

    return (a * d) / (b * c)

def odds_ratio_ci(observed, alpha=0.05):
    if observed.shape != (2, 2):
        return None

    a, b = observed[0, 0], observed[0, 1]
    c, d = observed[1, 0], observed[1, 1]

    # Haldane–Anscombe korekce (kvůli nulám)
    if 0 in (a, b, c, d):
        a += 0.5
        b += 0.5
        c += 0.5
        d += 0.5

    # odds ratio
    or_value = (a * d) / (b * c)

    # standard error log(OR)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)

    z = 1.96  # pro 95% CI
    log_or = np.log(or_value)

    lower = np.exp(log_or - z * se)
    upper = np.exp(log_or + z * se)

    return or_value, lower, upper

# --- výpočty a ukládání ---
results = []
for label, table in datasets.items():
    chi2_stat, p_chi = chi_squared_test(table)
    p_fisher = fisher_test(table)
    results.append({
        "Counts": label,
        "Chi2_stat": chi2_stat,
        "Chi2_pvalue": p_chi,
        "Fisher_pvalue": p_fisher
    })

for name, data in datasets.items():
    or_value = odds_ratio(data)
    print(f"{name}: odds ratio = {or_value:.3f}")
    
for name, data in datasets.items():
    or_val, ci_low, ci_high = odds_ratio_ci(data)
    print(f"{name}: OR = {or_val:.3f}, 95% CI = ({ci_low:.3f}, {ci_high:.3f})")

# uložit do Excelu
df_results = pd.DataFrame(results)
excel_path = os.path.join(output_folder, "test_comparison_results.xlsx")
df_results.to_excel(excel_path, index=False)
print(f"Results saved to {excel_path}")
print(df_results)

# --- graf ---
plt.figure(figsize=(6,4))
plt.plot(df_results["Counts"], df_results["Chi2_pvalue"], marker='o', label='Chi-squared')
plt.plot(df_results["Counts"], df_results["Fisher_pvalue"], marker='s', label='Fisher exact')
plt.ylabel('p-value')
plt.xlabel('Expected counts category')
plt.title('Comparison of Chi-squared vs Fisher p-values')
plt.ylim(0,1)
plt.legend()
plt.grid(True)
plt.tight_layout()

plot_path = os.path.join(output_folder, "test_comparison_plot.png")
plt.savefig(plot_path)
plt.show()
print(f"Plot saved to {plot_path}")
