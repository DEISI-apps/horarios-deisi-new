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
    filter_horizontal = ('alunos', 'alunos_avulso')
    list_display = ('disciplina', 'turma', 'inscritos', 'inscritos_avulso')
    ordering = ('disciplina', 'turma')
    list_filter = ('disciplina__semestre', 'turma__ano',)
    search_fields = ['disciplina__nome', 'turma__nome', ]

admin.site.register(TurmaDisciplina, TurmaDisciplinaAdmin)



class AlunoAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

admin.site.register(Aluno, AlunoAdmin)
