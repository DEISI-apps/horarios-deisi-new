from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse


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

inscricoes_abertas = True
semestre = 2
ano_lectivo = '25-26'
lista_disciplinas_recuperacao = ['Matemática I (2º Sem)', 'Fund Programação (2º Sem)', 'Fundamentos de Física (2º Sem)']

# Create your views here.

def index_view(request):
    return render(request, 'horarios/index.html')


def horarios_view(request):

    horarios = Horario.objects.filter(curso__sigla='LEI', ano_lectivo=ano_lectivo, semestre=semestre)
    context = {
        'horarios':horarios,
        'inscricoes_abertas': inscricoes_abertas,
        'semestre':semestre,
        'ano_lectivo':ano_lectivo,
    }

    print("Estou em horarios_view. Autenticado?", request.user.is_authenticated)

    if not request.user.is_authenticated:
        print("nao estou autenticado!")
        return render(request, 'horarios/horarios.html', context)

    try:
        aluno = Aluno.objects.get(user = request.user)
        print("aluno: ", aluno)
    except:
        logout(request)
        return render(request, 'horarios/horarios.html', context)


    turmasdisciplinas = []
    for tdisc in TurmaDisciplina.objects.filter(turma__curso=aluno.curso).order_by('turma__ano'):
        if aluno in tdisc.alunos.all() or aluno in tdisc.alunos_avulso.all():
            turmasdisciplinas.append(tdisc)


    context |= {
        'turmasdisciplinas': turmasdisciplinas,
        'aluno':aluno,
    }

    return render(request, 'horarios/horarios.html', context)



def lista_horarios_view(request):
    return render(request, 'horarios/lista-horarios.html')



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

            return redirect('horarios:disciplinas')

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
def turmas_corrige_view(request, max_disciplinas, ano_que_deve_estar):

    aluno = Aluno.objects.get(user = request.user)

    horarios = Horario.objects.filter(curso=aluno.curso, ano_lectivo=ano_lectivo, semestre=semestre)

    context = {
        'turmas_por_ano': [
            ([ (turma, turma.inscrito(aluno)) for turma in Turma.objects.filter(curso=aluno.curso, ano=ano0+1).order_by('nome')], horario)
            for ano0,horario in enumerate(horarios)
        ],
        'aluno': aluno,
        'turma_corrige': True,
        'max_disciplinas':max_disciplinas,
        'ano_que_deve_estar':ano_que_deve_estar,
    }

    return render(request, 'horarios/turmas.html', context)


@login_required
def sem_turma_view(request):

    aluno = Aluno.objects.get(user = request.user)

    horarios = Horario.objects.filter(curso=aluno.curso, ano_lectivo=ano_lectivo, semestre=semestre)

    context = {
        'turmas_por_ano': [
            ([ (turma, turma.inscrito(aluno)) for turma in Turma.objects.filter(curso=aluno.curso, ano=ano0+1).order_by('nome')], horario)
            for ano0,horario in enumerate(horarios)
        ],
        'sem_turma': True,
    }

    return render(request, 'horarios/turmas.html', context)



@login_required
def disciplinas_view(request):

    aluno = Aluno.objects.get(user = request.user)

    if aluno.turma == None or aluno.turma == '' or aluno.turma == 'None' or aluno.ano not in [1,2,3]:
        return redirect('horarios:sem_turma')

    context = {
        'disciplinas_por_ano': [
            ([ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=0).order_by('nome')]),
            ([ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=1).order_by('nome')]),
            ([ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=2).order_by('nome')]),
            ([ (disciplina,disciplina.inscrito(aluno)) for disciplina in Disciplina.objects.filter(semestre=semestre, curso=aluno.curso, ano=3).order_by('nome')]),
         ],
        'aluno': aluno,
        'turma': aluno.turma,
        'ano': aluno.ano,
        'semestre': semestre,
    }

    return render(request, 'horarios/disciplinas.html', context)



