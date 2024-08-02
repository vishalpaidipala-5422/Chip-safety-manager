from flask import Flask, request, render_template, send_file, session
import pandas as pd
from io import BytesIO
import os

tool = Flask(__name__)
tool.secret_key = 'supersecretkey'
tool.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(tool.config['UPLOAD_FOLDER']):
    os.makedirs(tool.config['UPLOAD_FOLDER'])


@tool.route("/")
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
    column_data = df[columns[0]].dropna().unique()  # Unique values from the first column as an example
    return render_template('select_column.html', columns=columns, data=column_data)

@tool.route('/fill_data', methods=['POST'])
def fill_data():
    return render_template("safety_plan.html")


if __name__ == "__main__":
    tool.run(host='0.0.0.0', debug=True)
