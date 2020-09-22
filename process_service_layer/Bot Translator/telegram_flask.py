from flask import Flask, Response
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
import requests
import json


bot_token = '1231315957:AAG_sYHCOWxGPKpHxKtmr1iowV8zy2j8Lhs'

app = Flask(__name__)


def start(update, context):
	user = {
        'id': update.message.from_user.id,
        'firstName': update.message.from_user.first_name,
        'lastName': update.message.from_user.last_name,
    }
	context.bot.send_message(chat_id=update.message.from_user.id, text="Hi {}, Welcome to our bot translator.\n For more information and how to use the bot please type this '/help_info' command.".format(user['firstName']))
    
def translate(update, context):
	if len(context.args) == 0:
		context.bot.send_message(chat_id=update.message.from_user.id, text="Please provide some text to be translated")
      
	else:
		# merging all the words passed from the user
		text = ' '.join(context.args)  # ['hello', 'world'] -> 'hello world'
		context.bot.send_message(chat_id=update.message.from_user.id, text="Translating '" + text + "'")
    
		#route to destination_langauge service
		url = 'http://127.0.0.1:5003/language'
		myobj = {
			'user_id': update.message.from_user.id
		}

		res = requests.get(url, params=myobj)    
		dest_lang = res.json()['retreived']
    
		# route to the translation service
		url = 'http://127.0.0.1:5002/translate'
		myobj = {
			'text': text,
			'dest_lang': dest_lang
		}

		res = requests.post(url, data=myobj)
		# read the json response
		translated = res.json()['response']
		context.bot.send_message(chat_id=update.message.from_user.id, text=translated)

	
def dest_language(update, context):
	if len(context.args) == 0:
		context.bot.send_message(chat_id=update.message.from_user.id, text="Please provide the language code of the destination language")
			
	else:
		# getting user prefered destination language
		lang = context.args[0]  # ['it'] -> 'it'
    
		# route to the language service
		url = 'http://127.0.0.1:5003/language'
		myobj = {
			'user_id': update.message.from_user.id,
			'dest_lang': lang
		}

		res = requests.post(url, data=myobj)
		context.bot.send_message(chat_id=update.message.from_user.id, text='Selected langauge: ' + lang)
	
	
    
def list_languages(update, context):
	if len(context.args) == 0:
		#getting user prefered destination language
		languages = ' '.join(context.args) 
    
		#route to the language service
		url = 'http://127.0.0.1:5005/list'
		myobj = {
			'list_lang': languages
		}

		res = requests.get(url)
		languages = res.json()['retreived']
		print(type(languages))

		dict_lang = ""
		for each in languages['langauges']:
			a = each['language']
			b = each['code']
			dict_lang += a+" : " +b +"\n"
			print(a + ':' + b)
    
		context.bot.send_message(chat_id=update.message.from_user.id, text='Supported langauges with their langauge codes: ' +"\n"+ dict_lang)  

		
	else:
		context.bot.send_message(chat_id=update.message.from_user.id, text="Oops! something went wrong, make sure not to add any additional text after the command")
		
    

def detect(update, context):
	if len(context.args) == 0:
		context.bot.send_message(chat_id=update.message.from_user.id, text="Please provide some text to be detected")
	else:
		# merging all the words passed from the user
		text = ' '.join(context.args)  # ['hello', 'world'] -> 'hello world'
		context.bot.send_message(chat_id=update.message.from_user.id, text="Detecting '" + text + "'")
    
		# route to the detect language service
		url = 'http://127.0.0.1:5004/detect'
		myobj = {
			'text': text
		}

		res = requests.post(url, data=myobj)
		# read the json response
		detected_language = res.json()['response']
		context.bot.send_message(chat_id=update.message.from_user.id, text=detected_language)
		
Help_message = ("Welcome to the Telegram Bot Translator, to translate text to another langauge, you have to first choose the destination langauge using the '/dest_language' command.\n For example, '/dest_language it'\n"
"\nThen use '/translate' command to transalte your text input to another language.\n For example '/translate hello how are you'\n"
"\nUse '/list_languages' command to list the languages that are supported by the bot application and their corresponding language codes which you require to successfully run the '/dest_language' command. This command does not require extra user input\n"
"\nTo identify what language a text belongs to, use the '/detect' command.\n For example '/detect come stai'\n"
"\n You are officially up to date with all the commands, lets go translate some texts..")

def help_info(update, context):
    context.bot.send_message(chat_id=update.message.from_user.id, text= Help_message)

    

def init_bot():
    updater = Updater(token=bot_token, use_context=True)

    dispatcher = updater.dispatcher

    # let accept "/start" messages from the bot
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    # let accept "/help_info" messages from the bot
    help_handler = CommandHandler('help_info', help_info)
    dispatcher.add_handler(help_handler)

    # let accept "/translate ..." from the bot
    translate_handler = CommandHandler('translate', translate)
    dispatcher.add_handler(translate_handler)
    
    # let accept "/dest_language ..." from the bot
    dest_lang_handler = CommandHandler('dest_language', dest_language)
    dispatcher.add_handler( dest_lang_handler)
      
    # let accept "/list_languages" from the bot
    list_handler = CommandHandler('list_languages', list_languages)
    dispatcher.add_handler(list_handler)
    
    # let accept "/detect..." from the bot
    detect_handler = CommandHandler('detect', detect)
    dispatcher.add_handler(detect_handler)

    return updater
    
updater = init_bot()

@app.route('/start', methods=['GET', 'POST'])
def start():
	# start the telegram bot
	updater.start_polling()
	return Response('{"running":true}', status=200, mimetype='application/json')
	
@app.route('/stop', methods=['GET', 'POST'])
def stop():
	# start the telegram bot
	updater.stop()
	return Response('{"running":false}', status=200, mimetype='application/json')	


if __name__ == '__main__':
    app.run(debug=True, port=5001)
