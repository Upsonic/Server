from django.utils.deprecation import MiddlewareMixin

from dash import settings
class DisableCSRF(MiddlewareMixin):
   def process_request(self, request):

         setattr(request, '_dont_enforce_csrf_checks', True)