import os
import sys
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

import ai_interpreter
import maps_search
import scraper
import formatter

# Load environment variables
load_dotenv()

app = FastAPI(title="Maps Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search Request Model
class SearchRequest(BaseModel):
    query: str
    location: Optional[str] = ""
    radius: Optional[float] = 5.0
    max_results: Optional[int] = 5
    min_rating: Optional[float] = 0.0
    apenas_abertos: Optional[bool] = False

# Global state to keep track of running tasks (for a simple implementation)
# In a real production app, use Celery or Redis for task queues.
task_status = {
    "is_running": False,
    "logs": [],
    "resultados": []
}

def log(message: str):
    print(message)
    task_status["logs"].append(message)

def get_location_coordinates(location: str):
    lat, lon = None, None
    if location:
        log(f"[*] Buscando coordenadas para: '{location}'...")
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="maps_bot_assistant")
        try:
            loc_data = geolocator.geocode(location)
            if loc_data:
                lat, lon = loc_data.latitude, loc_data.longitude
                log(f"    [+] Encontrado: {loc_data.address}")
            else:
                log(f"    [!] Localização '{location}' não encontrada.")
        except Exception as e:
            log(f"    [!] Erro na geolocalização: {e}")
    else:
        log("[*] Nenhuma localização digitada. Detectando localização atual pelo IP...")
        import urllib.request
        import json
        try:
            req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get("status") == "success":
                    lat, lon = data.get("lat"), data.get("lon")
                    city, region = data.get("city"), data.get("regionName")
                    log(f"    [+] Localização detectada: {city}, {region} (Lat: {lat}, Lon: {lon})")
                else:
                    log("    [!] Não foi possível detectar a localização pelo IP.")
        except Exception as e:
            log(f"    [!] Erro ao detectar localização: {e}")
    return lat, lon

def run_bot_logic(request: SearchRequest):
    global task_status
    task_status["is_running"] = True
    task_status["logs"] = []
    task_status["resultados"] = []
    
    try:
        log("[*] Iniciando processamento...")
        
        lat, lon = get_location_coordinates(request.location)

        log("[*] Consultando a Inteligência Artificial para otimizar o termo de busca...")
        
        # We don't overwrite sys.stdout here to avoid threading issues with FastAPI,
        # but the submodules might still print to console. Ideally they should take a logger.
        query_google = ai_interpreter.interpretar_busca(request.query)
        log(f"🧠 A IA otimizou sua busca para: '{query_google}'")

        log("[*] Abrindo navegador em segundo plano...")
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # For web API, run headless=True so it doesn't pop up on the server
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="pt-BR",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()
            
            try:
                log("[*] Pesquisando no Google Maps...")
                maps_search.iniciar_busca(page, query_google, lat=lat, lon=lon, radius=request.radius)
                
                log(f"[*] Extraindo até {request.max_results} resultados (Raio máx: {request.radius}km, Nota mín: {request.min_rating})...")
                resultados = scraper.extrair_dados_resultados(
                    page, 
                    max_results=request.max_results, 
                    min_rating=request.min_rating, 
                    origin_lat=lat, 
                    origin_lon=lon, 
                    max_radius=request.radius, 
                    apenas_abertos=request.apenas_abertos
                )
                task_status["resultados"] = resultados
                
            except Exception as e:
                log(f"[!] Erro durante navegação/raspagem: {e}")
            finally:
                log("[*] Fechando o navegador...")
                browser.close()

        if task_status["resultados"]:
            log(f"\n[✔] Sucesso! Encontrados {len(task_status['resultados'])} resultados válidos.")
        else:
            log("\n[!] Nenhum resultado foi encontrado (ou todos foram filtrados).")

    except Exception as e:
        log(f"\n[!] Erro fatal na execução: {e}")
    finally:
        task_status["is_running"] = False


@app.post("/api/search")
async def start_search(request: SearchRequest, background_tasks: BackgroundTasks):
    global task_status
    if task_status["is_running"]:
        raise HTTPException(status_code=400, detail="Search is already running. Please wait.")
    
    # Start the task in background
    background_tasks.add_task(run_bot_logic, request)
    return {"status": "started", "message": "Search job has been started."}

@app.get("/api/status")
async def get_status():
    global task_status
    return {
        "is_running": task_status["is_running"],
        "logs": task_status["logs"],
        "results": task_status["resultados"]
    }

@app.get("/api/export/{format}")
async def export_results(format: str):
    global task_status
    if not task_status["resultados"]:
        raise HTTPException(status_code=404, detail="No results to export.")
    
    if format not in ["csv", "json", "excel"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use csv, json, or excel.")
    
    file_mapping = {
        "csv": "resultados_busca.csv",
        "json": "resultados_busca.json",
        "excel": "resultados_busca.xlsx"
    }
    
    filename = file_mapping[format]
    
    # Create the file
    try:
        formatter.exportar_dados(task_status["resultados"], format)
        if os.path.exists(filename):
            return FileResponse(path=filename, filename=filename, media_type='application/octet-stream')
        else:
            raise HTTPException(status_code=500, detail="Failed to create export file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend directory for static files
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
os.makedirs(frontend_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
