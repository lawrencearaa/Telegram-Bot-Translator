from flask import Flask, Response, request
from googletrans import Translator
import json

app = Flask(__name__)
translator = Translator()


@app.route('/detect', methods=['POST'])
def detect_language():
	# Receive text from user and identify what language it belongs to
	text = request.form['text']
	output = translator.detect(text)
	#detected_language = json.dumps(output)
	return Response('{"response":"' + output.lang + '"}', status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=5004)

