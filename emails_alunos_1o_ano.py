from horarios.models import *

alunos = []

for turma in TurmaDisciplina.objects.all():
    # if turma.disciplina.ano == 1:
        for a in turma.alunos.all():
            alunos.append(a.user.email)

print(*list(set(alunos)), sep="\n")