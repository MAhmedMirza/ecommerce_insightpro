from threading import Thread
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, make_response
import pandas as pd
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
import os
import uuid
from datetime import datetime
from . import db
from .models import UploadedDatasets, ETLLog
from app.tasks import run_etl_process

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    current_app.logger.info("Upload endpoint hit")  # Debug log
    if request.method == 'POST':
        current_app.logger.info("POST request received")  # Debug log
        
        if 'file' not in request.files:
            current_app.logger.error("No file part in request")  # Debug log
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        file = request.files['file']
        current_app.logger.info(f"File received: {file.filename}")  # Debug log
        
        if not file or file.filename == '':
            current_app.logger.error("Empty file")  # Debug log
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        try:
            if not file.filename.lower().endswith('.csv'):
                current_app.logger.error("Invalid file type")  # Debug log
                return jsonify({'success': False, 'message': 'Only CSV files are allowed'}), 400

            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            
            current_app.logger.info(f"Upload folder: {upload_folder}")  # Debug log
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, unique_filename)
            current_app.logger.info(f"Saving to: {file_path}")  # Debug log
            
            # Save file with explicit error handling
            try:
                file.save(file_path)
                if not os.path.exists(file_path):
                    raise RuntimeError("File save failed silently")
                current_app.logger.info("File saved successfully")  # Debug log
            except Exception as save_error:
                current_app.logger.error(f"File save failed: {str(save_error)}")  # Debug log
                return jsonify({
                    'success': False,
                    'message': 'Failed to save file'
                }), 500
            
            # Database operations
            current_app.logger.info("Creating dataset record")  # Debug log
            new_dataset = UploadedDatasets(
                UserID=current_user.UserID,
                OriginalFileName=original_filename,
                StoredFileName=unique_filename,
                Status='Processing',
            )
            db.session.add(new_dataset)
            db.session.commit()
            current_app.logger.info(f"Dataset record created: {new_dataset.DatasetID}")  # Debug log
            
            # Start Celery task
            current_app.logger.info("Starting Celery task")  # Debug log
            task = run_etl_process.delay(
                current_user.UserID,
                new_dataset.DatasetID,
                file_path
            )
            
            new_dataset.TaskID = task.id
            db.session.commit()
            current_app.logger.info(f"Celery task started: {task.id}")  # Debug log
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processing started!',
                'dataset_id': new_dataset.DatasetID,
                'task_id': task.id,
                'redirect_url': url_for('main.dashboard', dataset_id=new_dataset.DatasetID),
            })
            
        except Exception as e:
            current_app.logger.error(f"Upload failed: {str(e)}", exc_info=True)  # Debug log
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error processing file: {str(e)}'
            }), 500
    
    return render_template('upload.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    dataset_id = request.args.get('dataset_id')
    dataset = UploadedDatasets.query.filter_by(
        DatasetID=dataset_id,
        UserID=current_user.UserID
    ).first_or_404()
    
    etl_logs = ETLLog.query.filter_by(
        DatasetID=dataset_id,
        UserID=current_user.UserID
    ).order_by(ETLLog.StartTime.desc()).all()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         dataset=dataset,
                         etl_logs=etl_logs)

@main_bp.route('/api/task-status/<task_id>')
@login_required
def task_status(task_id):
    task = run_etl_process.AsyncResult(task_id)

    response = {
        'state': task.state,
        'status': task.status,
        'ready': task.ready(),
        'successful': task.successful()
    }

    if task.state == 'In Progress':
        response.update({
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'progress': task.info.get('progress', 0),
            'status_message': task.info.get('status', '')
        })
    elif task.ready():
        if task.failed():
            error_message = str(task.result)
            response.update({
                'error': error_message
            })
        else:
            response['result'] = task.result if isinstance(task.result, dict) else str(task.result)

    resp = make_response(jsonify(response))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp

@main_bp.context_processor
def inject_user():
    return dict(user=current_user)

@main_bp.route('/forgetpassword')
def forgetpassword():
    return render_template('auth/forgetpassword.html')