from django.conf import settings
from googletrans import Translator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import qrcode
from datetime import date
from .forms import AgregarForm, UpdateImg, UpdateForm, CustomUserCreationForm, UpdateCuenta
from .models import Agregar
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from .decorators import user_iniciado
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def home(request):
    query = request.GET.get('query')
    piezas = Agregar.objects.filter(activo=True)

    if query:
        piezas = piezas.filter(titulo__icontains=query)
    mensaje = "No se encontraron resultados para tu búsqueda." if query and not piezas.exists() else ""

    return render(request, 'myapp/home.html', {'piezas': piezas, 'query': query, 'mensaje': mensaje})

@permission_required('myapp.view_agregar')
@login_required(login_url="/accounts/login/")
def agregar(request):
    if request.method == 'POST':
        formulario = AgregarForm(request.POST, request.FILES)
        if formulario.is_valid():
            # Guardar nueva pieza
            nueva_pieza = formulario.save()
            
            # Generar URL y QR
            url_pieza = f"https://AdminQRs.pythonanywhere.com/pieza/{nueva_pieza.id}/"
            qr_img = qrcode.make(url_pieza)
            qr_filename = f'qr_{nueva_pieza.id}.png'
            qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)
            qr_img.save(qr_path)
            
            # Actualizar la pieza con la ruta del QR
            nueva_pieza.codigo_qr = f"qr_codes/{qr_filename}"
            nueva_pieza.save()
            
            # Preparar datos para la vista QR
            qr_url = os.path.join(settings.MEDIA_URL, 'qr_codes', qr_filename)
            mensaje = "Guardado y QR generado con éxito"
            
            # Redirigir a la vista del QR generado
            return render(request, 'myapp/Pieza/qr_generado.html', {
                'qr_url': qr_url,
                'mensaje': mensaje,
            })
        else:
            # Si el formulario no es válido
            data = {'form': formulario}
            return render(request, 'myapp/Pieza/agregar.html', data)
    
    # Si la solicitud es GET
    data = {'form': AgregarForm()}
    return render(request, 'myapp/Pieza/agregar.html', data)

def detalle_pieza(request, id):
    pieza = get_object_or_404(Agregar, id=id)
    return render(request, 'myapp/detalle_pieza.html', {'pieza': pieza})

@permission_required('myapp.view_articulo')
@login_required(login_url="/accounts/login/")
def listado_piezas(request):
    elemento = Agregar.objects.all()
    data = {'elemento': elemento}
    return render(request, 'myapp/pieza_admin.html', data)

@permission_required('myapp.view_imagen')
@login_required(login_url="/accounts/login/")
def actualizar_img(request, id):
    pieza = get_object_or_404(Agregar, id=id)
    data = {'form': UpdateImg(instance=pieza)}
    if request.method == 'POST':
        nueva_img = Agregar.objects.get(id=id)
        formulario = UpdateImg(instance=pieza, data=request.FILES, files=request.FILES)
        if formulario.is_valid():
            nueva_img.Imagen.delete()
            formulario.save()
            return redirect(to="listado_piezas")
        data["form"] = formulario
    return render(request, 'myapp/Pieza/modificar.html', data)

@permission_required('myapp.view_articulo')
@login_required(login_url="/accounts/login/")
def actualizar_datos(request, id):
    pieza = get_object_or_404(Agregar, id=id)
    data = {'form': UpdateForm(instance=pieza)}
    if request.method == 'POST':
        formulario = UpdateForm(data=request.POST, instance=pieza, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="listado_piezas")
        data["form"] = formulario
    return render(request, 'myapp/Pieza/modificar.html', data)

@permission_required('myapp.delete_articulo')
@login_required(login_url="/accounts/login/")
def eliminar_pieza(request, id):
    pieza = get_object_or_404(Agregar, id=id)
    img = Agregar.objects.get(id=id)
    if img.Imagen:
        img.Imagen.delete()
    qr_filename = f'qr_{id}.png'
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)
    if os.path.exists(qr_path):
        os.remove(qr_path)
    pieza.delete()
    return redirect(to="listado_piezas")

@user_iniciado
def registro(request):
    data = {'form': CustomUserCreationForm()}
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            email = formulario.cleaned_data['email']
            dominio_mail = email.split('@')[-1]
            group = Group.objects.get(name='Admin' if dominio_mail == 'usm.cl' else 'Usuario')
            user.groups.add(group)
            login(request, user)
            messages.success(request, "Te has registrado correctamente")
            return redirect(to="home")
        data["form"] = formulario
    return render(request, 'registration/registro.html', data)

def logoutUser(request):
    logout(request)
    return redirect(to='home')

@permission_required('myapp.view_articulo')
def suspender(request, id):
    pieza = get_object_or_404(Agregar, id=id)
    if request.method == 'POST':
        pieza.activo = not pieza.activo
        pieza.save()
        return redirect(to='listado_piezas')

@login_required(login_url="/accounts/login/")
def editar_cuenta(request):
    cuenta = request.user
    data = {'form': UpdateCuenta(instance=cuenta)}
    if request.method == 'POST':
        formulario = UpdateCuenta(data=request.POST, instance=cuenta, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="home")
        data["form"] = formulario
    return render(request, 'myapp/editar_cuenta.html', data)

def translate_text(request):
    if request.method == "GET":
        text = request.GET.get('text', '')
        lang = request.GET.get('lang', 'es')
        translator = Translator()
        translated = translator.translate(text, dest=lang)
        return JsonResponse({"translated_text": translated.text})
    
