OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

// Search target |11> in a 2-qubit space.
h q[0];
h q[1];

// Oracle: phase flip |11>.
cz q[0], q[1];

// Diffusion.
h q[0];
h q[1];
x q[0];
x q[1];
cz q[0], q[1];
x q[0];
x q[1];
h q[0];
h q[1];

c[0] = measure q[0];
c[1] = measure q[1];
