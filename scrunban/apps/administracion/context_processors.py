def pending_notes_context(request):
    from apps.proyecto.models import Project
    from apps.administracion.models import Note
    from apps.autenticacion.models import User
    
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

def assignments_context(request):
    from apps.administracion.models import Grained
    from apps.proyecto.models import Team

    teams = Team.teams.filter(user=request.user.user)
    user_stories = []
    for team in teams:
        graineds = Grained.graineds.filter(developers=team)
        for grained in graineds:
            user_story = grained.user_story
            user_stories.append(user_story)

    user_stories.sort(key=lambda x: x.get_weight(), reverse=True)
    
    context = {
        'assignments': user_stories
    }

    return context

def notifications_count_context(request):
    pending_notes_length = len( pending_notes_context(request).get('pending_notes', []) )
    assignments_length = len( assignments_context(request).get('assignments', []) )

    context = {
        'notifications_count': pending_notes_length + assignments_length
    }

    return context
        
def url_names_context(request):
    from scrunban.settings import base as base_settings
    return {'URL_NAMES': base_settings.URL_NAMES }
