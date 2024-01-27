import requests
from django.core.management.base import BaseCommand
from horarios.models import Curso, Disciplina

class Command(BaseCommand):
    help = 'Fetch Disciplina data from JSON API and load into Disciplina model'

    def add_arguments(self, parser):
        parser.add_argument('curso_sigla', type=str, help='The sigla of the Curso to associate with the Disciplinas')

    def handle(self, *args, **kwargs):
        curso_sigla = kwargs['curso_sigla']

        api_url = f'https://dsdeisi.pythonanywhere.com/disciplinas-curso-json/{curso_sigla}/23-24'

        try:
            # Make a GET request to the API
            response = requests.get(api_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON data from the response
                api_data = response.json()

                # Get the Curso object for the specified sigla
                curso_obj = Curso.objects.get(sigla=curso_sigla)

                # Clear existing Disciplina objects for the specific curso
                Disciplina.objects.filter(curso=curso_obj).delete()

                # Create Disciplina objects from the API data
                for disciplina_data in api_data.get('disciplinas', []):
                    Disciplina.objects.create(
                        nome=disciplina_data['sigla'],
                        ano=disciplina_data['nome'],
                        semestre=disciplina_data['semestre'],
                        curso=curso_obj
                    )

                self.stdout.write(self.style.SUCCESS(f'Disciplina data for {curso_sigla} loaded successfully'))

            else:
                # Handle the case where the API request was not successful
                self.stdout.write(self.style.ERROR(f"API request failed with status code: {response.status_code}"))

        except Exception as e:
            # Handle any exceptions that might occur during the request
            self.stdout.write(self.style.ERROR(f"Error during API request: {str(e)}"))
