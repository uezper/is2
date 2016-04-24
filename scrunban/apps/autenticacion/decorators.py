from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from scrunban.settings import base as base_settings

class login_required():
    """
    Decorador para solicitar autentificación en una vista.
    Redirige la solicitud a la página de logeo con los parámetros para volver a la dirección
    originalmente solicitada.

    :param redirect_url: La dirección originalmente solicitada. Se agrega dentro de la URL.

    """
    def __init__(self, redirect_url):
        """
        Inicializador. Se almacena la url solicitada.
        """
        self.redirect_url = redirect_url
        
    def __call__(self, view):
        """
        Retorna una función que extiende la funcionalidad de las vistas con este decorador.

        Args:
            view: La vista donde se aplica el decorador.

        Retuns:
            Un envolvente de la vista para proteger de usuarios sin autentificación.
        """
        def view_wrapper(request):
            if not request.user.is_authenticated():
                # El hashtag (#) es necesario para poder utilizar $location.search() en el script.
                return HttpResponseRedirect( "{}#?next={}".format( reverse( base_settings.LOGIN_NAME ), request.path_info ) )
            else:
                return view(request)
        
        return view_wrapper
