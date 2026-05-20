QUANTUM_COLORS = {
    "hilbert_black": "#101214",
    "graphite": "#1B1F23",
    "chalk": "#F2EFE6",
    "silver_eigen": "#B7C0C7",
    "qubit_cyan": "#00A7C8",
    "pauli_blue": "#3454D1",
    "cooper_gold": "#F2B84B",
    "fermion_green": "#4CAF7D",
    "phase_red": "#D94F45",
    "bra_purple": "#7B61FF",
}

PLOT_CYCLE = [
    QUANTUM_COLORS["qubit_cyan"],
    QUANTUM_COLORS["cooper_gold"],
    QUANTUM_COLORS["fermion_green"],
    QUANTUM_COLORS["pauli_blue"],
    QUANTUM_COLORS["phase_red"],
    QUANTUM_COLORS["bra_purple"],
]


def apply_quantum_style():
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": QUANTUM_COLORS["hilbert_black"],
            "axes.facecolor": QUANTUM_COLORS["graphite"],
            "axes.edgecolor": QUANTUM_COLORS["silver_eigen"],
            "axes.labelcolor": QUANTUM_COLORS["chalk"],
            "xtick.color": QUANTUM_COLORS["silver_eigen"],
            "ytick.color": QUANTUM_COLORS["silver_eigen"],
            "text.color": QUANTUM_COLORS["chalk"],
            "grid.color": "#3A4047",
            "axes.prop_cycle": plt.cycler(color=PLOT_CYCLE),
        }
    )
