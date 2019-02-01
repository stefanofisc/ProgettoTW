from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField, SubmitField

class RegistrationForm(Form):
    nome = StringField('nome', [validators.Length(min=2, max=25)], render_kw={"placeholder": "nome"})
    cognome = StringField('cognome', [validators.Length(min=2, max=25)], render_kw={"placeholder": "cognome"})
    email = StringField('email', [validators.Length(min=6, max=35)], render_kw={"placeholder": "email"})
    username = StringField('username', [validators.Length(min=4, max=25)], render_kw={"placeholder": "username"})
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
    ], render_kw={"placeholder": "password"})
    confirm = PasswordField('Repeat Password', render_kw={"placeholder": "repeat password"})

class LoginForm(Form):
    username = StringField('username', [validators.DataRequired()], render_kw={"placeholder": "username"})
    password = PasswordField('password', [validators.DataRequired()], render_kw={"placeholder": "password"})

class EditBlogPostForm(Form):
    titolo = StringField('Titolo', [validators.DataRequired()], render_kw={"placeholder": "Inserisci un titolo"})
    body = TextAreaField('Testo', [validators.DataRequired()])
    url_img = StringField('Url_img', [validators.DataRequired()], render_kw={"placeholder": "Inserisci un url"})
    url_video = StringField('Id_video', [validators.DataRequired()], render_kw={"placeholder": "Inserisci id del video"})
    desc_video = TextAreaField('Descrizione', [validators.DataRequired()])
    submit = SubmitField('Ok')

class CommentBlogPostForm(Form):
    body = TextAreaField('Testo', [validators.DataRequired(), validators.length(max=800)])
    submit = SubmitField('Ok')

class VisualPassesForm(Form):
    norad_id = StringField('norad_id', [validators.DataRequired(), validators.length(max=5)], render_kw={"placeholder": "id 5-cifre"})
    days = StringField('days', [validators.DataRequired()], render_kw={"placeholder": "max 10"})
    min_visibility = StringField('min_visibility', [validators.DataRequired()], render_kw={"placeholder": "in secondi"})
    submit = SubmitField('Ok')

class SeeMore(Form):
    submit = SubmitField('Ok')