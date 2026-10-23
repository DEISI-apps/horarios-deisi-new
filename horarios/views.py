from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import get_connection


from django.core.mail import send_mail

from .models import *
from .forms import *

import json, random, string
import base64

from django.contrib.auth.decorators import user_passes_test

def is_sata(user):
    return user.groups.filter(name="sata").exists()



from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required, user_passes_test

SEMESTRE_ATUAL = '1'

inscricoes_abertas = True
semestre = 1
ano_lectivo = '26-27'
lista_disciplinas_recuperacao = [] # ['Matemática I (2º Sem)', 'Fund Programação (2º Sem)', 'Fundamentos de Física (2º Sem)']



# Lista de templates
email_templates = [
    {
        "subject": "Acesso aos horários LEI",
        "body": "Olá,\n\nRecebemos um pedido para atualizar a sua palavra‑chave.\nPara continuar, utilize o link abaixo:\n\n{{reset_link}}\n\nSe não fez este pedido, pode ignorar esta mensagem."
    },
    {
        "subject": "Reposição de palavra‑chave – horarios LEI",
        "body": "Olá,\n\nPara redefinir a sua palavra‑chave de acesso aos horários LEI, siga este link:\n\n{{reset_link}}\n\nEste link é válido por tempo limitado."
    },
    {
        "subject": "Confirmação de pedido de acesso",
        "body": "Viva,\n\nFoi solicitado um novo acesso à plataforma de horários LEI.\nPode concluí‑lo aqui:\n\n{{reset_link}}"
    },
    {
        "subject": "Atualização de credenciais – LEI",
        "body": "Olá,\n\nPara atualizar a sua palavra‑chave e continuar a usar a plataforma, clique no link seguinte:\n\n{{reset_link}}"
    },
    {
        "subject": "Pedido de redefinição confirmado",
        "body": "Olá,\n\nO seu pedido foi registado com sucesso.\nUtilize o link abaixo para definir uma nova palavra‑chave:\n\n{{reset_link}}"
    },
    {
        "subject": "Ação necessária: acesso App Horarios",
        "body": "Olá,\n\nPara concluir o processo de acesso aos horários LEI, siga este endereço:\n\n{{reset_link}}\n\nObrigado."
    },
    {
        "subject": "Novo acesso à plataforma LEI",
        "body": "Viva,\n\nEstá quase tudo pronto.\nBasta clicar no link abaixo para concluir a redefinição da palavra‑chave:\n\n{{reset_link}}"
    },
    {
        "subject": "Segurança da conta – LEI",
        "body": "Olá,\n\nPor motivos de segurança, a redefinição da palavra‑chave é feita através deste link:\n\n{{reset_link}}"
    },
    {
        "subject": "Definir nova palavra‑chave",
        "body": "Olá,\n\nPara definir uma nova palavra‑chave de acesso, utilize o link seguinte:\n\n{{reset_link}}\n\nCaso não tenha feito este pedido, ignore este email."
    },
    {
        "subject": "Continuação do pedido de acesso",
        "body": "Olá,\n\nPode continuar o processo de acesso à plataforma através do link abaixo:\n\n{{reset_link}}"
    }
]



# Create your views here.

def index_view(request):
    return render(request, 'horarios/index.html')


