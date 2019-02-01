from flask import session, render_template, request, url_for, redirect
from app import app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import requests 
import json

mongo = PyMongo(app)

class Utente:
    # la function def_utente verifica se c'è un utente connesso e restituisce i suoi dati principali
    def def_utente():
        if not session.get('logged_in'):
            username = 'Guest'
        else:
            username = session.get('username')
        utente = [username, session.get('admin')]
        return utente
 
class Package:
    def __init__(self,start,max,end,d,startaz,startazcomp,startel,maxaz,maxazcomp,maxel,endaz,endazcomp,endel):
        self.startUTC = start
        self.maxUTC = max
        self.endUTC = end
        self.duration = d
        self.startAz = startaz
        self.startAzCompass = startazcomp
        self.startEl = startel
        self.maxAz = maxaz
        self.maxAzCompass = maxazcomp
        self.maxEl = maxel
        self.endAz = endaz
        self.endAzCompass = endazcomp
        self.endEl = endel



@app.route('/')
@app.route('/index')
def home():
    utente = Utente.def_utente()
    ora_del_giorno = datetime.now().hour
    return render_template('homepage.html', utente=utente, titolo='Homepage', ora_del_giorno=ora_del_giorno, messaggio='Buongiorno')


from app.forms import SeeMore
@app.route('/news', methods=['GET', 'POST'])
def news():
    utente = Utente.def_utente()
    see_more = SeeMore(request.form)
    # chiedo i 5 post più recenti nel database
    post_collezione = mongo.db.posts
    posts = post_collezione.find().sort([('creato_il', -1)]).limit(5)
    # carica i dati dei satelliti
    satellites = mongo.db.satellites.find({})

    if request.method == 'POST' and see_more.validate():
        # carica tutti i post dal database e ordinali
        all_posts = post_collezione.find({}).sort([('creato_il', -1)])
        return render_template('news.html',utente=utente,titolo='News',posts=all_posts,norad_id="25544",satellites=satellites)
   
    return render_template('news.html', utente=utente, titolo='News', posts=posts, norad_id="25544", satellites=satellites)
    

@app.route('/about')
def about():
    utente = Utente.def_utente()
    satellites = mongo.db.satellites.find({})
    return render_template('about.html', utente=utente, titolo='Info', satellites=satellites)


from app.forms import EditBlogPostForm
from app.forms import CommentBlogPostForm
@app.route('/posts/id/<string:id>/modify', methods=['GET', 'POST'])
def modify(id):
    # prendo i dati dell'utente per verificare poi le sue autorizzazioni
    utente = Utente.def_utente()
    # carico i form di modifica post e commenta post
    form = EditBlogPostForm(request.form)
    comment_form = CommentBlogPostForm(request.form)
    
    # cerca il post da modificare
    to_edit_post = mongo.db.posts.find_one({'_id' : ObjectId(id)})

    # se l'admin vuole modificare il post 
    if request.method == 'POST' and form.validate():
        # prendo i dati dal form
        titolo = form.titolo.data
        body = form.body.data
        url_img = form.url_img.data
        url_video = form.url_video.data
        desc_video = form.desc_video.data
        try:
            to_edit_post['titolo'] = titolo
            to_edit_post['body'] = body
            to_edit_post['url_img'] = url_img
            to_edit_post['url_video'] = url_video
            to_edit_post['desc_video'] = desc_video
            mongo.db.posts.save(to_edit_post)
            return redirect(url_for('post', utente=utente, titolo='Modifica post', id = to_edit_post['_id']))
        except:
            return 'Non sono riuscito a modificare il post'

    # se l'utente vuole commentare il post
    elif request.method == 'POST' and comment_form.validate():
        # prendo i dati dal form
        body = comment_form.body.data
        # inserisci il commento al post nel database
        try:
            # prendo la data di creazione del commento
            now = datetime.now()
            creato_il = now.strftime('%d/%m/%Y, %H:%M:%S')
            commenti = mongo.db.comments
            commenti.insert({'autore' : utente[0], 'creato_il' : creato_il, 'body' : body, 'id_post' : str(to_edit_post['_id'])})
            return redirect(url_for('post', utente=utente, titolo='Commenta post', id = to_edit_post['_id']))
        except:
            return "Errore nell'inserimento del commento"
    else:
        # altrimenti renderizza la pagina di modifica del post, con i form già precompilati con i dati da modificare
        modifica = 1 # la invio all'edit post per fargli capire che deve mostrare il tasto "modifica post" e non "crea post"
        form.titolo.data = to_edit_post['titolo']
        form.body.data = to_edit_post['body']
        form.url_img.data = to_edit_post['url_img']
        form.url_video.data = to_edit_post['url_video']
        form.desc_video.data = to_edit_post['desc_video']    
        return render_template('edit_post.html', utente=utente, titolo='Edit post', modifica=modifica, form=form)            

