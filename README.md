# Comandos


# carregar cursos

`python manage.py carrega_cursos`
* this command loads into the database all courses available in URL
* URL: https://dsdeisi.pythonanywhere.com/cursos-json


# carregar disciplinas do curso

`python manage.py carrega_disciplinas_curso <course sigla>`
* this command loads into the database all courses available in URL
* URL: https://dsdeisi.pythonanywhere.com/disciplinas-curso-json/LEI/23-24

# criar turmas dos anos do curso

`python manage.py cria_turmas <sigla curso> <prefixo do curso> <ano> <turmasdia> <turmas noite>`
* this ocmmand creates turmas of a course and year
* exemplo: python manage.py cria_turmas LEI EINF 3 3 1


# carregar alunos do curso

`python manage.py carrega_alunos <course sigla> <json file with alunos>`
* this command loads into the database all students of course contained in a fil in the commands\data folder