def horarios_view(request):

    horarios = Horario.objects.filter(curso__sigla='LEI', ano_lectivo=ano_lectivo, semestre=semestre)
    context = {
        'horarios':horarios,
        'inscricoes_abertas': inscricoes_abertas,
        'semestre':semestre,
        'ano_lectivo':ano_lectivo
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
                if turmaDisciplina.turma == turma:

                    #and \
                    #turmaDisciplina.disciplina.nome != "Fund Programação 2º Sem" and \
                    #turmaDisciplina.disciplina.nome != "Matemática I" and \
                    #turmaDisciplina.disciplina.nome != "Fundamentos de Física":

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

##############################################
##############################################
##############################################

@user_passes_test(is_sata)
def lista_disciplinas_view(request):

    disciplinas = Disciplina.objects.filter(semestre=semestre, curso__nome='LEI')

    disciplinas0 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=0)
    disciplinas1 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=1)
    disciplinas2 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=2)
    disciplinas3 = Disciplina.objects.filter(semestre=semestre, curso__sigla='LEI', ano=3)

    context = {'disciplinas': [
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas0],
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas1],
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas2],
            [(d, sum([len(t.alunos.all())+len(t.alunos_avulso.all())  for t in TurmaDisciplina.objects.filter(disciplina=d)]))  for d in disciplinas3],
        ]}

    return render(request, 'horarios/lista_disciplinas.html', context)

@user_passes_test(is_sata)
def lista_turmas_de_disciplina_view(request, disciplina_id):

    disciplina = Disciplina.objects.get(id=disciplina_id)
    turmasdisciplina = TurmaDisciplina.objects.filter(disciplina=disciplina)

    turmasdisciplina = [(t, len(t.alunos.all()) + len(t.alunos_avulso.all()))for t in turmasdisciplina]

    context = {

        'disciplina': disciplina,
        'turmasdisciplina': turmasdisciplina,
    }
    return render(request, 'horarios/lista_turmas_disciplina.html', context)


@user_passes_test(is_sata)
def lista_alunos_turma_view(request, turmadisciplina_id):
    turmadisciplina = TurmaDisciplina.objects.get(id=turmadisciplina_id)

    context = {
        'turmadisciplina': turmadisciplina,
        'alunos': turmadisciplina.alunos.all().order_by('user__first_name', 'user__last_name'),
        'alunos_avulso': turmadisciplina.alunos_avulso.all().order_by('user__first_name', 'user__last_name')
    }
    return render(request, 'horarios/lista_alunos_turmas_disciplina.html', context)