@login_required
def disciplina_avulso_view(request, disciplina_id, inscrito_nalguma):

    aluno = Aluno.objects.get(user = request.user)
    if aluno.turma == None or aluno.turma == '' or aluno.turma == 'None':
        return redirect('horarios:sem_turma')

    disciplina = Disciplina.objects.get(id=disciplina_id)
    turmasdisciplina = disciplina.turmasdisciplinas.all()

    if request.method == 'POST':

        turmadisciplina_id = request.POST['turmadisciplina']
        turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)


        if turmadisciplina.inscritos_avulso < turmadisciplina.turma.lotacao_avulso:

            disciplinas = [
                aluno.turmasdisciplinas.filter(turma__ano=1).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=1).count(),
                aluno.turmasdisciplinas.filter(turma__ano=2).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=2).count(),
                aluno.turmasdisciplinas.filter(turma__ano=3).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=3).count()
            ]
            max_disciplinas = max(disciplinas)
            ano_que_deve_estar = disciplinas.index(max_disciplinas) + 1

            if max_disciplinas >= 3 and aluno.ano != ano_que_deve_estar:
                for turmaDisciplina in aluno.turmasdisciplinas.all():
                    turmaDisciplina.alunos.remove(aluno)
                for turmaDisciplina in aluno.turmasdisciplinas_avulso.all():
                    turmaDisciplina.alunos_avulso.remove(aluno)

                    aluno.turma=None
                    aluno.ano=None
                    aluno.save()

                    return redirect('horarios:turmas_corrige', max_disciplinas=max_disciplinas, ano_que_deve_estar=ano_que_deve_estar)



            # desinscrever da outra turma, se estiver inscrito
            for tdisc in turmasdisciplina:
                if aluno in tdisc.alunos_avulso.all():
                    tdisc.alunos_avulso.remove(aluno)

            # inscrever nesta turma
            turmadisciplina.alunos_avulso.add(aluno)


            return redirect('horarios:disciplinas')

    context = {
        'disciplina': disciplina,
        'turmasdisciplina': turmasdisciplina,
        'inscrito_nalguma': inscrito_nalguma,
        'aluno':aluno,
        'horario': Horario.objects.get(curso=aluno.curso, ano_lectivo=ano_lectivo, semestre=semestre, ano=aluno.ano)

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


    disciplinas = [
                aluno.turmasdisciplinas.filter(turma__ano=1).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=1).count(),
                aluno.turmasdisciplinas.filter(turma__ano=2).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=2).count(),
                aluno.turmasdisciplinas.filter(turma__ano=3).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=3).count()
            ]
    max_disciplinas = max(disciplinas)
    ano_que_deve_estar = disciplinas.index(max_disciplinas) + 1

    if max_disciplinas >= 3 and aluno.ano != ano_que_deve_estar:
        for turmaDisciplina in aluno.turmasdisciplinas.all():
            turmaDisciplina.alunos.remove(aluno)
        for turmaDisciplina in aluno.turmasdisciplinas_avulso.all():
            turmaDisciplina.alunos_avulso.remove(aluno)

        aluno.turma=None
        aluno.ano=None
        aluno.save()

        return redirect('horarios:turmas_corrige', max_disciplinas=max_disciplinas, ano_que_deve_estar=ano_que_deve_estar)


    return redirect('horarios:disciplinas')


def cancelar_inscricao_viewmmmmm(request, turmadisciplina_id):

    aluno = Aluno.objects.get(user = request.user)
    turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)


    if aluno in turmadisciplina.alunos_avulso.all():
            turmadisciplina.alunos_avulso.remove(aluno)
    if aluno in turmadisciplina.alunos.all():
            turmadisciplina.alunos.remove(aluno)


    disciplinas = [
                aluno.turmasdisciplinas.filter(turma__ano=1).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=1).count(),
                aluno.turmasdisciplinas.filter(turma__ano=2).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=2).count(),
                aluno.turmasdisciplinas.filter(turma__ano=3).count() + aluno.turmasdisciplinas_avulso.filter(turma__ano=3).count()
            ]
    max_disciplinas = max(disciplinas)
    ano_que_deve_estar = disciplinas.index(max_disciplinas) + 1

    if max_disciplinas >= 3 and aluno.ano != ano_que_deve_estar:
        for turmaDisciplina in aluno.turmasdisciplinas.all():
            turmaDisciplina.alunos.remove(aluno)
        for turmaDisciplina in aluno.turmasdisciplinas_avulso.all():
            turmaDisciplina.alunos_avulso.remove(aluno)

        aluno.turma=None
        aluno.ano=None
        aluno.save()

        return redirect('horarios:turmas_corrige', max_disciplinas=max_disciplinas, ano_que_deve_estar=ano_que_deve_estar)


    return redirect('horarios:disciplinas')



def lista_disciplinas_view(request):

    disciplinas = Disciplina.objects.filter(semestre=semestre, curso__nome='LEI')

    disciplinas1 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=1)
    disciplinas2 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=2)
    disciplinas3 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=3)

    context = {'disciplinas': [
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas1],
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas2],
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas3],
        ]}

    return render(request, 'horarios/lista_disciplinas.html', context)