# mostra la pagina completa del post richiesto
@app.route('/posts/id/<string:id>', methods=['GET', 'POST'])
def post(id):
    # form per il commento al post
    form = EditBlogPostForm(request.form)
    # prendo i dati dell'utente connesso
    utente = Utente.def_utente()
    # apro connessione con il database e cerco il post richiesto
    post = mongo.db.posts
    find_post = post.find_one({'_id' : ObjectId(id)})
    # se il post non esiste lo notifico su schermo
    if not find_post:
        return 'Invalid _id: post not found'
    # carico i commenti relativi al post
    commenti = mongo.db.comments.find({'id_post' : id})
    
    # renderizza la pagina se l'utente l'ha solo aperta
    if request.method == 'GET':
        return render_template('post.html', utente=utente, titolo=find_post['titolo'], post=find_post, commenti=commenti, form=form)
    # altrimenti l'utente ha interagito con la pagina (modifica post in place)
    else:
        return modify(find_post['_id'])

# crea un nuovo post
@app.route('/posts/new', methods=['GET', 'POST'])
def get_post():
    # prendo i dati dell'utente che crea il post
    utente = Utente.def_utente()
    
    form = EditBlogPostForm(request.form)
    # se l'utente vuole creare un nuovo post
    if request.method == 'POST' and form.validate():
        # prendo i dati dal form
        titolo = form.titolo.data
        body = form.body.data
        url_img = form.url_img.data
        url_video = form.url_video.data
        desc_video = form.desc_video.data
        autore = session.get('username')
        # prendo la data di creazione del post
        now = datetime.now()
        creato_il = now.strftime('%d/%m/%Y, %H:%M:%S')
        # inserisco i dati nel database
        try:
            post = mongo.db.posts
            post.insert({'titolo':titolo,'body':body,'autore':autore,'creato_il':creato_il,'url_img':url_img,'url_video':url_video,'desc_video':desc_video})
            this_post = post.find_one({'creato_il' : creato_il})
            #return post(utente,'Crea post',this_post, this_post['_id'])
            return redirect(url_for('post', utente=utente, titolo='Crea post', id = this_post['_id']))
        except:
            return 'Non sono riuscito ad inserire il post' #function Javascript
    return render_template('edit_post.html', utente=utente, titolo='Edit post', form=form)            


@app.route('/login')
def login():
    utente = Utente.def_utente()
    form = LoginForm(request.form)
    return render_template('login.html', utente=utente, titolo='Login',form=form)

from app.forms import LoginForm
@app.route('/login_user', methods=['POST'])
def login_user():
    utente = Utente.def_utente()
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        #prendo i dati dal form
        username = form.username.data
        password = form.password.data
        # apro connessione con il database
        user = mongo.db.utenti
        # cerco l'utente nel database
        login_user = user.find_one({'username': username})

        # se ho trovato l'username, verifico la password
        if login_user:
            if check_password_hash(login_user['password'], password):
                session.clear()
                # verifica utente/admin
                if login_user['admin']:
                    session['admin'] = True
                else:
                    session['admin'] = False
                session['username'] = username
                session['logged_in'] = True
                return home()
        # altrimenti gli notifico che il login è fallito
        return render_template('login.html', titolo='Login', utente=utente, form=form, error='Invalid username/password combination')

    return render_template('login.html', titolo="Login", utente=utente, form=form)

