from apps.proyecto.models import Project
from apps.administracion.models import Note
from apps.autenticacion.models import User

def pending_notes_context(request):
    # TODO Filter notes per permissions
    try:
        user = request.user.user
        print(user)
        pending_notes = list(
            Note.notes.filter(
                aproved=False,
                grained__user_story__project__scrum_master=user
            )
        )
        context = {
            'pending_notes': pending_notes
        }
        return context

    except AttributeError:
        return {}

        
def url_names_context(request):
    from scrunban.settings import base as base_settings
    return {'URL_NAMES': base_settings.URL_NAMES }
