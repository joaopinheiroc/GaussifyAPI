import base64
import io
import matplotlib


matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

def calculate_probability(mean: float, std_dev: float, target_x: float) -> float:

    if std_dev <= 0:
        raise ValueError("Standard deviation must be greater than zero.")

    probability = norm.cdf(target_x, loc=mean, scale=std_dev)
    return float(probability)

def generate_chart_base64(mean:float, std_dev: float, target_x: float) -> str:
    x = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 500)
    y = norm.pdf(x, loc=mean, scale=std_dev)

    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(x, y, color="#4f46e5", linewidth=2)
 
    x_area = np.linspace(mean - 4 * std_dev, target_x, 300)
    y_area = norm.pdf(x_area, loc=mean, scale=std_dev)
    ax.fill_between(x_area, y_area, color="#4f46e5", alpha=0.3)
 
    ax.axvline(target_x, color="#dc2626", linestyle="--", label=f"x = {target_x}")
    ax.set_title("Normal Distribution")
    ax.set_xlabel("Value")
    ax.set_ylabel("Probability Density")
    ax.legend()
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)

    base64_image = base64.b64encode(buffer.read()).decode("utf-8")
    return base64_image

def process_calculation(mean: float, std_dev: float, target_x: float) -> dict:

    probability = calculate_probability(mean, std_dev, target_x)
    chart_base64 = generate_chart_base64(mean, std_dev, target_x)

    return {
        "probability": probability,
        "chart_base64": chart_base64
    }