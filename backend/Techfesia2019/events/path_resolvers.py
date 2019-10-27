import os
from events.models import Event


def resolve_events():
    return 'events'


def resolve_event_data_folder(event: Event):
    return os.path.join(resolve_events(), event.public_id)


def resolve_event_picture_path(event: Event):
    return os.path.join(resolve_event_data_folder(event), 'event_picture')


def resolve_event_logo_path(event: Event):
    return os.path.join(resolve_event_data_folder(event), 'event_logo')
