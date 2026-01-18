import os
from flask import Flask, render_template, jsonify, request
from supabase import create_client, Client
from datetime import datetime

# 1. Setup - Vi skapar bara appen här
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/tasks')
def get_tasks():
    try:
        # Vi hämtar URL och KEY exakt när de behövs
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        # Skapa klienten lokalt inuti funktionen
        supabase_client = create_client(url, key)
        
        response = supabase_client.table('tasks').select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/menu')
def get_menu():
    vecko_meny = {
        "Monday": "Pannbiff med gräddsås och potatismos",
        "Tuesday": "Raggmunk med stekt fläsk och lingon",
        "Wednesday": "Chili con Carne serveras med ris",
        "Thursday": "Köttbullar med potatismos och gräddsås",
        "Friday": "Kålpudding med gräddsås och potatismos",
        "Saturday": "Grillad Entrecôte med bearnaise",
        "Sunday": "Söndagsstek med inlagd gurka"
    }
    dagar_se = {
        "Monday": "Måndag", "Tuesday": "Tisdag", "Wednesday": "Onsdag",
        "Thursday": "Torsdag", "Friday": "Fredag", "Saturday": "Lördag", "Sunday": "Söndag"
    }
    idag_engelska = datetime.now().strftime('%A')
    return jsonify({
        'day': dagar_se.get(idag_engelska, "Idag"),
        'dish': vecko_meny.get(idag_engelska, "Se menyn på plats")
    })

# Ingen "app = app" och ingen global "supabase" variabel här nere