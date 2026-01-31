from horarios.models import *
import json


with open("alunos.json", encoding="utf-8") as ficheiro:
    alunos_moodle = json.load(ficheiro)


for aluno in alunos_moodle:
    if not Aluno.objects.filter(user__username=aluno['numero']).exists():
        print(aluno['numero'])