def lista_turmas_de_disciplina_view(request, disciplina_id):

    disciplina = Disciplina.objects.get(id=disciplina_id)
    turmasdisciplina = TurmaDisciplina.objects.filter(disciplina=disciplina)

    turmasdisciplina = [(t, len(t.alunos.all()) + len(t.alunos_avulso.all()))for t in turmasdisciplina]

    context = {

        'disciplina': disciplina,
        'turmasdisciplina': turmasdisciplina,
    }
    return render(request, 'horarios/lista_turmas_disciplina.html', context)



def lista_alunos_turma_view(request, turmadisciplina_id):
    turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)

    context = {
        'turmadisciplina': turmadisciplina,
        'alunos': turmadisciplina.alunos.all().order_by('user__first_name', 'user__last_name'),
        'alunos_avulso': turmadisciplina.alunos_avulso.all().order_by('user__first_name', 'user__last_name')
    }
    return render(request, 'horarios/lista_alunos_turmas_disciplina.html', context)



def fazer_inscricao_mesmo_ano_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)
    turma = Turma.objects.get(nome=aluno.turma, ano=aluno.ano)
    disciplina = Disciplina.objects.get(id=disciplina_id)

    turmadisciplina = TurmaDisciplina.objects.get(turma=turma, disciplina=disciplina)
    turmadisciplina.alunos.add(aluno)

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
def finalizar_view(request):

    aluno = Aluno.objects.get(user = request.user)

    turmasdisciplinas = []
    for tdisc in TurmaDisciplina.objects.filter(turma__curso=aluno.curso):
        if aluno in tdisc.alunos.all() or aluno in tdisc.alunos_avulso.all():
            turmasdisciplinas.append(tdisc)

    context = {
        'turmasdisciplinas': turmasdisciplinas,
        'aluno':aluno,
        'semestre':semestre,
        'ano_lectivo':ano_lectivo,
    }

    return render(request, 'horarios/finalizar.html', context)


#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################


@login_required
def report_view(request):

    info = {}
    for curso in Curso.objects.all():
        info[curso.sigla]={}
        turmas = Turma.objects.filter(curso=curso, semestre=semestre).order_by('ano','nome')
        for turma in turmas:
            info[curso.sigla][turma.nome] = {}
            alunos = set()

            turmadisciplinas = TurmaDisciplina.objects.filter(turma=turma, disciplina__semestre=semestre)

            for turmadisciplina in turmadisciplinas:
                for aluno in turmadisciplina.alunos.all():
                    if turmadisciplina.disciplina.nome not in lista_disciplinas_recuperacao:
                        alunos.add(aluno)


            info[curso.sigla][turma.nome]['alunos'] = sorted(list(alunos), key=lambda a:a.user.username)

            info[curso.sigla][turma.nome]['alunos_out'] = {aluno:[] for aluno in list(alunos)}
            for aluno in info[curso.sigla][turma.nome]['alunos']:
                for turmadisciplina in turmadisciplinas:
                    if turmadisciplina.disciplina.nome in lista_disciplinas_recuperacao:
                        continue
                    if aluno not in turmadisciplina.alunos.all() and aluno not in turmadisciplina.alunos_avulso.all():
                        info[curso.sigla][turma.nome]['alunos_out'][aluno].append(turmadisciplina.disciplina)

            info[curso.sigla][turma.nome]['alunos_avulso'] = {}
            disciplinas = {}
            for turmadisciplina in turmadisciplinas:
                if turmadisciplina.disciplina.nome in lista_disciplinas_recuperacao:
                    continue

                alunos = []
                for aluno in turmadisciplina.alunos_avulso.all():
                    alunos.append(aluno)
                disciplinas[turmadisciplina.disciplina] = sorted(alunos, key=lambda a:a.user.username)

        # disciplinas de recuperação
            disciplinas = {}
            for disciplina in lista_disciplinas_recuperacao:
                for turmadisciplina in TurmaDisciplina.objects.filter(disciplina__nome=disciplina):
                    if disciplina in disciplinas:
                        disciplinas[disciplina] += [aluno for aluno in turmadisciplina.alunos.all()] + [aluno for aluno in turmadisciplina.alunos_avulso.all()]
                    else:
                        disciplinas[disciplina] = [aluno for aluno in turmadisciplina.alunos.all()] + [aluno for aluno in turmadisciplina.alunos_avulso.all()]
                disciplinas[disciplina].sort(key=lambda a:a.user.username)

            info[curso.sigla]['D01EINF01']['alunos_avulso'] = disciplinas


    context = {
        'info': info,
        'semestre':semestre,
    }

    return render(request, 'horarios/report.html', context)



