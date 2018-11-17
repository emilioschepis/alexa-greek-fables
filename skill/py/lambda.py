import logging

# ask_sdk_core
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

# ask_sdk_model
from ask_sdk_model import Response

# extra
from random import randrange
from boto3.dynamodb.conditions import Key
import boto3
import os

TABLE_NAME = os.environ['TABLE_NAME']
STORIES_COUNT = int(os.environ['STORIES_COUNT'])

sb = SkillBuilder()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Fable:
    def __init__(self, title, quote, story):
        self.title = title
        self.quote = quote
        self.story = story

    def speech(self):
        # type: (Fable) -> str
        return """
        This story is called '{}'<break time="1s"/>
        {}<break time="1s"/>
        The lesson is: {}
        """.format(self.title, self.story, self.quote)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type('LaunchRequest')(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = 'Welcome to Greek Fables! '
        speech_question = 'Would you like to hear a story?'

        handler_input.response_builder \
            .speak(speech_text + speech_question) \
            .ask(speech_question)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name('AMAZON.HelpIntent')(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = 'You can ask me to read you a fable!'

        handler_input.response_builder \
            .speak(speech_text) \
            .ask(speech_text)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler for Cancel and Stop Intents."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name('AMAZON.CancelIntent')(handler_input) or
                is_intent_name('AMAZON.StopIntent')(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Exception handler for any exception"""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech_text = "Sorry, there was a problem. Try again in a few moments."

        handler_input.response_builder \
            .speak(speech_text) \
            .set_should_end_session(True)
        return handler_input.response_builder.response


class ReadFableIntentHandler(AbstractRequestHandler):
    """Handler ReadFable Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name('ReadFableIntent')(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        random_id = randrange(0, STORIES_COUNT)
        query_result = table.query(
            KeyConditionExpression=Key('id').eq(random_id)
        )

        if len(query_result['Items']) != 1:
            raise FileNotFoundError('Could not find a fable with the specified id of {}.'.format(random_id))

        fable_data = query_result['Items'][0]
        fable = Fable(
            fable_data['title'],
            fable_data['quote'],
            fable_data['story']
        )

        handler_input.response_builder \
            .speak(fable.speech()) \
            .set_should_end_session(True)
        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(ReadFableIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
