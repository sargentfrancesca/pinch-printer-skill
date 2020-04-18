from mycroft import MycroftSkill, intent_file_handler
import requests
from urllib.parse import urlencode
from http import HTTPStatus
from bs4 import BeautifulSoup
import inquirer

URL = "pinchofnom.com"
PARAM = "s"

class PinchOfNomScraper(object):

    def __init__(self, query):
        self.query = query
        self.html = ''
        self.recipes = {}
        self.chosen_url = ''
        self.title = ''
        self.ingredients = {}
        self.steps = {}
    
    @property
    def url(self):
        query_dict = {PARAM:self.query}
        qs = urlencode(query_dict)
        return f"http://{URL}/?{qs}"

    def get_recipes(self):
        response = requests.get(self.url)
        if response.status_code == HTTPStatus.OK:
            return HTTPStatus.OK, response.content
        return HTTPStatus.BAD_REQUEST, ''
    
    def parse_recipes(self, html):
        body = BeautifulSoup(html, 'html.parser')
        thumnbails = body.select('div.pon-recipe-thumbnail')
        
        for thumb in thumnbails:
            url = thumb.find_all('a', href=True, limit=2)
            href = url[-1]['href']
            name = url[-1].string
            self.recipes[name] = href
        return self.recipes
    
    def choose_recipe(self):
        # questions = [
        # inquirer.List('recipe',
        #                 message="What recipe do you want?",
        #                 choices=[x for x in self.recipes],
        #             ),
        # ]
        # answers = inquirer.prompt(questions)
        # recipe_name = answers["recipe"]
        # self.chosen_url = self.recipes[recipe_name]
        a = [x for x in self.recipes][0]
        self.chosen_url = self.recipes[a]
        return self.chosen_url

    def get_recipe(self):
        response = requests.get(self.chosen_url)
        if response.status_code == HTTPStatus.OK:
            return HTTPStatus.OK, response.content
        return HTTPStatus.BAD_REQUEST, ''
    
    def parse_ingredients(self, body):
        ingredients_container = body.select('.wprm-recipe-ingredients-container')[0]
        ingredients_li = ingredients_container.find_all('li')

        ingredients = []
        for ingredient in ingredients_li:
            amount_string = ingredient.select('.wprm-recipe-ingredient-amount')

            if amount_string:
                amount = amount_string[0].string
            else:
                amount = ''
            
            unit_string = ingredient.select('.wprm-recipe-ingredient-unit')

            if unit_string:
                unit = unit_string[0].string
            else:
                unit = ''
            
            name = ingredient.select('.wprm-recipe-ingredient-name')[0].string
            ingredients.append(f'{amount} {unit} {name}')

        self.ingredients = frozenset(ingredients)
        print(self.ingredients) 
        return self.ingredients
    
    def parse_recipe(self, html):
        body = BeautifulSoup(html, 'html.parser')
        self.html = body
        recipe = body.select('.pon-section-4')[0]
        self.title = recipe.select('h2')[0].string
        self.description = recipe.select('h5')[0].string
        return recipe
    
    def parse_steps(self):
        body = self.html
        steps_p = body.select('.pon-recipe-step-info > p')
        self.steps = [f"{i}. {step.text}" for i, step in enumerate(steps_p, 1)]
        print(self.steps)
        return self.steps


class PinchPrinter(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('printer.pinch.intent')
    def handle_printer_pinch(self, message):
        query = message.data.get('query')

        pinch = PinchOfNomScraper(query=query)
        self.log.info(f"Got class for query {query}", pinch)
        status_code, body = pinch.get_recipes()
        pinch.parse_recipes(body)

        if pinch.recipes:
            pinch.choose_recipe()
            status_code, recipe_body = pinch.get_recipe()
            recipe_body = pinch.parse_recipe(recipe_body)
            ingredients = str(pinch.parse_ingredients(recipe_body))
            steps = str(pinch.parse_steps())
            recipe = f"{ingredients} {steps}"

            self.speak_dialog('printer.pinch', data={
                'recipe': recipe,
                'query': query
            })


def create_skill():
    return PinchPrinter()

