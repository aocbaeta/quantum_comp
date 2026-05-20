from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pennylane as qml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "tables" / "quantum_languages"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def main() -> None:
    # Toy data: classify points by sign of x0 * x1, an XOR-like nonlinear rule.
    x_train = np.array(
        [
            [-1.0, -1.0],
            [-1.0, 1.0],
            [1.0, -1.0],
            [1.0, 1.0],
            [-0.6, -0.8],
            [-0.6, 0.8],
            [0.6, -0.8],
            [0.6, 0.8],
        ]
    )
    y_train = np.array([1, 0, 0, 1, 1, 0, 0, 1], dtype=float)

    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuit(x, weights):
        qml.AngleEmbedding(x, wires=[0, 1], rotation="Y")
        for layer in range(weights.shape[0]):
            qml.RY(weights[layer, 0], wires=0)
            qml.RY(weights[layer, 1], wires=1)
            qml.CNOT(wires=[0, 1])
            qml.RZ(weights[layer, 2], wires=0)
            qml.RZ(weights[layer, 3], wires=1)
            qml.CNOT(wires=[1, 0])
        return qml.expval(qml.PauliZ(0))

    rng = np.random.default_rng(7)
    weights = rng.normal(scale=0.1, size=(3, 4))
    bias = 0.0
    lr = 0.35

    # Parameter-shift by finite difference is enough here: tiny demonstrator,
    # intentionally framework-light and easy to inspect.
    eps = 1e-4
    losses = []
    for _step in range(80):
        logits = np.array([circuit(x, weights) + bias for x in x_train])
        preds = sigmoid(3.0 * logits)
        loss = -np.mean(y_train * np.log(preds + 1e-9) + (1 - y_train) * np.log(1 - preds + 1e-9))
        losses.append(float(loss))

        grad_w = np.zeros_like(weights)
        for index in np.ndindex(weights.shape):
            plus = weights.copy()
            minus = weights.copy()
            plus[index] += eps
            minus[index] -= eps
            logits_plus = np.array([circuit(x, plus) + bias for x in x_train])
            logits_minus = np.array([circuit(x, minus) + bias for x in x_train])
            loss_plus = -np.mean(
                y_train * np.log(sigmoid(3.0 * logits_plus) + 1e-9)
                + (1 - y_train) * np.log(1 - sigmoid(3.0 * logits_plus) + 1e-9)
            )
            loss_minus = -np.mean(
                y_train * np.log(sigmoid(3.0 * logits_minus) + 1e-9)
                + (1 - y_train) * np.log(1 - sigmoid(3.0 * logits_minus) + 1e-9)
            )
            grad_w[index] = (loss_plus - loss_minus) / (2 * eps)

        grad_b = float(np.mean(3.0 * (preds - y_train)))
        weights -= lr * grad_w
        bias -= lr * grad_b

    final_logits = np.array([circuit(x, weights) + bias for x in x_train])
    final_probs = sigmoid(3.0 * final_logits)
    final_labels = (final_probs >= 0.5).astype(int)
    accuracy = float(np.mean(final_labels == y_train))

    payload = {
        "task": "toy XOR-like variational quantum classifier",
        "accuracy": accuracy,
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "probabilities": final_probs.tolist(),
        "labels": final_labels.tolist(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "qml_variational_classifier.json").open("w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
