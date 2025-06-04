from datetime import datetime
import traceback
from flask import current_app
from app.models import UploadedDatasets
from .etl import run_etl_for_user

# Celery instance will be initialized in create_app()
celery = None

def create_task(celery_app):
    """Factory function to create the ETL task with proper Celery binding"""
    @celery_app.task(
        bind=True,
        name='app.tasks.run_etl_process',
        autoretry_for=(Exception,),
        retry_backoff=True,
        retry_backoff_max=60,
        retry_kwargs={'max_retries': 3},
        max_retries=3,
        time_limit=600,
        soft_time_limit=300
    )
    def run_etl_process(self, user_id, dataset_id, file_path):
        """Celery Task: run ETL Process for a given user and dataset."""
        dataset = UploadedDatasets.query.filter_by(
            DatasetID=dataset_id, 
            UserID=user_id
        ).first()

        if not dataset:
            self.update_state(
                state='FAILURE',
                meta={
                    'exc_type': 'DatasetNotFound',
                    'exc_message': f"Dataset ID {dataset_id} not found for User ID {user_id}",
                    'status': 'failed'
                }
            )
            raise ValueError(f"Dataset ID {dataset_id} not found for User ID {user_id}")

        try:
            dataset.Status = 'In Progress'
            current_app.db.session.commit()

            # Delegate to your existing ETL implementation
            result = run_etl_for_user(user_id, dataset_id, file_path)

            if result.get('status') == 'Success':
                dataset.Status = 'Success'
                current_app.db.session.commit()
                return result
            else:
                dataset.Status = 'Failed'
                current_app.db.session.commit()
                raise RuntimeError(result.get('error_details', 'ETL process failed'))

        except Exception as e:
            current_app.db.session.rollback()
            dataset.Status = 'Failed'
            current_app.db.session.commit()
            raise

    return run_etl_process

# This will be initialized in create_app()
run_etl_process = None