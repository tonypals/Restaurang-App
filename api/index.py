import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from supabase import create_client, Client 
from datetime import datetime  # Denna saknades för menyn!

# 1. Ladda miljövariabler och initiera Supabase direkt
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 2. Definiera mappar korrekt för Vercel
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
static_dir = os.path.join(os.path.dirname(__file__), '../static')

# 3. Skapa Flask-appen EN gång
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/tasks')
def get_tasks():
    try:
        # Vi behåller 'tasks' som du ville
        response = supabase.table('tasks').select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"FEL VID HÄMTNING: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/toggle_task', methods=['POST'])
def toggle_task():
    try:
        data = request.json
        supabase.table('tasks').update({"is_completed": data['is_completed']}).eq("task_id", data['task_id']).execute()
        return jsonify({"status": "success"})
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

# Viktigt för Vercel
app = app