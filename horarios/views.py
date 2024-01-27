from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from django.core.mail import send_mail

from .models import *
from .forms import *

import json, random, string
import base64

semestre = 2
ano_lectivo = '23-24'

# Create your views here.

def index_view(request):
    return render(request, 'horarios/index.html')


def horarios_view(request):
    return render(request, 'horarios/horarios.html')



@login_required
def turmas_view(request):

    aluno = Aluno.objects.get(user = request.user)

    if request.method == 'POST':
        turma_id = request.POST['turma']
        turma = Turma.objects.get(id=turma_id)

        if turma.inscritos < turma.lotacao:

            aluno.ano = turma.ano
            aluno.turma = turma.nome
            aluno.save()

            for turmaDisciplina in TurmaDisciplina.objects.filter(disciplina__curso=aluno.curso, disciplina__semestre=semestre):
                if aluno in turmaDisciplina.alunos.all():
                    # desinscrever de todas as turma
                    turmaDisciplina.alunos.remove(aluno)
                if turmaDisciplina.turma == turma and \
                    turmaDisciplina.disciplina.nome != "Fund Programação 2º Sem" and \
                    turmaDisciplina.disciplina.nome != "Matemática I" and \
                    turmaDisciplina.disciplina.nome != "Fundamentos de Física":
                    # inscrever nesta turma
                    turmaDisciplina.alunos.add(aluno)

            return redirect('horarios:turmas')

    horarios = Horario.objects.filter(curso=aluno.curso, ano_lectivo=ano_lectivo, semestre=semestre)

    context = {
        'turmas_por_ano': [
            ([ (turma, turma.inscrito(aluno)) for turma in Turma.objects.filter(curso=aluno.curso, ano=ano0+1).order_by('nome')], horario)
            for ano0,horario in enumerate(horarios)
        ],
        'aluno': aluno,
    }

    return render(request, 'horarios/turmas.html', context)


@login_required
def disciplinas_view(request):

    aluno = Aluno.objects.get(user = request.user)

    if request.method == 'POST':
        disciplina_id = request.POST['disciplina']
        disciplina = Disciplina.objects.get(id=disciplina_id)

        accao = request.POST['accao']

        if accao == "desinscrever":

            for turma in disciplina.turmas.all():
                if aluno in turma.alunos.all():
                    turma.alunos.remove(aluno)

            disciplina.alunos.remove(aluno)


        else:
            disciplina.alunos.add(aluno)

        disciplina.save()


    context = {
        'disciplinas_por_ano': [
            [ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=1).order_by('nome')],
            [ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=2).order_by('nome')],
            [ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=3).order_by('nome')],
         ],
        'aluno': aluno,
        'turma': aluno.turma,
        'ano': aluno.ano,
        'semestre': semestre,
    }

    return render(request, 'horarios/disciplinas.html', context)



@login_required
def disciplina_avulso_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)
    disciplina = Disciplina.objects.get(id=disciplina_id)

    inscrito_nalguma = False
    turmasdisciplina = disciplina.turmasdisciplinas.all()
    for tdisc in turmasdisciplina:
            if aluno in tdisc.alunos_avulso.all():
                inscrito_nalguma = True

    if request.method == 'POST':

        turmadisciplina_id = request.POST['turmadisciplina']
        turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)



        if turmadisciplina.inscritos_avulso < turmadisciplina.turma.lotacao_avulso:

            # desinscrever da outra turma, se estiver inscrito
            for tdisc in turmasdisciplina:
                if aluno in tdisc.alunos_avulso.all():
                    tdisc.alunos_avulso.remove(aluno)

            # inscrever nesta turma
            turmadisciplina.alunos_avulso.add(aluno)

            return redirect('horarios:disciplinas')

    context = {
        'disciplina': disciplina,
        'turmasdisciplina': disciplina.turmasdisciplinas.all(),
        'inscrito_nalguma': inscrito_nalguma,
        'aluno':aluno,
    }

    return render(request, 'horarios/disciplina_avulso.html', context)