##############################################
##############################################
##############################################


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
@user_passes_test(is_sata)
def report_view(request):

    info = {}

    # Prefetch de TurmaDisciplina (via turma e disciplina)
    turmadisciplina_prefetch = Prefetch(
        'turmasdisciplinas',
        queryset=TurmaDisciplina.objects.select_related('disciplina').prefetch_related('alunos', 'alunos_avulso').filter(
            turma__semestre=SEMESTRE_ATUAL,
            disciplina__semestre=SEMESTRE_ATUAL
        )
    )

    # Turmas
    cursos = Curso.objects.prefetch_related(
        Prefetch(
            'turmas',
            queryset=Turma.objects.filter(semestre=SEMESTRE_ATUAL).prefetch_related(turmadisciplina_prefetch)
        )
    )

    cursos = Curso.objects.prefetch_related(
        Prefetch(
            'turmas',
            queryset=Turma.objects
                .filter(semestre=SEMESTRE_ATUAL)
                .order_by('ano', 'nome')
                .prefetch_related(turmadisciplina_prefetch)
        )
    )

    # Disciplinas de recuperação
    turmadisciplinas_recuperacao = TurmaDisciplina.objects.filter(
        disciplina__nome__in=lista_disciplinas_recuperacao,
        turma__semestre=SEMESTRE_ATUAL,
        disciplina__semestre=SEMESTRE_ATUAL
    ).prefetch_related('alunos', 'alunos_avulso', 'turma')

    # Map disciplina de recuperação -> lista de alunos
    disciplinas_recuperacao_map = {}
    for td in turmadisciplinas_recuperacao:
        nome = td.disciplina.nome
        if nome not in disciplinas_recuperacao_map:
            disciplinas_recuperacao_map[nome] = []
        disciplinas_recuperacao_map[nome] += list(td.alunos.all()) + list(td.alunos_avulso.all())

    # Ordenar alunos
    for nome, alunos_list in disciplinas_recuperacao_map.items():
        disciplinas_recuperacao_map[nome] = sorted(alunos_list, key=lambda a: a.user.username)

    # Construir info
    for curso in cursos:
        info[curso.sigla] = {}

        for turma in curso.turmas.all():
            info[curso.sigla][(turma.nome, turma.ano)] = {}

            # Alunos regulares (excluindo disciplinas de recuperação)
            alunos_set = set()
            for td in turma.turmasdisciplinas.all():
                if td.disciplina.nome not in lista_disciplinas_recuperacao:
                    alunos_set.update(td.alunos.all())

            alunos_list = sorted(list(alunos_set), key=lambda a: a.user.username)
            info[curso.sigla][(turma.nome, turma.ano)]['alunos'] = alunos_list

            # Alunos fora (faltas em disciplinas regulares)
            alunos_out = {aluno: [] for aluno in alunos_list}
            for aluno in alunos_list:
                for td in turma.turmasdisciplinas.all():
                    if td.disciplina.nome in lista_disciplinas_recuperacao:
                        continue
                    if aluno not in td.alunos.all() and aluno not in td.alunos_avulso.all():
                        alunos_out[aluno].append(td.disciplina)
            info[curso.sigla][(turma.nome, turma.ano)]['alunos_out'] = alunos_out

            # Alunos avulso por disciplina (não recuperação)
            disciplinas_avulso = {}
            for td in turma.turmasdisciplinas.all():
                if td.disciplina.nome in lista_disciplinas_recuperacao:
                    continue
                disciplinas_avulso[td.disciplina] = sorted(list(td.alunos_avulso.all()), key=lambda a: a.user.username)
            info[curso.sigla][(turma.nome, turma.ano)]['alunos_avulso'] = disciplinas_avulso


            # Alunos inscritos em todas as disciplinas regulares da turma
            disciplinas_regulares = [
                td for td in turma.turmasdisciplinas.all()
                if td.disciplina.nome not in lista_disciplinas_recuperacao
            ]

            if disciplinas_regulares:
                # Começa com o conjunto de alunos da primeira disciplina
                alunos_todas = set(disciplinas_regulares[0].alunos.all())
                # Intersecta com os conjuntos de alunos das outras disciplinas
                for td in disciplinas_regulares[1:]:
                    alunos_todas.intersection_update(td.alunos.all())
                info[curso.sigla][(turma.nome, turma.ano)]['alunos_todas'] = sorted(list(alunos_todas), key=lambda a: a.user.username)
            else:
                info[curso.sigla][(turma.nome, turma.ano)]['alunos_todas'] = []


        # Adicionar disciplinas de recuperação à turma fixa D01EINF01
        if 'D01EINF01' in info[curso.sigla]:
            info[curso.sigla]['D01EINF01']['alunos_avulso'] = disciplinas_recuperacao_map

    context = {
        'info': info,
        'semestre': SEMESTRE_ATUAL,
    }

    return render(request, 'horarios/report.html', context)




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


from django.db.models import Prefetch
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.shortcuts import render, redirect

SEMESTRE_ATUAL = '1'  # 1º semestre

@login_required
@user_passes_test(is_sata)
def report_alunos_view(request):
    info = {}

    # Prefetch de TurmaDisciplina e alunos para evitar N+1
    turmadisciplina_prefetch = Prefetch(
        'turmasdisciplinas',
        queryset=TurmaDisciplina.objects.prefetch_related('alunos', 'alunos_avulso').filter(
            turma__semestre=SEMESTRE_ATUAL,
            disciplina__semestre=SEMESTRE_ATUAL
        )
    )

    # Prefetch das turmas e disciplinas de cada curso
    alunos = Aluno.objects.prefetch_related(
        Prefetch('curso__turmas', queryset=Turma.objects.prefetch_related(turmadisciplina_prefetch))
    )

    n_alunos_inscritos = 0
    for aluno in alunos:
        info[(aluno.nome_completo, aluno.user.username)] = []
        # Percorrer apenas turmas do semestre 2 do curso do aluno
        for turma in aluno.curso.turmas.all():
            for td in turma.turmasdisciplinas.all():
                if aluno in td.alunos.all() or aluno in td.alunos_avulso.all():
                    info[(aluno.nome_completo, aluno.user.username)].append((td.disciplina, td.turma))
        info[(aluno.nome_completo, aluno.user.username)].sort(key=lambda e: (e[0].ano,e[0].nome))

        n_alunos_inscritos += 1 if len(info[(aluno.nome_completo, aluno.user.username)]) > 0 else 0

    context = {'info': info, 'n_alunos_inscritos': n_alunos_inscritos, 'n_alunos_faltam': len(alunos) - n_alunos_inscritos}
    return render(request, 'horarios/report_alunos.html', context)


