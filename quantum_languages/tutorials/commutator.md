# Comutador

Este tutorial mostra como calcular o commutador
`[A, B] = A B - B A` para operadores quânticos usando Python e frameworks
modernos: Qiskit, Cirq e PennyLane.

## Definição

O commutador de dois operadores `A` e `B` é:

```text
[A, B] = A B - B A
```

Para as matrizes de Pauli, temos:

```text
[X, Y] = 2 i Z
[Y, Z] = 2 i X
[Z, X] = 2 i Y
```

## Python direto

A implementação central está em `src/algebra.py`.
Use o `PYTHONPATH=src` para importar o módulo do diretório raiz.

```bash
cd ~/quantum_ic
source .venv/bin/activate
PYTHONPATH=src python - <<'PY'
import numpy as np
from algebra import X, Y, Z, commutator

print("[X, Y]:")
print(commutator(X, Y))
print("Expected:")
print(2j * Z)
print("Check:", np.allclose(commutator(X, Y), 2j * Z))
PY
```

## Qiskit

No Qiskit, o commutador pode ser calculado a partir das matrizes de operadores Pauli.

```bash
cd ~/quantum_ic
source .venv/bin/activate
python - <<'PY'
import numpy as np
from qiskit.quantum_info import Operator

X = Operator.from_label("X").data
Y = Operator.from_label("Y").data
Z = Operator.from_label("Z").data
comm = X @ Y - Y @ X
print("[X, Y] =")
print(comm)
print("Expected:")
print(2j * Z)
print("Check:", np.allclose(comm, 2j * Z))
PY
```

## Cirq

Em Cirq, use as matrizes unitárias de Pauli e calcule o commutador diretamente.

```bash
cd ~/quantum_ic
source .venv/bin/activate
python - <<'PY'
import numpy as np
import cirq

X = cirq.unitary(cirq.X)
Y = cirq.unitary(cirq.Y)
Z = cirq.unitary(cirq.Z)
comm = X @ Y - Y @ X
print("[X, Y] =")
print(comm)
print("Expected:")
print(2j * Z)
print("Check:", np.allclose(comm, 2j * Z))
PY
```

## PennyLane

Em PennyLane, basta usar arrays NumPy para os operadores de Pauli.

```bash
cd ~/quantum_ic
source .venv/bin/activate
python - <<'PY'
import numpy as np

X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
comm = X @ Y - Y @ X
print("[X, Y] =")
print(comm)
print("Expected:")
print(2j * Z)
print("Check:", np.allclose(comm, 2j * Z))
PY
```

## Código exato do commutador

O algoritmo abaixo é o commutador Python completo, equivalente ao que você forneceu:

```python
GENERIC_SPIN = "s"
sg = GENERIC_SPIN

def delta(a, b):
    return [[a[1], b[1]], [a[2], b[2]]]


def _allowed_contraction(lhs, rhs):
    lhs_kind, _, lhs_spin = lhs
    rhs_kind, _, rhs_spin = rhs

    if lhs_kind == rhs_kind:
        return False

    if rhs_spin != GENERIC_SPIN and lhs_spin != rhs_spin:
        return False

    return True


def _sign_from_expansion_order(interaction_index):
    return 1 if interaction_index % 2 == 0 else -1


def comm(v1, v2):
    sig = []
    flt = []
    dta = []
    interaction_index = 0

    for i, lhs in enumerate(v1):
        _, lhs_site, _ = lhs
        left_prefix = v1[:i]
        left_suffix = v1[i + 1 :]

        for j, rhs in enumerate(v2):
            sign = _sign_from_expansion_order(interaction_index)
            interaction_index += 1

            if not _allowed_contraction(lhs, rhs):
                continue

            flatt = left_prefix + v2[:j] + v2[j + 1 :] + left_suffix
            sig.append([sign])
            flt.append(flatt)
            dta.append([] if lhs_site == rhs[1] else delta(lhs, rhs))

    return [sig, flt, dta]
```

## Rodar o commutador exato no repositório

O script abaixo implementa e executa exatamente esse commutador:

```bash
cd ~/quantum_ic
source .venv/bin/activate
python quantum_languages/scripts/commutator_symbolic.py
```

Ele executa auto-testes e imprime o resultado formatado das três amostras de exemplo.

## Usar em Qiskit / Cirq / PennyLane

Esse código é puramente simbólico/algébrico e funciona em qualquer ambiente Python.
Em Qiskit/Cirq/PennyLane, você pode rodar o mesmo script quando estiver no ambiente da linguagem quântica,
pois o resultado não depende de circuitos:

```bash
cd ~/quantum_ic
source .venv/bin/activate
python quantum_languages/scripts/commutator_symbolic.py
```

Para linguagens de circuito como OpenQASM ou QCL, o equivalente exato não é direto na sintaxe de gates,
porque o código implementa uma expansão de contração simbólica e não a aplicação de portas unitárias.

OpenQASM e QCL são linguagens de circuito em vez de álgebra matricial.
Elas não possuem uma forma nativa de escrever `AB - BA` diretamente,
mas você pode comparar a ação sequencial de `XY` e `YX` em um estado.

Para cálculos algébricos de commutador, use um framework Python como Qiskit,
Cirq ou PennyLane.
