// ===== SUPABASE-KONFIGURATION =====
// Dessa hämtas från servern istället för att vara hårdkodade
let _supabase = null;

/**
 * Ladda Supabase-konfiguration från servern
 */
async function initSupabase() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        if (config.supabaseUrl && config.supabaseKey) {
            _supabase = supabase.createClient(config.supabaseUrl, config.supabaseKey);
            console.log('Supabase initialiserad');
        } else {
            console.warn('Supabase-konfiguration saknas');
        }
    } catch (error) {
        console.error('Kunde inte ladda Supabase-config:', error);
    }
}

// ===== GLOBALA VARIABLER =====
let currentRole = 'all';  // Vilken roll som är vald
let dbTasks = {};  // Håller reda på vilka uppgifter som är avbockade
let demoHour = null;  // Demo-timme
let demoMin = null;  // Demo-minut
let allTasks = [];  // Alla uppgifter från servern

/**
 * Ladda uppgifter från Flask API:et
 * Detta ersätter den hårdkodade datan!
 */
async function loadTasksFromServer() {
    try {
        console.log('Laddar uppgifter från servern...');
        const response = await fetch('/api/tasks');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        allTasks = data;
        console.log(`Laddade ${allTasks.length} uppgifter från servern`);
        
    } catch (error) {
        console.error('Kunde inte ladda uppgifter från servern:', error);
        alert('Fel: Kunde inte ladda uppgifter från servern. Se konsolen för detaljer.');
    }
}

/**
 * Ladda dagens meny från Flask API:et
 */
async function loadMenuFromServer() {
    try {
        console.log('Laddar meny från servern...');
        const response = await fetch('/api/menu');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        document.getElementById('todayTitle').innerText = `Dagens Special - ${data.day}`;
        document.getElementById('specialFood').innerText = data.dish;
        console.log('Meny laddad:', data);
        
    } catch (error) {
        console.error('Kunde inte ladda meny:', error);
        document.getElementById('todayTitle').innerText = 'Dagens Special';
        document.getElementById('specialFood').innerText = 'Kunde inte ladda meny';
    }
}

/**
 * Organisera uppgifter per period
 */
function organizeTasksByPeriod() {
    const periods = {
        morning: { label: '🌅 Morgonprep', range: '07:00 - 10:00', tasks: [] },
        lunch: { label: '🍲 Lunchrusning', range: '10:00 - 14:00', tasks: [] },
        afternoon: { label: '☀️ Eftermiddag', range: '14:00 - 18:00', tasks: [] },
        evening: { label: '🌆 Kväll', range: '18:00 - 22:00', tasks: [] },
        closing: { label: '🌙 Stängning', range: '22:00 - 01:00', tasks: [] }
    };
    
    allTasks.forEach(task => {
        if (periods[task.period]) {
            periods[task.period].tasks.push(task);
        }
    });
    
    return periods;
}

/**
 * Ladda avbockad-status från Supabase
 */
async function loadFromDb() {
    if (!_supabase) {
        console.warn('Supabase inte initialiserad än');
        updateUI();
        return;
    }
    
    try {
        const { data, error } = await _supabase.from('tasks').select('*');
        
        if (error) {
            console.error('Supabase-fel:', error);
            updateUI();
            return;
        }
        
        if (data) {
            dbTasks = {};
            data.forEach(t => { 
                dbTasks[t.task_id] = t.is_completed; 
            });
            console.log(`Laddade status för ${data.length} uppgifter från Supabase`);
        }
        
        updateUI();
    } catch (err) {
        console.error('Fel vid laddning från Supabase:', err);
        updateUI();
    }
}

/**
 * Toggla en uppgift (bocka av/av)
 */
async function toggleTask(id) {
    if (!_supabase) {
        console.warn('Supabase inte tillgänglig');
        return;
    }
    
    try {
        const newState = !dbTasks[id];
        dbTasks[id] = newState;
        
        updateUI();
        
        const { error } = await _supabase.from('tasks').upsert({ 
            task_id: id, 
            is_completed: newState, 
            updated_at: new Date().toISOString()
        });
        
        if (error) {
            console.error('Kunde inte spara till Supabase:', error);
        } else {
            console.log(`Uppgift ${id} uppdaterad till: ${newState}`);
        }
    } catch (err) {
        console.error('Fel vid toggle:', err);
    }
}

