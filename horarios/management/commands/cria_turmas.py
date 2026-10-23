import requests
from django.core.management.base import BaseCommand
from horarios.models import *

class Command(BaseCommand):
    help = 'Fetch Disciplina data from JSON API and load into Disciplina model'

    def add_arguments(self, parser):
        parser.add_argument('curso_sigla', type=str, help='The sigla of the Curso to associate with the Disciplinas')
        parser.add_argument('curso_prefixo', type=str, help='The prefix of curso')
        parser.add_argument('ano', type=int, help='The year the Curso')
        parser.add_argument('semestre', type=int, help='The semester the Curso')
        parser.add_argument('turmas_dia', type=int, help='The number of turmas de dia of the Curso')
        parser.add_argument('turmas_noite', type=int, help='The number of turmas de noite of the Curso')
        parser.add_argument('lotacao', type=int, help='The maximum number of students per class')
        parser.add_argument('lotacao_avulso', type=int, help='The maximum number of students from other years')

    def handle(self, *args, **kwargs):
        curso_sigla = kwargs['curso_sigla']
        curso_prefixo = kwargs['curso_prefixo']
        ano = kwargs['ano']
        semestre = kwargs['semestre']
        turmas_dia = kwargs['turmas_dia']
        turmas_noite = kwargs['turmas_noite']
        lotacao = kwargs['lotacao']
        lotacao_avulso = kwargs['lotacao_avulso']


        curso = Curso.objects.get(sigla=curso_sigla)

       # Turma.objects.filter(curso=curso, ano=ano).delete()


        for t in range(1, turmas_dia+1):
            nome = f'D0{ano}{curso_prefixo}0{t}'

            turma = Turma.objects.create(
                nome=nome,
                curso=curso,
                ano=ano,
                semestre=semestre,
                lotacao=lotacao,
                lotacao_avulso=lotacao_avulso,
                )

            for disciplina in Disciplina.objects.filter(curso=curso, ano=ano):
                TurmaDisciplina.objects.create(
                    turma=turma,
                    disciplina=disciplina,
                    )

        for t in range(1, turmas_noite+1):
            nome = f'N0{ano}{curso_prefixo}0{t}'

            turma = Turma.objects.create(
                nome=nome,
                curso=curso,
                ano=ano,
                semestre=semestre,
                lotacao=17,
                lotacao_avulso=3,
                )

            for disciplina in Disciplina.objects.filter(curso=curso, ano=ano):
                TurmaDisciplina.objects.create(
                    turma=turma,
                    disciplina=disciplina,
                    )
