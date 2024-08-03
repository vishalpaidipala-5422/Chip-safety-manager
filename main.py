from flask import Flask, request, render_template, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
from io import BytesIO
import os

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


@tool.route('/uploader', methods=['POST'])
def uploader():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    file_path = os.path.join(tool.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    session['file_path'] = file_path

    sheets = pd.ExcelFile(file_path).sheet_names
    return render_template('select_sheet.html', sheets=sheets)


@tool.route('/select_columns', methods=['POST'])
def select_columns():
    sheet_name = request.form['sheet']
    session['sheet_name'] = sheet_name
    file_path = session.get('file_path')
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    columns = df.columns.tolist()
    column_data = df[columns[0]].dropna().unique(
    )  # Unique values from the first column as an example
    return render_template('select_column.html',
                           columns=columns,
                           data=column_data)


@tool.route('/fill_data', methods=['POST'])
def fill_data():
    sheet_name = session.get('sheet_name')
    file_path = session.get('file_path')
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Retrieve dropdown selections and user input data
    user_inputs = request.form.getlist('user_input')

    # Validate lengths
    if len(user_inputs) != len(df):
        flash(
            f"Number of inputs ({len(user_inputs)}) does not match number of rows in the sheet ({len(df)}).",
            'error')
        return redirect(url_for('select_columns'))

    # Create new column
    df['New Column'] = user_inputs

    # Output Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    output.seek(0)

    # Clean up the uploaded file
    if os.path.exists(file_path):
        os.remove(file_path)

    return send_file(output,
                     attachment_filename='output.xlsx',
                     as_attachment=True)


if __name__ == "__main__":
    tool.run(host='0.0.0.0', debug=True)