def cancelar_inscricao_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)
    disciplina = Disciplina.objects.get(id=disciplina_id)

    for tdisc in disciplina.turmasdisciplinas.all():
        if aluno in tdisc.alunos_avulso.all():
            tdisc.alunos_avulso.remove(aluno)
        if aluno in tdisc.alunos.all():
            tdisc.alunos.remove(aluno)

    return redirect('horarios:disciplinas')



@login_required
def disciplina_do_ano_remover_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)
    disciplina = Disciplina.objects.get(id=disciplina_id)

    for tdisc in TurmaDisciplina.objects.filter(turma__curso=aluno.curso, turma__ano=aluno.ano):
        if aluno in tdisc.alunos.all():
            turma_inscrito = tdisc.turma
            break

    turmadisciplina = TurmaDisciplina.objects.get(disciplina=disciplina, turma = turma_inscrito)
    inscrito = True if aluno in turmadisciplina.alunos.all() else False

    if request.method == 'POST':

        turmadisciplina_id = request.POST['turmadisciplina']
        turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)

 # debug       lixo = TurmaDisciplina.objects.get(ano=1)
        # reinscrever nesta turma
        turmadisciplina.alunos.add(aluno)
        return redirect('horarios:disciplinas')

    context = {
        'disciplina': disciplina,
        'turmadisciplina': turmadisciplina,
        'inscrito': inscrito,
        'aluno':aluno,
    }

    return render(request, 'horarios/disciplina_do_ano_remover.html', context)


@login_required
def wwwinscrever_disciplina_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)

    disciplina = TurmaDisciplina.objects.get(id=disciplina_id)
    disciplina.alunos.add(aluno)


    context = {
        'disciplinas': Disciplina.objects.filter(semestre=1).order_by('ano', 'semestre', 'nome'),
        'aluno': Aluno.objects.get(user = request.user),
    }

    return render(request, 'horarios/disciplinas.html', context)



@login_required
def horario_view(request):
    pass




def login_view(request):


    if request.method == 'POST':
        credential = request.POST['credential'] # poderá ser email ou username
        password = request.POST['password']

        # testa se é um email
        user = authenticate(request, email=credential, password=password)

        if user is not None:
            login(request, user)
            return redirect('horarios:turmas')

        else:

            # testa se é um username
            user = authenticate(request, username=credential, password=password)

            if user is not None:
                login(request, user)
                return redirect('horarios:horarios')

        return render(request, 'horarios/login.html', {
            'message': 'Credenciais inválidas'
        })

    return render(request, 'horarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('horarios:horarios')


def forgot_password(request):

  email = request.POST.get('email')

  if not email:
    return render(request, 'horarios/forgot.html', {'error': 'Por favor, insira o seu email.'})

  user = User.objects.filter(email=email).first()

  if not user:
    return render(request, 'horarios/forgot.html', {'error': 'O email inserido não está registado.'})

  token = token = default_token_generator.make_token(user)
  uidb64 = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))

  reset_link = request.build_absolute_uri(f'/reset/{uidb64}/{token}/')

  send_mail(
        'Definição de palavra chave',
        f'Olá,\n\nPediu para redefinir a sua palavra chave, clique por favor no seguinte link:\n\n{reset_link}',
        'lucio.studer@gmail.com',
        [email]
  )

  return render(request, 'horarios/forgot.html', {'success': 'Foi-lhe enviado um email com um link para redefinir a sua senha.'})



def password_reset_confirm(request, uidb64, token):

    try:
        uid = base64.urlsafe_b64decode(uidb64 + '==')
        uid = int.from_bytes(uid, 'big')

        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return render(request, 'horarios/login.html')
            else:
                form = SetPasswordForm(user)
            return render(request, 'horarios/password_reset_confirm.html', {'form':form, 'token':token, 'uidb64':uidb64})
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    form = SetPasswordForm(user)
    return render(request, 'horarios/password_reset_confirm.html', {'form':form, 'token':token, 'uidb64':uidb64})


def registar_aluno(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('horarios:login')
    else:
        form = AlunoForm()

    return render(request, 'horarios/registo_aluno.html', {'form': form})