from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from forms import LoginForm, RegisterForm
import os
import fitz
from PIL import Image
from reportlab.pdfgen import canvas
from io import BytesIO
import pytesseract
import uuid

app = Flask(__name__)
app.secret_key = 'snapdocs_secret_key'

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# In-memory storage
users = {}
comments = {}
tags = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        users[form.username.data] = {'password': form.password.data}
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return redirect(url_for('preview_file', filename=filename))
    return redirect(url_for('index'))

@app.route('/preview/<filename>')
def preview_file(filename):
    return render_template('preview.html', filename=filename)

@app.route('/convert-to-pdf/<filename>')
def convert_to_pdf(filename):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)
    pdf_path = os.path.join(app.config['CONVERTED_FOLDER'], f"{uuid.uuid4()}.pdf")
    image.save(pdf_path, "PDF", resolution=100.0)
    return send_from_directory(app.config['CONVERTED_FOLDER'], os.path.basename(pdf_path))

@app.route('/extract-text/<filename>')
def extract_text(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = ""
    if filename.lower().endswith(".pdf"):
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
    else:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
    return render_template('result.html', text=text, filename=filename)

@app.route('/add-comment/<filename>', methods=['POST'])
def add_comment(filename):
    comment = request.form.get('comment')
    comments.setdefault(filename, []).append(comment)
    return redirect(url_for('view_comments', filename=filename))

@app.route('/view-comments/<filename>')
def view_comments(filename):
    file_comments = comments.get(filename, [])
    return render_template('comment.html', filename=filename, comments=file_comments)

@app.route('/add-tag/<filename>', methods=['POST'])
def add_tag(filename):
    tag = request.form.get('tag')
    tags.setdefault(filename, []).append(tag)
    return redirect(url_for('view_tags', filename=filename))

@app.route('/view-tags/<filename>')
def view_tags(filename):
    file_tags = tags.get(filename, [])
    return render_template('tagging.html', filename=filename, tags=file_tags)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)
    app.run(debug=True)
