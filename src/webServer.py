import flask
from flask import Flask
import smtpService
import os
import json
from functools import wraps

app = Flask(__name__)

credentials = json.loads(os.getenv("CREDENTIALS"))
key = os.getenv("KEY")


def checkFrom(from_value):
    """
    Function to verify if it's possible to send mail with the mail in parameter.
    Basically check if parameter match with stored credentials
    :param from_value: email to check
    :return: match boolean
    """
    for account in credentials.items():
        if account[0] == from_value:
            return True
    return False


def requireApiKey(view_function):
    """
    Decorator for API key
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if flask.request.headers.get('x-api-key') == key:
            return view_function(*args, **kwargs)
        else:
            flask.abort(401)
    return decorated_function


@app.route('/', methods=["GET"])
def index():
    """
    A little documentation
    :return: an HTML documentation of this web service
    """
    return flask.render_template('index.html')


@app.route("/sendemail", methods=["POST"])
@requireApiKey
def sendEmail():
    """
    Post http method to send mail
    Data example :
        {
            "From": "overbookd@24heures.org",
            "To": [
                "mail@domain.fr",
                "foo@bar.net"
            ],
            "Subject": "Testing mail",
            "Body": "Hello world"
        }
    :return: http 400 code if no correct data.
             http 200 code if mail can sent
    """
    mail = flask.request.json

    # Checking data
    try:
        mail["From"]
    except KeyError:
        return "'From' key is mandatory, check /getemaillist for more detail", 400
    try:
        mail["To"]
    except KeyError:
        return "'To' key is mandatory. It should a email list", 400
    if not isinstance(mail["To"], list):
        return "'To' value should be a list", 400
    try:
        mail["Subject"]
    except KeyError:
        return "'Subject' key is mandatory. It should a string", 400
    try:
        mail["Body"]
    except KeyError:
        return "'Body' key is mandatory. It should a string", 400

    # Check sender before send mail
    if checkFrom(mail["From"]):
        # SmtpSender object creation
        sender = smtpService.SmtpSender(
            mail["From"],
            credentials[mail["From"]],
            mail["To"],
            mail["Subject"],
            mail["Body"]
        )
        # Check of wrong emails on receivers list
        if not sender.getWrongEmails():
            sender.sendEmail()
            return "Mail sent", 200
        else:
            return "There is some wrong emails, check /verifyemails for more details", 400
    else:
        return f"{mail['From']} is not valid", 400


@app.route("/verifyemail", methods=["POST"])
@requireApiKey
def verifyEmails():
    """
    Post http request to check emails validity
    Data example :
        [
            "mail@domain.fr",
            "foo@bar.net"
        ]
    :return: list of none valid emails
    """
    email = flask.request.json
    if not isinstance(email, list):
        return "Parameter should be a list", 400
    # SmtpSender object with just email for checking
    sender = smtpService.SmtpSender("", "", email, "", "")
    return flask.jsonify(sender.getWrongEmails())


@app.route("/getemaillist", methods=["GET"])
@requireApiKey
def getEmailList():
    """
    http get request to get available sender mail
    :return: list of available mails
    """
    return flask.jsonify(list(credentials.keys()))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
