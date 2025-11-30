import binascii
import os
from django.db import models
from rest_framework import authentication, exceptions

from .models import Usuario

def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()

class UsuarioAuthToken(models.Model):
    """
    Token simple ligado a Usuario (no depende de django.contrib.auth.models.User).
    """
    key = models.CharField(max_length=40, primary_key=True)
    usuario = models.ForeignKey(Usuario, related_name='auth_tokens', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'USUARIO_AUTHTOKEN'

    def __str__(self):
        return f"Token for {self.usuario.correo_usuario}"

    @classmethod
    def create(cls, usuario):
        key = generate_key()
        return cls.objects.create(key=key, usuario=usuario)


class UsuarioTokenAuthentication(authentication.BaseAuthentication):
    """
    Autenticación por cabecera: Authorization: Token <key>
    Retorna la instancia Usuario como request.user y el token como request.auth.
    """
    keyword = 'Token'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Token no proporcionado.'
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = 'Formato inválido para Authorization header.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Token con encoding inválido.')

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            token = UsuarioAuthToken.objects.select_related('usuario').get(key=key)
        except UsuarioAuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido.')

        usuario = token.usuario
        if usuario.estado_usuario != 'ACTIVO':
            raise exceptions.AuthenticationFailed('Usuario inactivo.')

        # devolver (usuario, token)
        return (usuario, token)

    def authenticate_header(self, request):
        return self.keyword
