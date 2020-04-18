from mycroft import MycroftSkill, intent_file_handler


class PinchPrinter(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('printer.pinch.intent')
    def handle_printer_pinch(self, message):
        query = message.data.get('query')
        recipe = ''

        self.speak_dialog('printer.pinch', data={
            'recipe': recipe,
            'query': query
        })


def create_skill():
    return PinchPrinter()

