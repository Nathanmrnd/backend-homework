import json
import requests
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# Usual flask initialization
app = Flask(__name__)

# Database declaration
db_name = 'notes.db'   # filename where to store stuff (sqlite is file-based)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name      # how do we connect to the database ? here we say it's by looking in a file named chat.db
db = SQLAlchemy(app)    # this variable, db, will be used for all SQLAlchemy commands


@app.route('/')
def test():
    return f"mon serveur fonctionne"

# Define a table in the database
class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean, default=False)

with app.app_context():     # actually create the database (i.e. tables etc)
    db.create_all()

  
"""
http :5001/api/notes title="courses" content="acheter des céréales" done=True
http :5001/api/notes title="devoirs" content="lire le cours de MMC" done=0
http :5001/api/notes title="devoirs" content="faire la vaiselle"
"""    
@app.route('/api/notes', methods=['POST'])
def create_note():
    # we expect the user to send a json object with the 3 fields (title, content, done)
    try:
        parameters = json.loads(request.data)
        title = parameters['title']
        content = parameters['content']
        done = parameters.get('done', None)  # attention renvoie une chaîne de caractère
        
        if done == None:
            new_note = Note(title=title, content=content)   # création d'un objet de type Notes, done=False par défaut
        else :
            # j'ai des problèmes de conversion 
            # on prend l'objet donné par l'utilisateur, on le convertit en string, on le met en minuscules 
            # et on renvoie True si il appartient à la liste
            to_bool = lambda x: str(x).lower() in ['true', '1']
            new_note = Note(title=title, content=content, done=to_bool(done))  
        
        print("received request to create note")
        db.session.add(new_note)
        db.session.commit()
        return parameters
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422
    
"""
http :5001/api/notes
"""
@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(id=note.id, title=note.title, content=note.content, done=note.done) for note in notes]


"""
http :5001/api/notes/<id>/done
"""
# to be continued


# Frontend
"""
http://localhost:5001/front/notes
"""
@app.route('/front/notes')
def front_users():
    url = request.url_root + '/api/notes'
    req = requests.get(url)
    if not (200 <= req.status_code < 300):
        return dict(error=f"could not request notes list", url=url,
                    status=req.status_code, text=req.text)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes)

if __name__ == '__main__':
    app.run(debug=False)