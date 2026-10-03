# Quantum basics (beginner level)

You only need these 12 ideas for this project. Each in one paragraph.

## 1. Qubit
A bit is a coin lying flat: heads (0) or tails (1). A qubit is a coin
*spinning* on the table: while spinning it is neither heads nor tails, a
blend of both. That blend is **superposition**.

## 2. H gate
Takes a flat coin and sets it spinning: |0> becomes (|0> + |1>)/sqrt(2).

## 3. CNOT gate
A quantum *if* statement: flips the target qubit only if the control is 1.
This is the gate that links two qubits together.

## 4. Bell state
Two qubits in a linked superposition: each qubit alone measures completely
random, but the two always agree. Recipe: H on qubit 0, then CNOT(0 -> 1).
|Phi+> = (|00> + |11>)/sqrt(2). The entire quantum core of this project.

## 5. Measurement / shots
Slapping the spinning coin down: it becomes 0 or 1 with some probability.
One slap = one **shot**. We repeat thousands of shots and count outcomes.

## 6. SWAP gate
Exchanges the states of two qubits. Costs 3 CNOTs. Used to move quantum
information along the chip.

## 7. Coupling map
The road map: which qubit pairs may do a two-qubit gate directly.
No road = no direct CNOT = detour via SWAPs.

## 8. Virtual vs physical qubits
Your circuit talks about *logical* qubits (0, 1). The chip has *physical*
qubits (0..34). The transpiler chooses which physical qubit hosts each
logical one (layout) and may move them during the circuit (routing).

## 9. Transpilation
Rewriting the logical circuit so it obeys the road map: pick physical
qubits, insert SWAPs where roads are missing, translate to allowed gates.

## 10. Noise
Heat and vibration scramble qubits, like a whispered message degrading in
the telephone game. More gates (especially SWAPs) = more exposure = worse
results. We simulate it with depolarizing + readout errors.

## 11. Fidelity
A 0-100% score: how close the real state is to the ideal Bell state.
F = (1 + <XX> - <YY> + <ZZ>)/4, where each <PP> is measured by its own
circuit (see `quantum/fidelity/`).

## 12. Graphs / NetworkX
A topology is a graph: vertices = qubits, edges = allowed two-qubit gates.
`diameter` = longest shortest path = worst-case trip length. Our comparison
rests on graph theory: vertices = qubits, edges = allowed two-qubit gates.
