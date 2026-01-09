# Atualizar semestre

Atualizar em `views.py`:

```python
inscricoes_abertas = True
semestre = 2
ano_lectivo = '23-24'
lista_disciplinas_recuperacao = ['Matemática I (2º Sem)', 'Fund Programação (2º Sem)', 'Fundamentos de Física (2º Sem)']
```

# Comandos para carregar dados


### carregar cursos

`python manage.py carrega_cursos`
* this command loads into the database all courses available in URL
* URL: https://dsdeisi.pythonanywhere.com/cursos-json


### carregar disciplinas do curso

`python manage.py carrega_disciplinas_curso <course sigla> <ano letivo>`
* this command loads into the database all courses available in URL
* URL: https://dsdeisi.pythonanywhere.com/disciplinas-curso-json/LEI/23-24
* exemplo: `python manage.py carrega_disciplinas_curso LEI 25-26`


### criar turmas dos anos do curso

1. comando: `python manage.py cria_turmas <sigla curso> <prefixo do curso> <ano> <turmasdia> <turmas noite> <lotacao> <lotacao_avulso>`
    * this command creates turmas of a course and year
    * exemplo: `python manage.py cria_turmas LEI EINF 3 3 1 15 3`

### carregar de ficheiro JSON alunos do curso

1. criar ficheiro JSON com os alunos, segundo a sintaxe: 

```json
[
  {
    "firstname": "Niclénio",
    "lastname": "dos Santos",
    "idnumber": 22210307,
    "email": "niclesantos78@gmail.com"
  },{
    ...
  }
]
```

2. colocar ficheiro em `\horarios\management\commands\data`
3. executar comando: `python manage.py carrega_alunos <course sigla> <json file with alunos>`
    * this command loads into the database all students of course contained in a file in the commands\data folder
    * exemplo: `python manage.py carrega_alunos LEI alunos.json`

### carregar de ficheiro TXT alunos do curso

1. criar ficheiro TXT com os alunos segundo a sintaxe: `<numero>\t<nome>\t<email>`
2. colocar ficheiro em `\horarios\management\commands\data`
3. executar comando: `python manage.py carrega_alunos <course sigla> <txt file with alunos>`
    * this command loads into the database all students of course contained in a file in the commands\data folder
    * exemplo: `python manage.py carrega_alunos LEI alunos.json`

