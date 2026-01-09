import requests
from django.core.management.base import BaseCommand
from horarios.models import Curso, Turma, Disciplina, Aluno
from django.contrib.auth.models import User
import os, json

class Command(BaseCommand):
    help = 'Fetch Disciplina data from JSON API and load into Disciplina model'

    def add_arguments(self, parser):
        parser.add_argument('curso_sigla', type=str, help='The sigla of the Curso to associate with the Disciplinas')
        parser.add_argument('ficheiro', type=str, help='The json filename with students')

    def handle(self, *args, **kwargs):
        curso_sigla = kwargs['curso_sigla']
        ficheiro = kwargs['ficheiro']

        curso = Curso.objects.get(sigla=curso_sigla)

        with open(os.path.join('horarios', 'management', 'commands', 'data', ficheiro), encoding='utf-8') as f:
            dados = f.readlines()

        for a in Aluno.objects.all():
            if a.user.username != 'admin' or a.user.username[0] != 'f' or a.user.username[0] != 'p':
                a.user.delete()
                a.delete()


        for info in dados:

            username, name, email = info.split('\t')
            first_name = name.split()[0]
            last_name = ' '.join(name.split()[1:])

            user, created = User.objects.get_or_create(
                username = username,      
                email = email,
                first_name = first_name,
                last_name = last_name,
            )

            Aluno.objects.create(
                user=user,
                curso=curso,
            )
