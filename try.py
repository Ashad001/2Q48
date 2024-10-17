import numpy as np
import tensorflow as tf
import tensorflow_quantum as tfq
import cirq
from grid import Grid
from scipy.optimize import minimize

class Quantum2048Solver:
    def __init__(self, grid_size):
        self.grid = Grid(grid_size)
        self.n_qubits = 4  # Number of qubits in the circuit

    def initialize_quantum_circuit(self):
        # Create a quantum circuit with 4 qubits
        qubits = cirq.GridQubit.rect(1, self.n_qubits)
        circuit = cirq.Circuit()
        return qubits, circuit

    def encode_grid_state(self, grid):
        # Encode grid state into a quantum circuit
        qubits, circuit = self.initialize_quantum_circuit()
        state_vector = self.grid_to_state_vector(grid)
        for i, value in enumerate(state_vector):
            if value:
                circuit.append(cirq.X(qubits[i]))  # Apply X gate based on grid state
        return qubits, circuit

    def grid_to_state_vector(self, grid):
        # Flatten grid and normalize to create a state vector
        flat_grid = np.array(grid).flatten()
        state_vector = np.zeros(2**self.n_qubits)
        for i, value in enumerate(flat_grid):
            if value:
                state_vector[i] = 1
        return state_vector

    def apply_quantum_algorithm(self, circuit, params):
        # Apply parameterized quantum gates
        qubits = circuit.all_qubits()
        for i in range(self.n_qubits):
            circuit.append(cirq.ry(params[i])(qubits[i]))  # Apply rotation around Y-axis
        circuit.append(cirq.measure(*qubits))
        return circuit

    def interpret_quantum_result(self, result):
        # Interpret the quantum result to decide the next move
        counts = result.histogram(key='result')
        max_count = max(counts, key=counts.get)
        
        # Convert the measurement result to an action
        move_map = {
            '0000': 'w',  # Up
            '0001': 's',  # Down
            '0010': 'a',  # Left
            '0011': 'd',  # Right
        }
        return move_map.get(max_count, 'w')  # Default to 'w' if no match

    def optimize_parameters(self):
        # Define objective function for optimization
        def objective(params):
            qubits, circuit = self.encode_grid_state(self.grid.grid)
            circuit = self.apply_quantum_algorithm(circuit, params)

            # Convert circuit to TensorFlow Quantum circuit
            tfq_circuit = tfq.convert_to_tensor([circuit])
            model = tf.keras.models.Sequential([
                tf.keras.layers.Input(shape=(), dtype=tf.string),
                tfq.layers.PQC(circuit, tf.keras.layers.Dense(1))
            ])
            model.compile(optimizer='adam', loss='mse')

            # Dummy quantum data and labels (for demonstration)
            quantum_data = tfq.convert_to_tensor([circuit])
            labels = np.array([0])  # Dummy reward value
            model.fit(quantum_data, labels, epochs=1, verbose=0)

            # Get reward based on the model's prediction
            prediction = model.predict(tfq.convert_to_tensor([circuit]))[0]
            return -prediction  # Minimize negative reward

        # Initial guess for parameters
        initial_params = np.random.rand(self.n_qubits)
        # Perform optimization
        res = minimize(objective, initial_params, method='Nelder-Mead')
        return res.x

    def quantum_move(self):
        # Initialize the quantum circuit and optimize parameters
        optimized_params = self.optimize_parameters()
        qubits, circuit = self.encode_grid_state(self.grid.grid)
        circuit = self.apply_quantum_algorithm(circuit, optimized_params)

        # Simulate the quantum circuit
        simulator = cirq.Simulator()
        result = simulator.run(circuit, repetitions=1024)
        
        # Interpret the result to get the next action
        action = self.interpret_quantum_result(result)
        
        # Execute the action in the classical grid environment
        next_state, reward, done = self.grid.step(action)
        # self.grid.render()
        return next_state, reward, done

    def play_game(self):
        while not self.grid.is_full():
            _, reward, done = self.quantum_move()
            self.grid.render()
            if done:
                print("Game Over. Final Score:", self.grid.score)
                break

# Example usage:
solver = Quantum2048Solver(grid_size=4)
solver.play_game()
