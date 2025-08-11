# upload.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_from_directory, current_app
import os
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
upload = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'webp', 'pdf', 'ico'}
MAX_FILESIZE = 10 * 1024 * 1024
B_TO_MB= 1024*1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if request.method == 'POST':
        if 'media' not in request.files:
            flash(message='No file part', category='error')
            return redirect(request.url)
        file = request.files['media']
        if file.filename == '':
            flash(message='No selected file', category='error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # --- 1. Check file size (10 MB limit) ---
            file.seek(0, os.SEEK_END)
            file_size = file.tell()  
            file.seek(0)  
            if file_size > MAX_FILESIZE:
                flash(message=f'File size exceeds {MAX_FILESIZE/B_TO_MB}MB limit', category='error')
                return redirect(request.url)
            # --- 2. Check if file already exists ---
            file_path = os.path.join(upload_folder, filename)
            if os.path.exists(file_path):
                flash(message='A file with that name already exists', category='error')
                return redirect(request.url)
            # Save the file
            file.save(file_path)
            flash(message='File successfully uploaded', category='success')
            return redirect(url_for('upload.browse_media'))
        else:
            flash(message='File type not allowed', category='error')
            return render_template('upload.html', user=current_user)
    accept_string = ",".join(f".{ext.lower()}" for ext in ALLOWED_EXTENSIONS)
    media_files = os.listdir(upload_folder)
    return render_template('upload.html', user=current_user, accept_string=accept_string, media_files=media_files)

@upload.route('/browse')
@login_required
def browse_media():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    media_files = os.listdir(upload_folder)
    return render_template('browse_media.html', media_files=media_files,user=current_user)

@upload.route('/media/<filename>')
@login_required
def media_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

@upload.route('/delete', methods=['POST'])
@login_required
def delete_file():
    filename = request.form.get('filename')
    if not filename:
        flash('No filename provided', 'error')
        return redirect(url_for('upload.upload_file'))

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{filename} deleted successfully.', 'success')
    else:
        flash('File not found.', 'error')

    return redirect(url_for('upload.upload_file'))