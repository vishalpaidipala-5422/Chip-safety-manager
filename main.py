from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from io import BytesIO
import tempfile
import os
import shutil
import numpy as np

tool = Flask(__name__)
tool.secret_key = 'supersecretkey'
tool.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(tool.config['UPLOAD_FOLDER']):
    os.makedirs(tool.config['UPLOAD_FOLDER'])

login_manager = LoginManager()
login_manager.init_app(tool)
login_manager.login_view = 'login'


# Dummy user model
class User(UserMixin):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# In-memory user storage
users = {'admin': User(id=1, username='admin', password='password')}


@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None


@tool.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return redirect(url_for('login'))


@tool.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(url_for('main'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@tool.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@tool.route("/main")
def main():
    return render_template('mainpage.html')


@tool.route('/part2')
def part2():
    return render_template('part2.html')


@tool.route('/part3')
def part3():
    return render_template('part3.html')


@tool.route('/part4')
def part4():
    return render_template('part4.html')


@tool.route('/part5')
def part5():
    return render_template('part5.html')


@tool.route('/part6')
def part6():
    return render_template('part6.html')


@tool.route('/part8')
def part8():
    return render_template('part8.html')


@tool.route('/part9')
def part9():
    return render_template('part9.html')


@tool.route('/part11')
def part11():
    return render_template('part11.html')


@tool.route('/safety_plan')
def safety_plan():
    return render_template('safety_plan.html')


@tool.route('/upload', methods=['POST'])
def process_file():
    file = request.files['file']

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, 'uploaded_file.xlsx')

    # Save the file to the temporary directory
    file.save(temp_file_path)
    session['file_path'] = temp_file_path
    session['temp_dir'] = temp_dir

    # Read the Excel file to get sheet names
    excel_file = pd.ExcelFile(temp_file_path)
    sheet_names = excel_file.sheet_names

    return render_template('combined_form.html', sheet_names=sheet_names)


@tool.route('/process_file', methods=['POST'])
def process_and_search():
    sheet_name = request.form['sheet_name']
    search_query = request.form['search_query']
    file_path = session.get('file_path')

    # Read the selected sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Replace NaN or float values with an empty string
    df = df.replace([np.nan, 'nan', 'NaN', 'None', np.inf, -np.inf],
                    '',
                    regex=True)
    df = df.applymap(lambda x: ''
                     if isinstance(x, (float, np.float64, np.float32)) else x)

    # Convert DataFrame to list of dictionaries for easier handling in the template
    df_dict = df.to_dict(orient='records')

    # Find positions of the search string
    mask = df.applymap(lambda x: search_query.lower() in x.lower()
                       if isinstance(x, str) else False)
    positions = list(zip(*mask.to_numpy().nonzero()))

    # Enumerate the rows and columns, and prepare the data for the template
    enumerated_data = [(i, list(enumerate(row.items())))
                       for i, row in enumerate(df_dict)]

    return render_template('combined_form.html',
                           sheet_names=[sheet_name],
                           df=enumerated_data,
                           sheet_name=sheet_name,
                           search_query=search_query,
                           positions=positions)


@tool.route('/fill_values', methods=['POST'])
def fill_values():
    sheet_name = request.form['sheet_name']
    search_query = request.form['search_query']
    file_path = session.get('file_path')
    temp_dir = session.get('temp_dir')

    # Read the selected sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Replace NaN or float values with an empty string
    df = df.replace([np.nan, 'nan', 'NaN', 'None', np.inf, -np.inf],
                    '',
                    regex=True)
    df = df.applymap(lambda x: ''
                     if isinstance(x, (float, np.float64, np.float32)) else x)

    # Fill the user inputs at the corresponding cells
    for pos in request.form:
        if pos not in ['sheet_name', 'search_query']:
            row, col = map(int, pos.split('_'))
            df.iat[row, col] = request.form[pos]

    # Save the modified DataFrame to a new Excel file, preserving the original
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        with pd.ExcelFile(file_path) as original_file:
            for sheet in original_file.sheet_names:
                original_data = pd.read_excel(file_path, sheet_name=sheet)
                if sheet == sheet_name:
                    original_data = df
                original_data.to_excel(writer, sheet_name=sheet, index=False)

    output.seek(0)

    # Clean up the temporary file and directory
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error deleting temporary files: {e}")

    return send_file(output, download_name='modified.xlsx', as_attachment=True)


if __name__ == "__main__":
    tool.run(host='0.0.0.0', debug=True)
