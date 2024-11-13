# import pandas as pd
# import numpy as np
# from fununctions import DataEngineeringClass
# from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_file
# import secrets
# import os
# from werkzeug.utils import secure_filename

# class DataNotAvailable(Exception):
#     """Custom exception for handling missing data scenarios."""
#     def __init__(self, message="Data not available"):
#         self.message = message
#         super().__init__(self.message)

# app = Flask(__name__, template_folder='templates')
# cls_obj = DataEngineeringClass()
# app.secret_key = secrets.token_hex(16)

# # upload filder
# UPLOAD_FOLDER = 'Documents'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ALLOWED_EXTENSIONS = {'csv'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_files():
#     # Retrieve the uploaded file
#     customer_order_file = request.files.get('customer_order_file')
#     number_of_order = request.form.get('number_of_order')

#     # Check if number_of_order is provided and not empty
#     if number_of_order is None or number_of_order.strip() == '':
#         flash('Please enter the number of orders.')
#         return redirect(request.url)

#     try:
#         number_of_order = int(number_of_order)  # Convert to integer
#     except ValueError:
#         flash('Invalid input for the number of orders. Please enter a valid number.')
#         return redirect(request.url)

#     # Ensure the uploaded file has a .csv extension
#     if not customer_order_file or not allowed_file(customer_order_file.filename):
#         flash('Invalid file format. Please upload a CSV file only.')
#         return redirect(request.url)

#     # Secure the file name and save it to the upload folder
#     filename = secure_filename(customer_order_file.filename)
#     customer_order_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#     # Read the uploaded CSV into a pandas DataFrame
#     customer_order_df = pd.read_csv(file_path)

#     # Call your feature engineering function (assuming customer_order_df and number_of_order are inputs)
#     result = cls_obj.df_feature_engineering(customer_order_df, number_of_order)
    
#     return  render_template('result_display.html', result_df=result)

# @app.route('/download_csv_trigger', methods=['GET'])
# def download_csv_trigger():
#     # Trigger the download of the CSV file
#     return redirect(url_for('download_csv'))

# @app.route('/download_csv', methods=['GET'])
# def download_csv():
#     try:
#         # csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Selected Orders.csv')
#         csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.csv')

#         if os.path.exists(csv_path):
#             # return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='Selected Orders.csv')
#             return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='result.csv')
#         else:
#             return jsonify({'error': 'File not found'}), 404
#     except Exception as e:
#         return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)


import pandas as pd
import numpy as np
from fununctions import DataEngineeringClass
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, send_file
import secrets
import os
from werkzeug.utils import secure_filename

class DataNotAvailable(Exception):
    """Custom exception for handling missing data scenarios."""
    def __init__(self, message="Data not available"):
        self.message = message
        super().__init__(self.message)

app = Flask(__name__, template_folder='templates')
cls_obj = DataEngineeringClass()
app.secret_key = secrets.token_hex(16)

# upload folder
UPLOAD_FOLDER = 'Documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Retrieve the uploaded file
    customer_order_file = request.files.get('customer_order_file')
    number_of_order = request.form.get('number_of_order')

    # Check if number_of_order is provided and not empty
    if number_of_order is None or number_of_order.strip() == '':
        flash('Please enter the number of orders.')
        return redirect(request.url)

    try:
        number_of_order = int(number_of_order)  # Convert to integer
    except ValueError:
        flash('Invalid input for the number of orders. Please enter a valid number.')
        return redirect(request.url)

    # Ensure the uploaded file has a .csv extension
    if not customer_order_file or not allowed_file(customer_order_file.filename):
        flash('Invalid file format. Please upload a CSV file only.')
        return redirect(request.url)

    # Secure the file name and save it to the upload folder
    filename = secure_filename(customer_order_file.filename)
    customer_order_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Read the uploaded CSV into a pandas DataFrame
    customer_order_df = pd.read_csv(file_path)

    # Call your feature engineering function (assuming customer_order_df and number_of_order are inputs)
    result_df = cls_obj.df_feature_engineering(customer_order_df, number_of_order)
    
    # Save the result to a new CSV file
    result_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.csv')
    result_df.to_csv(result_csv_path, index=False)

    # Render the results in HTML table
    return render_template('result_display.html', filtered_df=result_df.to_html(classes='table table-striped table-bordered', index=False))

@app.route('/download_csv_trigger', methods=['GET'])
def download_csv_trigger():
    # Trigger the download of the CSV file
    return redirect(url_for('download_csv'))

@app.route('/download_csv', methods=['GET'])
def download_csv():
    try:
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.csv')

        if os.path.exists(csv_path):
            return send_file(csv_path, mimetype='text/csv', as_attachment=True, download_name='result.csv')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)


