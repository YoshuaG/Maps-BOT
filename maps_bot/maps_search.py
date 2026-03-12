import time
from playwright.sync_api import Page

def iniciar_busca(page: Page, query: str, lat: float | None = None, lon: float | None = None, radius: float = 5.0):
    """
    Acessa o Google Maps diretamente com a pesquisa na URL e aguarda os resultados aparecerem.
    """
    import urllib.parse
    import math
    
    print(f"[*] Abrindo Google Maps e pesquisando por: '{query}'...")
    
    # Faz o encode da query para URL (Ex: "batata frita" -> "batata+frita")
    query_encoded = urllib.parse.quote_plus(query)
    
    if lat is not None and lon is not None:
        # Define um zoom com base no raio (Aproximado)
        # 1km -> ~15.5z, 5km -> ~14z, 10km -> ~13z, 50km -> ~10.5z
        zoom = 14
        if radius > 0:
            zoom = max(10, min(18, int(15 - math.log2(radius))))
            
        url = f"https://www.google.com/maps/search/{query_encoded}/@{lat},{lon},{zoom}z"
    else:
        url = f"https://www.google.com/maps/search/{query_encoded}"
        
    try:
        page.goto(url, timeout=60000)
    except Exception as e:
        print(f"[!] Erro ao abrir a URL de busca: {e}")
        raise
    
    print("[*] Aguardando o carregamento dos resultados na barra lateral...")
    
    # Espera a barra lateral (feed) inicial de resultados aparecer
    try:
        page.wait_for_selector('div[role="feed"]', timeout=20000)
        time.sleep(3) # Tempo extra para os primeiros cards renderizarem por completo
        
        # Faz um pequeno scroll para garantir que a lista carregou mais de 2 itens
        feed = page.locator('div[role="feed"]')
        feed.hover()
        page.mouse.wheel(0, 1500)
        time.sleep(2)
    except Exception as e:
        print("[!] Não foi possível carregar a lista de resultados. Talvez a busca não tenha gerado uma lista em formato de barra lateral.")
