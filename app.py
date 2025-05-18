from flask import Flask, request, render_template
import subprocess
import os
import re
import logging

app = Flask(__name__)

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Map common errors to friendly messages
ERROR_MESSAGES = {
    r"SyntaxError": "Oops! Check your syntax. Did you miss a colon (:) or indent your code correctly?",
    r"NameError": "Hmm, looks like you used a variable that’s not defined. Check your spelling!",
    r"IndentationError": "Indentation issue! Make sure your spaces or tabs are consistent.",
    r"TypeError": "Type mismatch! Are you mixing numbers and text? Check your operations.",
    r"EOFError": "Your program expected more input! Add inputs (one per line) in the input box."
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.form['code']
    user_input = request.form.get('input', '')
    app.logger.debug(f"Received code:\n{code}")
    app.logger.debug(f"Received input:\n{user_input}")
    
    try:
        # Write code to a temporary file
        with open('temp.py', 'w') as f:
            f.write(code)
        # Run code with timeout and input
        process = subprocess.run(
            ['python', 'temp.py'],
            input=user_input,
            text=True,
            capture_output=True,
            timeout=10  # Increased timeout for input-heavy programs
        )
        output = process.stdout
        error = process.stderr
        app.logger.debug(f"Output:\n{output}")
        app.logger.debug(f"Error:\n{error}")
        
        # Handle errors with friendly messages
        if error:
            for err_pattern, friendly_msg in ERROR_MESSAGES.items():
                if re.search(err_pattern, error, re.IGNORECASE):
                    output += f"\nError: {friendly_msg}"
                    break
            else:
                output += f"\nError: {error.strip()}"
    except subprocess.TimeoutExpired:
        output = "Error: Your code took too long to run! Check for infinite loops."
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        output = f"Error: Something went wrong - {str(e)}"
    finally:
        # Clean up
        if os.path.exists('temp.py'):
            os.remove('temp.py')
    
    return {'output': output}

if __name__ == '__main__':
    app.run(debug=True)