import csv


siglas = """1,Matemática I
11047,Interação Humano-Máquina
12900,Sistemas de Informação nas Organizações (ramo: SI)
13318,Técnicas de Data Warehouse
13319,Complementos Engenharia de Software
13398,Arquitetura Avançada de Computadores
13558,Algoritmia e Estrutura de Dados
13763,Metodologias de Investigação e inovação
13766,OPÇÃO->Sistemas Sem Fios Cooperativos
15412,Seminário de Orientação
15430,Data Minning
1656,Matemática Discreta
16927,Projeto de Telecomunicações
1792,Bases de Dados
1796,Contabilidade
19082,Desenvolvimento Responsável de Software Suportado por IA Generativa
2129,Opção III - Intel Artificial
21942,OPÇÃO->Cibersegurança
22513,Data Science
23041,Direito Informático
23084,Fundamentos de Ciência de Dados
23265,Introdução à Ciências de Dados
23869,Ciência de Dados
24297,Tópicos em Aprendizagem Automatizada e suas Aplicações
24446,Fundamentos de Engenharia de Dados
24449,Visão Computacional
24450,Aprendizagem Automatizada II
24452,Introdução à Inteligência Artificial
24454,"Introdução à Privacidade, Segurança e Ética"
24454,"Introdução à Privacidade, Segurança e Ética (Op II)"
24496,Introdução à Matemática das Probabilidades
24497,Fundamentos de Engenharia de Dados p/ CD
24498,Introdução às Equações Diferenciais Ordinárias
25060,Técnicas de Programação Segura
25061,Desenvolvimento e operacionalização de aplicações
25069,Administração de Redes e Infraestrutura de IT
25228,"Privacidade, Segurança e Ética em Ciência de Dados"
25229,Fundamentos de Estatística para Ciências de Dados
25230,Programação Aplicada para Ciências de Dados
25232,Visualização de Informação Avançada
25233,Fundamentos de Sistemas de Recomendação
25626,OPÇÃO->Inteligência Artificial Integrada
25627,OPÇÃO->Sistemas Baseados em Posicionamento
25628,OPÇÃO->Eng. Software e Ciência de Dados
25632,OPÇÃO-> Aprendizagem Automatizada Avançada
25632,OPÇÃO->Introdução a Ciência das Rede
26020,Fundamentos de Processos de Mineração
26022,Fundamentos de processamento de Linguagem Natural
26110,Gestão de Processos de Negócio
26141,Desenvolvimento Interfaces Web
26190,Programação Low-Code e No-Code
27242,Tópicos Avançados em Redes Neuronais ou Princípios de IA e Aprendizagem Automatizada (Op 1)
27247,Programação para IA ou Geração de Linguagem Natural (Op 3)
339,Introdução às Ciências da Computação
5140,Trabalho Final de Curso
620,Probabilidades e Estatistica
6305,Sistemas Operativos
7,Sistemas Digitais
7334,Metodologias de Investigação Científica
7334,Metodologias de Investigação Científica (Op II)
7336,Fundamentos de Física
7337,Fundamentos de Programação
7339,Sinais e Sistemas
7340,Instrumentos de Gestão
7341,Engenharia de Software
7348,Computação Distribuída
7349,Complementos de Redes
7432,Teoria e Prática de Marketing
7434,Motivação e Liderança
7435,Sistemas Móveis Empresariais
7628,Seminário de Projecto
7646,Fundamentos de Telecomunicações
8334,Fundamentos de Sistemas de Informação
8341,Gestão de Sistemas e Tecnologias de Informação
8448,Base de Dados
8850,Marketing em Tecnologias da Informação
8856,Tecnologias e Planeamento de Segurança
898,Linguagens de Programação II"""


