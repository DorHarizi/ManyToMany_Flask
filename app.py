from flask import Flask, render_template, request
import numpy as np
from many_to_many_assignment import kuhn_munkers_backtracking

app = Flask(__name__)

def process_data(matrix_str, agent_vector_str, task_vector_str):
    # Parse matrix string into a NumPy array
    matrix = np.array(eval(matrix_str))
    
    # Parse agent vector string into a NumPy array
    agent_vector = np.array(eval(agent_vector_str))
    
    # Parse task vector string into a NumPy array
    task_vector = np.array(eval(task_vector_str))
    
    # Call the algorithm function with parsed data
    result = kuhn_munkers_backtracking(matrix, agent_vector, task_vector)
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        matrix_str = request.form.get('matrix')
        agent_vector_str = request.form.get('agent_vector')
        task_vector_str = request.form.get('task_vector')

        output = process_data(matrix_str, agent_vector_str, task_vector_str)

        return render_template('result.html', result=output)

if __name__ == '__main__':
    app.run(debug=True)
