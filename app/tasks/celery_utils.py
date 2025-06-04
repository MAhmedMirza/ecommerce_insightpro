from celery import Celery

def make_celery(app):
    """Create and configure a new Celery instance tied to the Flask app"""
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    # Update Celery config from Flask app config
    celery.conf.update(app.config['CELERY'])
    
    # Enable Flask application context for tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery