import requests
from django.core.management.base import BaseCommand
from horarios.models import *


class Command(BaseCommand):
    help = 'Fetch Curso data from JSON API and load into Curso model'

    def handle(self, *args, **kwargs):
        api_url = 'https://dsdeisi.pythonanywhere.com/cursos-json/'

        try:
            # Make a GET request to the API
            response = requests.get(api_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON data from the response
                api_data = response.json()

                # Clear existing Curso objects
                Curso.objects.all().delete()

                # Create Curso objects from the API data
                for curso_data in api_data.get('cursos', []):
                    Curso.objects.create(
                        sigla=curso_data['sigla'],
                        nome=curso_data['nome'],
                        ciclo_estudos=curso_data['ciclo']
                    )

                self.stdout.write(self.style.SUCCESS('Curso data loaded successfully'))

            else:
                # Handle the case where the API request was not successful
                self.stdout.write(self.style.ERROR(f"API request failed with status code: {response.status_code}"))

        except Exception as e:
            # Handle any exceptions that might occur during the request
            self.stdout.write(self.style.ERROR(f"Error during API request: {str(e)}"))
