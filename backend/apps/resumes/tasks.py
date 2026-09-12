from celery import shared_task


@shared_task
def process_resume_task(resume_id: int) -> None:
    """Runs the resume parsing pipeline asynchronously via Celery."""
    from .models import Resume
    from .services import process_resume

    resume = Resume.objects.get(id=resume_id)
    process_resume(resume)
