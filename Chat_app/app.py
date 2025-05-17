import json
import requests
from flask import Flask, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask import redirect, url_for

# ───────────────────────────────────────────────
# Initialisation Flask + SocketIO + Base SQLite
# ───────────────────────────────────────────────
app = Flask(__name__)

# Base de données SQLite (fichier local)
db_name = 'notes.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
db = SQLAlchemy(app)

# SocketIO : CORS libre pour le dev ; async_mode="eventlet" pour le temps réel
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# ───────────────────────────────────────────────
# Modèle SQLAlchemy
# ───────────────────────────────────────────────
class Note(db.Model):
    __tablename__ = 'note'
    id      = db.Column(db.Integer, primary_key=True)
    title   = db.Column(db.String)
    content = db.Column(db.String)
    done    = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# ───────────────────────────────────────────────
# Routes API
# ───────────────────────────────────────────────
@app.route('/')
def root():
    # redirige vers la page front-end des notes
    return redirect(url_for('front_notes'))

"""
Créer une note :
http :5001/api/notes title="courses" content="acheter des céréales"
http :5001/api/notes title="devoirs" content="lire le cours de MMC" done=true
"""
@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        params  = json.loads(request.data)
        title   = params['title']
        content = params['content']
        done    = params.get('done')
        to_bool = lambda x: str(x).lower() in ['true', '1', 'yes', 'on']

        note = Note(
            title   = title,
            content = content,
            done    = to_bool(done) if done is not None else False
        )
        db.session.add(note)
        db.session.commit()
        return {'id': note.id, 'title': note.title, 'content': note.content, 'done': note.done}
    except Exception as exc:
        return {'error': f'{type(exc).__name__}: {exc}'}, 422

"""
Lister toutes les notes :
http :5001/api/notes
"""
@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [
        {'id': n.id, 'title': n.title, 'content': n.content, 'done': n.done}
        for n in notes
    ]



"""
Basculer l’état done d’une note :
http :5001/api/notes/3/done   (via PATCH)
"""
@app.route('/api/notes/<int:note_id>/done', methods=['PATCH'])
def toggle_done(note_id):
    note = Note.query.get_or_404(note_id)
    note.done = not note.done
    db.session.commit()

    # Diffusion en temps réel à tous les navigateurs
    socketio.emit('note_updated', {'id': note.id, 'done': note.done}, broadcast=True)
    return {'id': note.id, 'done': note.done}

# ───────────────────────────────────────────────
# Frontend (rend le template Jinja2)
# ───────────────────────────────────────────────
@app.route('/front/notes')
def front_notes():
    notes = Note.query.all()          # ← accès direct SQLAlchemy
    notes = [{'id': n.id, 'title': n.title,
              'content': n.content, 'done': n.done} for n in notes]
    return render_template('notes.html.j2', notes=notes)

# ───────────────────────────────────────────────
# Données initiales (si la table est vide)
# ───────────────────────────────────────────────
with app.app_context():
    if Note.query.count() == 0:
        db.session.add_all([
            Note(title="courses", content="acheter des céréales", done=False),
            Note(title="devoirs", content="lire le cours de MMC", done=False),
        ])
        db.session.commit()

# ───────────────────────────────────────────────
# Lancement de l’application
# ───────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)