@login_required
def report_alunos_view(request):

    info = {}
    for aluno in Aluno.objects.all():
        info[aluno.nome_completo]=[]
        for turmadisciplina in TurmaDisciplina.objects.all():
            if aluno in turmadisciplina.alunos.all():
                info[aluno.nome_completo].append(turmadisciplina.turma.nome)
    context = {
        'info': info,
    }

    return render(request, 'horarios/report_alunos.html', context)


def email_view(request):

    email = request.POST.get('email')

    user = User.objects.filter(email=email).first()
    token = token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))
    reset_link = request.build_absolute_uri(f'/reset/{uidb64}/{token}/')

    turmasdisciplinas = ''
    for tdisc in TurmaDisciplina.objects.filter(turma__curso=aluno.curso):
        if aluno in tdisc.alunos.all() or aluno in tdisc.alunos_avulso.all():
            turmasdisciplinas += f'\n {tdisc.disciplina}, {tdisc.turma}'

    send_mail(
        f'Inscrição no {semestre}º semestre de {aluno.curso}',
        f'Olá,\nNo {semestre}º semestre de {ano_lectivo} inscreveu-se, em {aluno.curso}, às seguintes cadeiras e respetivas turmas:{turmasdisciplinas}',
        'lucio.studer@gmail.com',
        [email]
    )

    return redirect('horario:finalizar')



def report_alunos_nao_escolheram_turma_view(request):
    alunos_None = Aluno.objects.filter(turma=None)
    alunos_0 = Aluno.objects.filter(turma__exact='')

    context = {
        'alunos': alunos_None | alunos_0,
    }
    return render(request, 'horarios/report_alunos_sem_turma.html', context)



#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
#############################################################################################################################


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(
                request,
                'horarios/login.html',
                {'message': 'Preencha todos os campos'}
            )


        user = authenticate(
            request,
            username=username.strip('a') if username != 'admin' else username,
            password=password
        )


        print("user", user, "authenticade")

        if user is not None:
            print("user is not None. User is:", user, "username", username, "password", password)
            login(request, user)

            if request.user.is_authenticated:
                # O user está logado
                print("User logado:", request.user)
            else:
                # O user NÃO está logado
                print("User anónimo")

            return redirect('horarios:horarios')

        return render(
            request,
            'horarios/login.html',
            {'message': 'Username ou palavra-passe incorretos'}
        )

    if request.user.is_authenticated:
        return redirect('horarios:horarios')

    return render(request, 'horarios/login.html')



def __login_view(request):

    print("LOGIN")
    if request.method == 'POST':

        username = request.POST['username'].strip()
        password = request.POST['password'].strip()

        print(username,password)

        u = User.objects.get(username=username)
        email = u.email
        print("user:",  u, ", Email:", email)

        user = authenticate(request, email=email, password=password)
        print("user: ", user)

        if user is not None:
            print("user is not None", user)
            login(request, user)
            return redirect('horarios:horarios')

        return render(request, 'horarios/login.html', {
            'message': 'Credenciais inválidas'
        })

    if request.user.is_authenticated:
        return redirect('horarios:horarios')
    else:
        return render(request, 'horarios/login.html')



def logout_view(request):
    logout(request)
    return redirect('horarios:horarios')


def forgot_password(request):

  if request.method != 'POST':
    return render(request, 'horarios/forgot.html')

  username = request.POST.get('username')

  if not username:
    return render(
        request,
        'horarios/forgot.html',
        {'error': 'Por favor, insira o seu número de aluno'}
    )

  user = User.objects.filter( username=username.strip().strip('a')).first()

  if not user:
    return render(
        request,
        'horarios/forgot.html',
        {'error': 'Não existe registo de aluno de LEI com esse número. contacte lucio.studer@ulusofona.pt'}
    )

  token = token = default_token_generator.make_token(user)
  uidb64 = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))

  reset_link = request.build_absolute_uri(f'/reset/{uidb64}/{token}/')

  send_mail('Horários LEI: Definição de palavra chave',
        f'Olá,\n\nPediu para redefinir a sua palavra chave, clique por favor no seguinte link:\n\n{reset_link}',
        'horarios.deisi@gmail.com',
        [user.email.strip()]
  )

  return render(request, 'horarios/forgot.html', {'success': f'Foi enviado um email para <b style="font-weight:bold;">{user.email}</b> com um link para redefinir a sua senha.'})



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