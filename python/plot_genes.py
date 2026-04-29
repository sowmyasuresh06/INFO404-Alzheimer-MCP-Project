import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv(r"C:\temp\a1bg_boxplot.csv")

# Separate groups
ad = df[df["diagnosis"] == "AD"]["expression_value"]
control = df[df["diagnosis"] == "Control"]["expression_value"]

# Plot
plt.figure(figsize=(6,6))
plt.boxplot([ad, control], labels=["AD", "Control"])

plt.title("A1BG Expression: AD vs Control")
plt.ylabel("Expression Value")

plt.tight_layout()
plt.show()