/**
 * Uppdatera hela UI:t
 */
function updateUI() {
    const now = new Date();
    
    // Uppdatera klockan
    const h = demoHour !== null ? demoHour : now.getHours();
    const m = demoMin !== null ? demoMin : now.getMinutes();
    document.getElementById('clockDisplay').innerText = 
        `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;

    // Bestäm period
    let pKey = 'afternoon';
    if(h >= 6 && h < 10) pKey = 'morning';
    else if(h >= 10 && h < 14) pKey = 'lunch';
    else if(h >= 14 && h < 18) pKey = 'afternoon';
    else if(h >= 18 && h < 22) pKey = 'evening';
    else if(h >= 22 || h < 6) pKey = 'closing';

    const periods = organizeTasksByPeriod();
    const p = periods[pKey];
    
    document.getElementById('periodTag').innerText = p.label;
    document.getElementById('listHeading').innerText = p.label;
    document.getElementById('timeRange').innerText = p.range;

    // Filtrera uppgifter
    const filtered = p.tasks.filter(t => currentRole === 'all' || t.role === currentRole);
    filtered.sort((a, b) => a.time.localeCompare(b.time));
    
    // Färgkodning
    const categoryColors = {
        'hygien': '#4caf50',
        'säkerhet': '#f44336',
        'prep': '#2196f3',
        'gäst': '#ff9800',
        'ekonomi': '#9c27b0',
        'drift': '#607d8b'
    };
    
    // Rendera uppgifter
    document.getElementById('taskList').innerHTML = filtered.map(t => {
        const borderColor = categoryColors[t.category] || '#ddd';
        return `
        <div class="task-item ${dbTasks[t.id] ? 'completed' : ''}" style="border-left-color: ${borderColor};">
            <input type="checkbox" ${dbTasks[t.id] ? 'checked' : ''} onchange="toggleTask('${t.id}')">
            <div class="task-info">
                <div style="font-weight:bold; font-size:16px;">${t.title}</div>
                <div class="task-meta">
                    <span>⏰ ${t.time}</span>
                    <span>👤 ${t.assignee}</span>
                    <span style="text-transform: capitalize;">📍 ${t.role}</span>
                    ${t.priority === 'high' ? '<span style="color:#f44336;">⚠️ Hög prio</span>' : ''}
                </div>
            </div>
        </div>
    `}).join('');

    // Statistik
    const done = filtered.filter(t => dbTasks[t.id]).length;
    document.getElementById('countDone').innerText = done;
    document.getElementById('countTotal').innerText = filtered.length;
    document.getElementById('percentDone').innerText = 
        filtered.length > 0 ? Math.round((done/filtered.length)*100)+'%' : '0%';
}

/**
 * Byt roll-filter
 */
function setRole(r) {
    currentRole = r;
    document.querySelectorAll('.role-btn').forEach(b => 
        b.classList.toggle('active', b.id === 'btn-'+r)
    );
    updateUI();
}

/**
 * Sätt demo-tid
 */
function setDemoTime(h, m) { 
    demoHour = h; 
    demoMin = m; 
    updateUI(); 
}

/**
 * Återställ till riktig tid
 */
function resetTime() { 
    demoHour = null; 
    demoMin = null; 
    updateUI(); 
}

// ===== INITIALISERING =====
async function init() {
    console.log('Startar app...');
    
    // Initiera Supabase först
    await initSupabase();
    
    // Ladda data från servern först
    await loadTasksFromServer();
    await loadMenuFromServer();
    
    // Sen ladda Supabase-status
    await loadFromDb();
    
    // Sätt upp realtidsuppdatering
    if (_supabase) {
        try {
            _supabase.channel('tasks-channel')
                .on('postgres_changes', { 
                    event: '*', 
                    schema: 'public', 
                    table: 'tasks' 
                }, loadFromDb)
                .subscribe();
            console.log('Realtidsuppdatering aktiverad');
        } catch (err) {
            console.error('Kunde inte aktivera realtid:', err);
        }
    }
    
    // Uppdatera klockan var 10:e sekund
    setInterval(updateUI, 10000);
    
    console.log('App startad!');
}

// Starta allt när sidan är laddad
init();