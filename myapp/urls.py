from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import home, agregar, detalle_pieza, listado_piezas, actualizar_datos, actualizar_img, eliminar_pieza, registro, suspender, editar_cuenta

urlpatterns =[
    path('', home, name="home"),
    path('agregar/', agregar, name="agregar"),
    path('pieza/<int:id>/', detalle_pieza, name='detalle_pieza'),
    path('listado-piezas/', listado_piezas, name="listado_piezas"),
    path('actualizar-img/<id>/', actualizar_img, name="actualizar_img"),
    path('actualizar-datos/<id>/', actualizar_datos, name='actualizar_datos'),
    path('eliminar-pieza/<id>/', eliminar_pieza, name='eliminar_pieza'),
    path('registro/', registro, name='registro'),
    path('pieza/suspender/<int:id>/', suspender, name='suspender'),
    path('editar_cuenta/', editar_cuenta, name='editar_cuenta'),
    path('translate/', views.translate_text, name='translate_text'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
        name='password_reset'
    ),
    # Asegúrate de incluir las otras vistas relacionadas
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]

