# -*- coding: utf-8 -*-
import yaml
from flask import request, Flask
import sys

try:
    # load qi and connect to animated say service
    import qi
    session = qi.Session()
    try:
        session.connect("tcp://{ip}:9559".format(ip=sys.argv[1]))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + sys.argv[1] + " \"")
        sys.exit(1)

    tts = session.service("ALAnimatedSpeech")
    speech_config = session.service("ALTextToSpeech")
    speech_config.setParameter("speed", 75)

except ImportError:
    print("!!! NAOQI COULD NOT BE LOADED !!!")
    class tts_stub():
        def say(self, line, config):
            print(line)
    tts = tts_stub()

configuration = {"bodyLanguageMode":"contextual"}

# load all the buttons and the lines to say
with open("voicelines.yaml", "r") as voicelines_file:
    voicelines = yaml.load(voicelines_file)
    line_names = [x for line in voicelines for x in line.keys()]
    line_dict = dict()
    for item in voicelines:
        for key, value in item.items():
            line_dict[key] = value
    voicelines = line_dict
app = Flask(__name__)


# generate a HTML stub that shows all the buttons
button_string = '<form action="/{name}"><input type="submit" value="{name}"></form>\n'
buttons = list()
for name in line_names:
    buttons.append(button_string.format(name=name))

website = """
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>HTML5 boilerplate – all you really need…</title>
	<link rel="stylesheet" href="css/style.css">
	<!--[if IE]>
		<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
</head>

<body id="home">

	{buttons}
    <form action="/" method="POST"><input type="text" name="line"><input type="submit" value="Say"></form>
</body>
</html>
""".format(buttons="".join(buttons))


@app.route('/', defaults={"voiceline": None}, methods=["GET", "POST"])
@app.route('/<voiceline>')
def home(voiceline):
    if voiceline in voicelines:
        tts.say(voicelines[voiceline], configuration)
    elif request.form and request.form["line"]:
        tts.say(request.form["line"], configuration)
    return website

if __name__ == "__main__":
    app.run(debug=True, port=5579, host='192.168.43.75')


