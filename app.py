from flask import Flask, render_template, request, send_file, session, redirect, url_for
import numpy as np
import csv
from ast import literal_eval
from io import StringIO, BytesIO
import secrets
import os
from tempfile import NamedTemporaryFile
from many_to_many_assignment import kuhn_munkers_backtracking

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def process_data(matrix_str, agent_vector_str, task_vector_str):
    matrix = np.array(literal_eval(matrix_str))
    agent_vector = np.array(literal_eval(agent_vector_str))
    task_vector = np.array(literal_eval(task_vector_str))
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
        if matrix_str and agent_vector_str and task_vector_str:
            output = process_data(matrix_str, agent_vector_str, task_vector_str)
            return render_template('result.html', result=output)
        else:
            return render_template('index.html', error_message='Please provide all required fields')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            file = request.files['csv_file']
            if file:
                # Read CSV file
                stream = StringIO(file.stream.read().decode("UTF-8"))
                csv_input = csv.DictReader(stream)

                results = []
                for row in csv_input:
                    matrix_str = row.get('Matrix', '')
                    agent_vector_str = row.get('Agent Vector', '')
                    task_vector_str = row.get('Task Vector', '')

                    if matrix_str and agent_vector_str and task_vector_str:
                        # Process data
                        output = process_data(matrix_str, agent_vector_str, task_vector_str)
                        results.append(output)
                    else:
                        break  # Exit the loop if any of the required fields is missing

                if results:
                    # Prepare output CSV file
                    output_csv = StringIO()
                    writer = csv.writer(output_csv)
                    writer.writerow(['Result'])

                    for result in results:
                        writer.writerow([result])

                    output_csv.seek(0)

                    # Store output CSV in a temporary file
                    temp_file = NamedTemporaryFile(delete=False, mode='w+', newline='')
                    temp_file.write(output_csv.getvalue())
                    temp_file.close()

                    # Store the temporary file path in session
                    session['output_csv_path'] = temp_file.name

                    # Redirect to a new page where user can download the output CSV file
                    return redirect(url_for('result_csv'))

                else:
                    return render_template('index.html', error_message='No valid data found in CSV file.')

        except Exception as e:
            error_message = f"Error processing CSV file: {str(e)}"
            return render_template('index.html', error_message=error_message)

    return render_template('index.html')

@app.route('/result_csv')
def result_csv():
    # Retrieve the output CSV path from session
    output_csv_path = session.get('output_csv_path', None)
    if output_csv_path:
        with open(output_csv_path, 'r', newline='') as file:
            output_csv = file.read()
        return render_template('result_csv.html', output_csv=output_csv)
    else:
        return render_template('index.html', error_message='No output CSV file found')

@app.route('/download')
def download():
    # Retrieve the output CSV path from session
    output_csv_path = session.get('output_csv_path', None)
    if output_csv_path:
        # Prepare response for download
        return send_file(
            output_csv_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='output.csv'  # Provide a download name for the file
        )
    else:
        return render_template('index.html', error_message='No output CSV file found')

if __name__ == '__main__':
    app.run(debug=True)
