from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Curso)


class HorarioAdmin(admin.ModelAdmin):
    ordering = ('curso', 'ano_lectivo', 'ano', 'semestre')

admin.site.register(Horario, HorarioAdmin)

class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('curso', 'nome', 'ano', 'semestre')
    ordering = ('curso', 'ano', 'semestre', 'nome')

admin.site.register(Disciplina, DisciplinaAdmin)


class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'curso', 'ano', 'lotacao', 'lotacao_avulso')
    list_editable = ['lotacao', 'lotacao_avulso']
admin.site.register(Turma, TurmaAdmin)



class TurmaDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'turma', 'inscritos', 'inscritos_avulso')
    ordering = ('disciplina', 'turma')

admin.site.register(TurmaDisciplina, TurmaDisciplinaAdmin)


admin.site.register(Aluno)
