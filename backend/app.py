import pathlib as pl

import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

data = pl.Path(__file__).parent.absolute() / 'data'

# Charger les données CSV
associations_df = pd.read_csv(data / 'associations_etudiantes.csv')
evenements_df = pd.read_csv(data / 'evenements_associations.csv')

## Vous devez ajouter les routes ici : 

# Liste de toutes les associations
@app.route('/api/associations', methods=['GET'])
def getAssociations():
    return associations_df['id'].tolist(), 200

# Détails d'une association
@app.route('/api/association/<int:id>', methods=['GET'])
def infoAssociation(id):
    association = associations_df[associations_df['id'] == id]
    if association.empty:
        return {"error": "Association not found"}, 404
    return association.to_dict(orient='records'), 200

# Liste de tous les événements
@app.route('/api/evenements', methods=['GET'])
def getEvents():
    return evenements_df['id'].tolist(), 200

# Détails d'un événement
@app.route('/api/evenement/<int:id>', methods=['GET'])
def infoEvent(id):
    evenement = evenements_df[evenements_df['id'] == id]
    if evenement.empty:
        return {"error": "Event not found"}, 404
    return evenement.to_dict(orient='records'), 200

# Liste des événements d'une association
@app.route('/api/association/<int:id>/evenements', methods=['GET'])
def getAssociationEvents(id):
    events = evenements_df[evenements_df['association_id'] == id]
    return events['id'].tolist(), 200

# Liste des associations par type
@app.route('/api/associations/type/<string:type>', methods=['GET'])
def getAssociationsType(type):
    filtered_associations = associations_df[associations_df['type'] == type]
    return filtered_associations['id'].tolist(), 200

# Vérifier si le serveur est actif
@app.route('/api/alive', methods=['GET'])
def status():
    return {"message": "Alive"}, 200


if __name__ == '__main__':
    app.run(debug=False)
