from django.http import HttpResponseForbidden
from rest_framework_jwt.views import ObtainJSONWebToken


class SessionJWTLogin(ObtainJSONWebToken):

    def post(self, request, format=None, *args, **qwargs):
        response = super(SessionJWTLogin, self).post(request, format, *args, **qwargs)
        if 'token' in response.data:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.object.get('user') or request.user
                if user.id is None:
                    return HttpResponseForbidden("User not Authorized")
                response.data.update({'user_id': user.id})
        return response