s = { i.split(",")[1]: i.split(",")[0] for i in siglas.split('\n') }





@login_required
@user_passes_test(is_sata)
def report_alunos_csv_view(request):
    info = {}

    # Prefetch de TurmaDisciplina e alunos para evitar N+1
    turmadisciplina_prefetch = Prefetch(
        'turmasdisciplinas',
        queryset=TurmaDisciplina.objects.prefetch_related('alunos', 'alunos_avulso').filter(
            turma__semestre=SEMESTRE_ATUAL,
            disciplina__semestre=SEMESTRE_ATUAL
        )
    )

    # Prefetch das turmas e disciplinas de cada curso
    alunos = Aluno.objects.prefetch_related(
        Prefetch('curso__turmas', queryset=Turma.objects.prefetch_related(turmadisciplina_prefetch))
    )

    n_alunos_inscritos = 0
    for aluno in alunos:
        info[(aluno.nome_completo, aluno.user.username)] = []
        # Percorrer apenas turmas do semestre 2 do curso do aluno
        for turma in aluno.curso.turmas.all():
            for td in turma.turmasdisciplinas.all():
                if aluno in td.alunos.all() or aluno in td.alunos_avulso.all():
                    info[(aluno.nome_completo, aluno.user.username)].append((td.disciplina, td.disciplina.id_dsdeisi, td.turma))
        info[(aluno.nome_completo, aluno.user.username)].sort(key=lambda e: (e[0].ano,e[0].nome))

        n_alunos_inscritos += 1 if len(info[(aluno.nome_completo, aluno.user.username)]) > 0 else 0



    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="alunos-turmas.csv"'

    writer = csv.writer(response)

    writer.writerow(["nome", "numero", "disciplina", "id disciplina", "turma"])


    for aluno, data in info.items():

        for disciplina, id, turma in data:

            writer.writerow([
                aluno[0],
                aluno[1],
                disciplina,
                s[disciplina.nome],
                turma,
        ])

    return response




@login_required
@user_passes_test(is_sata)
def report_alunos_numeros_view(request):


    alunos = Aluno.objects.select_related("user")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="alunos-numeros.csv"'

    writer = csv.writer(response)

    writer.writerow(["numero", "nome"])


    for aluno in alunos:

            writer.writerow([
                aluno.user.username,
                aluno.user,
        ])

    return response


@login_required
def email_view(request):
    email = request.POST.get('email')
    user = User.objects.filter(email=email).first()
    if not user:
        # trata caso de email não encontrado
        return redirect('horario:finalizar')

    aluno = user.aluno  # relação OneToOne
    token = defau





@user_passes_test(is_sata)
def report_alunos_nao_escolheram_turma_view(request):
    alunos_None = Aluno.objects.filter(turma=None)
    alunos_0 = Aluno.objects.filter(turma__exact='')

    alunos = alunos_None | alunos_0

    alunos = [aluno for aluno in alunos if aluno.user.username[0] != 'p' and aluno.user.username[0] != 'f']

    context = {
        'alunos': alunos,
    }



    return render(request, 'horarios/report_alunos_sem_turma.html', context)




#############################################################################################################################
###  ENDPOINTS ##############################################################################################################
#############################################################################################################################

