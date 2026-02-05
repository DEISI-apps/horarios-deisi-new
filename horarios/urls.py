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
    path('lista-horarios/', views.lista_horarios_view, name='lista-horarios'),
    path('turmas/', views.turmas_view, name='turmas'),
    path('sem_turma/', views.sem_turma_view, name='sem_turma'),
    path('turmas_corrige/<str:max_disciplinas>/<str:ano_que_deve_estar>', views.turmas_corrige_view, name='turmas_corrige'),
    path('disciplinas/', views.disciplinas_view, name='disciplinas'),
    path('disciplina_avulso/<str:disciplina_id>/<int:inscrito_nalguma>', views.disciplina_avulso_view, name='disciplina_avulso'),
    path('cancelar_inscricao/<str:disciplina_id>', views.cancelar_inscricao_view, name='cancelar_inscricao'),
    path('fazer_inscricao/<str:disciplina_id>', views.fazer_inscricao_mesmo_ano_view, name='fazer_inscricao'),

    path('finalizar/', views.finalizar_view, name='finalizar'),
    path('report-turmas/', views.report_view, name='report-turmas'),
    path('report-alunos/', views.report_alunos_view, name='report-alunos'),
    path('report-alunos-sem-turma/', views.report_alunos_nao_escolheram_turma_view, name='report-alunos-sem-turma'),

    path('lista_disciplinas/', views.lista_disciplinas_view, name="lista_disciplinas"),
    path('turmas_disciplina/<str:disciplina_id>', views.lista_turmas_de_disciplina_view, name="turmas_disciplina"),
    path('alunos_turma/<str:turmadisciplina_id>', views.lista_alunos_turma_view, name="alunos_turma"),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('registar_aluno/', views.registar_aluno, name='registar_aluno'),

    path('turma-alunos/<int:disciplina_id_dsdeisi>/<str:turma_nome>', views.turma_alunos_view)
]
