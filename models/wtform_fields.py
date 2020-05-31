from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class MessageForm(FlaskForm):
    """ Message form
    """

    message = StringField('message')
    submit = SubmitField('send')