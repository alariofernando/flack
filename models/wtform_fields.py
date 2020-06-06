from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import Length

class MessageForm(FlaskForm):
    """ Message form
    """

    message = StringField('message', widget=TextArea())
    submit = SubmitField('send')

class ChannelForm(FlaskForm):
    """
    Channel creation software
    """

    name = StringField('channel', validators=[Length(min=5, max=25, message="Please input a name between 5 and 25 characters")])
    submit = SubmitField('send')