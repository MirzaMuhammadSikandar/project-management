from .models import TimelineEvent

# ------------------- Event Logging -------------------------
def log_event(project, user, event_type, description):
    TimelineEvent.objects.create(
        project=project,
        user=user,
        event_type=event_type,
        description=description
    )
    