from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from autenticacion import urls

class login_required():
    def __init__(self, redirect_url):
        self.redirect_url = redirect_url
        
    def __call__(self, view):
        def view_wrapper(request):
            if not request.user.is_authenticated():
                return HttpResponseRedirect( "{}?next={}".format( reverse(urls.LOGIN_NAME), request.path_info ) )
            else:
                return view(request)
        
        return view_wrapper