from app.forms import RegistrationForm
@app.route('/register', methods=['POST', 'GET'])
def register():
   utente = Utente.def_utente()
   form = RegistrationForm(request.form)
   if request.method == 'POST' and form.validate():
     # prendo i dati dal form di input
     nome = form.nome.data
     cognome = form.cognome.data
     email = form.email.data
     username = form.username.data
     password = form.password.data
     admin = False

     # mi connetto al database per verificare se l'username già esiste
     user = mongo.db.utenti
     existing_user = user.find_one({'username': username})
     # se l'utente non esiste, lo posso registrare
     # lo inserisco nel database ed effettuo automaticamente il login
     if existing_user is None:
        hashpass = generate_password_hash(password)
        user.insert({'nome': nome, 'cognome': cognome, 'email': email, 'username': username, 'password': hashpass, 'admin': admin})
        session.clear()
        session['username'] = username
        session['logged_in'] = True
        return home()
     # altrimenti gli notifico che la registrazione è fallita
     return render_template('register.html', titolo='Sign up', utente=utente, form=form, error = 'Registration failed: that username already exists!')
   # renderizza la pagina se la richiesta è GET 
   return render_template('register.html', titolo='Sign up',utente=utente, form=form)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.clear()
    return home()

@app.route('/satellite/<string:noradId>')
def satellite(noradId):
    utente = Utente.def_utente()
    # prendo i dati del satellite e li mando alla pagina
    sat_info = mongo.db.satellites.find_one({'satid' : noradId})
    return render_template("satellite.html", utente=utente, titolo="Satellite tracking", sat_info=sat_info, norad_id=noradId)


from app.forms import VisualPassesForm
@app.route('/visualpasses', methods=['GET','POST'])
def visualpasses():
    utente = Utente.def_utente()                # prendo i dati dell'utente
    form = VisualPassesForm(request.form)       # prendo i dati dal form
    satellites = mongo.db.satellites.find({})   # prendo i dati dei satelliti
                                                # prendo i dati geografici del visitatore
    pos = requests.get('http://api.ipstack.com/check?access_key=77d0b411d2b9bb6356575b9ad686681f')
    data = pos.json() 
    lat = str(data['latitude'])
    lng = str(data['longitude'])
    
    if request.method == 'POST' and form.validate():
                                                # prendo i dati dal form e ne verifico la correttezza
        id = form.norad_id.data
        days = form.days.data
        min_visibility = form.min_visibility.data
        check_days = int(days)
        if check_days > 10:
            days = "10"
                                                #satellites = mongo.db.satellites.find({})
        count = 0
        for sat in satellites:
            if id == sat['satid']:
                count = count + 1
        if count == 0:
            error = "Invalid NORAD id"
            return render_template("visualpasses.html", utente=utente, titolo="Visual passes", form=form, coord=data, error=error)
                                                # effettuo la richiesta vera e propria
        apiKey = '&apiKey=4MED2Z-GCCMV8-GPP7PZ-3XYW'
        apiRequest = 'http://www.n2yo.com/rest/v1/satellite/visualpasses/'+id+'/'+lat+'/'+lng+'/'+'0/'+days+'/'+min_visibility+'/'+apiKey
        response = requests.get(apiRequest)
        data1 = response.json()        
                                                # verifico l'esito della richiesta 
                                                # converto gli unix timestamp in UTC time zone
                                                # costruisco un pacchetto dati e lo mando al template
        if len(data1['info']) < 4:
            error = "Satellite " + data1['info']['satname'] + ": out-of-range"
            return render_template("visualpasses.html", utente=utente, titolo="Visual passes", form=form, coord=data, error=error)
        if data1['info']['passescount'] == 0:
            error = "Non sono previsti passaggi di questa tipologia!"
            return render_template("visualpasses.html", utente=utente, titolo="Visual passes", form=form, coord=data, error=error)
        else:
            package = []
            startUTC = []
            maxUTC = []
            endUTC = []
        
            i=0
            for data in data1['passes']:
                startUTC.append(datetime.utcfromtimestamp(data['startUTC']).strftime('%Y-%m-%d %H:%M:%S'))
                maxUTC.append(datetime.utcfromtimestamp(data['maxUTC']).strftime('%Y-%m-%d %H:%M:%S'))
                endUTC.append(datetime.utcfromtimestamp(data['endUTC']).strftime('%Y-%m-%d %H:%M:%S'))
                
                package.append( Package(startUTC[i], maxUTC[i], endUTC[i], data['duration'],
                                data['startAz'], data['startAzCompass'], data['startEl'],
                                data['maxAz'], data['maxAzCompass'], data['maxEl'],
                                data['endAz'], data['endAzCompass'], data['endEl']) )
                i = i+1
               
            return render_template('visualpasses.html', utente=utente, titolo="Visual passes", form=form, coord=data, package=package, nome=data1['info']['satname'], passaggi=data1['info']['passescount'])
    
    return render_template("visualpasses.html", utente=utente, titolo="Visual passes", form=form, coord=data)