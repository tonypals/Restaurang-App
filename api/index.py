import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
# HÄR ÄR FIXEN: Vi måste importera create_client specifikt
from supabase import create_client, Client 

# Detta hjälper Flask att hitta rätt mapp på Vercel
app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../Static')

# Ladda .env-filen
load_dotenv()




url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# LÄGG TILL DETTA FÖR ATT TESTA:
print(f"Hittad URL: {url}")
print(f"Hittad KEY: {key}")

if not url:
    print("FEL: Kunde inte ladda SUPABASE_URL från .env!")
app = Flask(__name__)

# Hämta variabler
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Nu kommer create_client att fungera!
supabase: Client = create_client(url, key)

# Hitta rätt mappar
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
static_dir = os.path.join(os.path.dirname(__file__), '../static')
data_dir = os.path.join(os.path.dirname(__file__), '../data')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route('/')
def home():
    """Huvudsida - renderar bara HTML-templaten"""
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    """Admin-sida för managern"""
    return render_template('admin.html')

@app.route('/api/tasks')
def get_tasks():
    try:
        # Detta anropar Supabase
        response = supabase.table('tasks').select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"FEL VID HÄMTNING: {e}") # Detta skriver ut felet i din terminal
        return jsonify({"error": str(e)}), 500

@app.route('/api/toggle_task', methods=['POST'])
def toggle_task():
    """Uppdaterar om en uppgift är klar eller inte i databasen"""
    try:
        data = request.json
        supabase.table('tasks').update({"is_completed": data['is_completed']}).eq("task_id", data['task_id']).execute()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config')
def get_config():
    """
    Hämta Supabase-konfiguration från miljövariabler
    Detta gör att vi inte behöver hårdkoda känsliga nycklar
    """
    return jsonify({
        'supabaseUrl': os.getenv('SUPABASE_URL', ''),
        'supabaseKey': os.getenv('SUPABASE_KEY', '')
    })

@app.route('/api/menu')
def get_menu():
    """
    API-endpoint för dagens meny
    Beräknar vilken dag det är och returnerar rätt maträtt
    """
    # Matsedel - lätt att ändra här!
    vecko_meny = {
        "Monday": "Pannbiff med gräddsås och potatismos",
        "Tuesday": "Raggmunk med stekt fläsk och lingon",
        "Wednesday": "Chili con Carne serveras med ris",
        "Thursday": "Köttbullar med potatismos och gräddsås",
        "Friday": "Kålpudding med gräddsås och potatismos",
        "Saturday": "Grillad Entrecôte med bearnaise",
        "Sunday": "Söndagsstek med inlagd gurka"
    }
    
    # Svenska dagnamn
    dagar_se = {
        "Monday": "Måndag", 
        "Tuesday": "Tisdag", 
        "Wednesday": "Onsdag",
        "Thursday": "Torsdag", 
        "Friday": "Fredag", 
        "Saturday": "Lördag", 
        "Sunday": "Söndag"
    }
    
    # Räkna ut dagens dag
    idag_engelska = datetime.now().strftime('%A')
    dag_namn = dagar_se.get(idag_engelska, "Idag")
    dagens_ratt = vecko_meny.get(idag_engelska, "Se menyn på plats")
    
    return jsonify({
        'day': dag_namn,
        'dish': dagens_ratt
    })

# För Vercel deployment
app = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)