def turma_alunos_view(request, disciplina_id_dsdeisi, turma_nome):
    data = {
            'id_dsdeisi': disciplina_id_dsdeisi,
            'turma_nome': turma_nome,
    }

    try:
        turma = TurmaDisciplina.objects.get(
                disciplina__id_dsdeisi=disciplina_id_dsdeisi,
                turma__nome =turma_nome
            )

        data |= {
            'disciplina': turma.disciplina.nome,
            'turma': turma.turma.nome,
        }

        serialized_alunos = [{'nome': str(a), 'numero': a.user.username, 'email': a.user.email } for a in turma.alunos.all()]

        data |= {
            'alunos': serialized_alunos,
        }

        serialized_alunos_avulso = [{'nome': str(a), 'numero': a.user.username, 'email': a.user.email }for a in turma.alunos_avulso.all()]

        data |= {
            'alunos_avulso': serialized_alunos_avulso,
        }

        return JsonResponse(data, status=200)
    except:

        data['erro'] = "erro!!"

        return JsonResponse(data, status=404)



from urllib.parse import unquote

def aluno_turmas_view(request, numeroAluno):

    data = {'numeroAluno': numeroAluno}

    try:
        aluno = Aluno.objects.get(user__username=numeroAluno.strip().lower())
        data |= {
            'aluno': str(aluno),
            'numero': str(aluno.user.username),
        }


        turmas  = []
        for turmasdisciplina in aluno.turmasdisciplinas.all():
            turmas.append({
                'disciplina': str(turmasdisciplina.disciplina),
                'id_dsdeisi': str(turmasdisciplina.disciplina.id_dsdeisi),
                'turma': str(turmasdisciplina.turma)
            })

        for turmasdisciplina in aluno.turmasdisciplinas_avulso.all():
            turmas.append({
                'disciplina': str(turmasdisciplina.disciplina),
                'id_dsdeisi': str(turmasdisciplina.disciplina.id_dsdeisi),
                'turma': str(turmasdisciplina.turma)
            })

        data['turmas'] = turmas

        return JsonResponse(data, status=200)

    except Aluno.DoesNotExist:
        return JsonResponse({'erro': 'Aluno não encontrado'}, status=404)


def aluno_numero_view(request, emailAluno):

    try:
        aluno = Aluno.objects.get(user__email=emailAluno)
        data = {
            'aluno': str(aluno),
            'numero': str(aluno.user.username),
        }

        return JsonResponse(data, status=200)

    except Aluno.DoesNotExist:
        return JsonResponse({'erro': 'Aluno não encontrado'}, status=404)


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


      #  inscricoes fechadas nao faz login
      #  if not inscricoes_abertas  and username[0] == 'a':
      #      return redirect('horarios:horarios')

        user = authenticate(
            request,
            username=username if username != 'admin' else username,
            password=password
        )

        print("user", username, password, user)

        if user is not None:
            login(request, user)
            return redirect('horarios:horarios')

        return render(
            request,
            'horarios/login.html',
            {'message': 'Username ou palavra-passe incorretos'}
        )

    if request.user.is_authenticated:
        return redirect('horarios:horarios')

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

  user = User.objects.filter( username=username.strip()).first()

  if not user:
    return render(
        request,
        'horarios/forgot.html',
        {'error': 'Não existe registo de aluno de LEI com esse número. contacte lucio.studer@ulusofona.pt'}
    )

  token = token = default_token_generator.make_token(user)
  uidb64 = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))

  reset_link = request.build_absolute_uri(f'/reset/{uidb64}/{token}/')


  template = random.choice(email_templates)
  subject = template["subject"]
  body = template["body"].replace("{{reset_link}}", reset_link)

    # Enviar email
  with get_connection() as connection:
    send_mail(
        subject,
        body,
        'pweb.profs@gmail.com',          # 'deisi.horarios@gmail.com',
        [user.email.strip()],
        connection=connection,
        fail_silently=False,
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