from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Curso(models.Model):
    sigla = models.CharField(max_length=10, default='')
    nome = models.CharField(max_length=100)
    ciclo_estudos =  models.IntegerField(default=None)

    def __str__(self) -> str:
        return self.sigla


class Horario(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='horarios', default=None)
    ano_lectivo = models.CharField(max_length=100)
    ano = models.IntegerField(default=None)
    semestre = models.IntegerField(default=None)
    horario = models.FileField(upload_to='horarios/', blank=True, null=True)

    def __str__(self):
        return f"{self.curso.sigla} {self.ano_lectivo}  {self.ano}ºano  {self.semestre}sem"


class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='alunos', default=None)

    ANO_CHOICES = [(1,1), (2,2), (3,3)]
    ano = models.IntegerField(choices=ANO_CHOICES, null=True, default=None)
    turma = models.CharField(max_length=100, blank=True, null=True, default=None)

    @property
    def nome_completo(self):
        return self.user.first_name + ' ' + self.user.last_name

    def __str__(self):
        return self.nome_completo

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.IntegerField(null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='disciplinas', default=None) # devia ser M:M !!

    def __str__(self):
        return self.nome

    def inscrito(self, aluno):
        for td in TurmaDisciplina.objects.filter(disciplina=self):
            if aluno in td.alunos.all() or  aluno in td.alunos_avulso.all():
                return True
        return False

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='turmas', default=None)
    ano = models.IntegerField(null=True, blank=True)
    semestre =  models.CharField(max_length=100, default='2')
    lotacao = models.IntegerField(null=True, blank=True)
    lotacao_avulso = models.IntegerField(null=True, blank=True)

    @property
    def inscritos(self):
        l = [len(turma.alunos.all()) for turma in TurmaDisciplina.objects.filter(turma=self)]
        if len(l) > 0:
            return max(l)
        else:
            return 0

    def inscrito(self, aluno):
        for td in TurmaDisciplina.objects.filter(turma=self):
            if aluno in td.alunos.all():
                return True
        return False

    @property
    def inscritos_avulso(self):
        l = [len(turma.alunos_avulso.all()) for turma in TurmaDisciplina.objects.filter(turma=self)]
        if len(l) > 0:
            return max(l)
        else:
            return 0

    def __str__(self):
        return f"{self.nome}"


class TurmaDisciplina(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='turmasdisciplinas')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='turmasdisciplinas')
    alunos = models.ManyToManyField(Aluno, related_name='turmasdisciplinas', blank=True)
    alunos_avulso = models.ManyToManyField(Aluno, related_name='turmasdisciplinas_avulso', blank=True)

    @property
    def inscritos(self):
        return self.alunos.count()

    @property
    def inscritos_avulso(self):
        return self.alunos_avulso.count()

    def __str__(self):
        return f"{self.turma} - {self.disciplina}"







