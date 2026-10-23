alunos="""Arcanjo	Bondo Rescova	a22608615	arcanjo.b.p.rescova@gmail.com
Elias	Carvalho Tenente	a22506993	eliastenente05@gmail.com
Bruna	de Almeida	a22608639	brusantsz8217@gmail.com
Julia	Dos Santos	a22609509	juliapotris14@gmail.com
Simão	Jesus Lameira	a22609426	simaolameira08@gmail.com
João	Kalosa Pacheco	a22400467	kalosapacheco@gmail.com
Tomás	Lopes Henriques	a22609476	tplopeshenriques@gmail.com
Tiago	Martins Letras	a22609660	letrast8@gmail.com
Jorge	Olavo Gambôa	a22609683	jrg.miguel19@gmail.com
Valter	Pacheco	a22513255	isaadomii.9@gmail.com
Salumaria	Pinto Ferreira	a22609206	salumariaf@gmail.com
Geraldo	Púcuta Sambo	a22412320	geraldosambo4@gmail.com
Guilherme	Santos Paducho	a22608685	paduchoguilherme@gmail.com
Yanik	Silva Razak	a22609172	yaniksilvarazak@gmail.com
Martim	Sousa Charro	a22609494	martimcharro@icloud.com"""


from horarios.models import Curso, Turma, Disciplina, Aluno
from django.contrib.auth.models import User

alunos_bd = Aluno.objects.all().values_list("user__username", flat=True)


for aluno in alunos.splitlines():

    if aluno.split('\t')[2] in alunos_bd:
        continue


    first_name, last_name, username, email = aluno.split("\t")

    user, created = User.objects.get_or_create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password="ulu@26"
    )

    lei = Curso.objects.get(sigla="LEI")

    a = Aluno.objects.create(
        user=user,
        curso=lei,
    )

    print(a)
    print(user)
