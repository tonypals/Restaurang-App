import os
from flask import Flask, render_template, jsonify
from supabase import create_client
from datetime import datetime

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
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        # Vi skapar klienten inuti anropet för att inte låsa resurser
        supabase = create_client(url, key)
        response = supabase.table('tasks').select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    #

@app.route('/api/menu')
def get_menu():
    vecko_meny = {
        "Monday": "Pannbiff", "Tuesday": "Raggmunk", "Wednesday": "Chili con Carne",
        "Thursday": "Köttbullar", "Friday": "Kålpudding", "Saturday": "Entrecôte", "Sunday": "Stek"
    }
    dagar_se = {
        "Monday": "Måndag", "Tuesday": "Tisdag", "Wednesday": "Onsdag",
        "Thursday": "Torsdag", "Friday": "Fredag", "Saturday": "Lördag", "Sunday": "Söndag"
    }
    idag_engelska = datetime.now().strftime('%A')
    return jsonify({
        'day': dagar_se.get(idag_engelska, "Idag"),
        'dish': vecko_meny.get(idag_engelska, "Meny")
    })

app = app

