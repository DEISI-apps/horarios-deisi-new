from horarios.models import *

for aluno in Aluno.objects.all():
#    if aluno.user.username[0] == 'a':
        aluno.user.set_password("ulu@26")
        aluno.user.save()
