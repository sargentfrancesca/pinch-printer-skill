from mycroft import MycroftSkill, intent_file_handler
from scraper import PinchOfNomScraper


class PinchPrinter(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('printer.pinch.intent')
    def handle_printer_pinch(self, message):
        query = message.data.get('query')

        pinch = PinchOfNomScraper(query=search)
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

