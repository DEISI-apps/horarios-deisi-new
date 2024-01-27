"""projeto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path, include

app_name = 'horarios'

urlpatterns = [
    path('', views.horarios_view, name='horarios'),
    path('turmas/', views.turmas_view, name='turmas'),
    path('disciplinas/', views.disciplinas_view, name='disciplinas'),
    path('disciplina_avulso/<str:disciplina_id>', views.disciplina_avulso_view, name='disciplina_avulso'),
    path('cancelar_inscricao/<str:disciplina_id>', views.cancelar_inscricao_view, name='cancelar_inscricao'),
    path('disciplina_do_ano_remover/<str:disciplina_id>', views.disciplina_do_ano_remover_view, name='disciplina_do_ano_remover'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='fogot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('registar_aluno/', views.registar_aluno, name='registar_aluno'),
]
