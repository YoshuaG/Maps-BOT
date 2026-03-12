import time
from playwright.sync_api import Page

def extrair_dados_resultados(page: Page, max_results: int = 10, min_rating: float = 0.0, origin_lat: float | None = None, origin_lon: float | None = None, max_radius: float = 5.0, apenas_abertos: bool = False) -> list:
    """
    Itera sobre os resultados carregados e extrai nome, telefone, endereço, avaliação e link.
    """
    resultados = []
    
    print(f"[*] Iniciando extração de até {max_results} locais...")
    
    # Localizar os links de resultados que geralmente ficam na div com role feed
    cards = page.locator('div[role="feed"] > div > div > a')
    count = cards.count()
    
    print(f"[*] Encontrados {count} locais na lista atual do Maps.")
    
    limit = count
    
    # Precisamos controlar quantos foram 'adicionados' com sucesso, e não apenas iterados
    adicionados = 0
    
    for i in range(limit):
        if adicionados >= max_results:
            break
            
        try:
            print(f"[*] Processando estabelecimento {i+1} de {limit}...")
            
            # Recaptura o locator dinamicamente caso a página tenha mudado
            card = page.locator('div[role="feed"] > div > div > a').nth(i)
            link = card.get_attribute("href") or "Link indisponível"
            
            # Clicar no local para abrir as informações detalhadas ao lado
            card.click()
            time.sleep(3) # Aguarda painel lateral de detalhes carregar
            
            # ====== EXTRAÇÃO DE DADOS ======
            
            # 1. Nome do Estabelecimento (h1 na página de detalhes)
            # Como Playwright apontou que existem 3 h1, vamos usar a classe principal ou o '.last'
            nome_loc = page.locator('h1.DUwDvf')
            if nome_loc.count() == 0:
                nome_loc = page.locator('h1').last
                
            nome = nome_loc.inner_text().strip() if nome_loc.count() > 0 else "N/A"
            
            # 2. Avaliação / Nota
            nota_loc = page.locator('div[font-display="large"]') # Playwright acha pela fonte da nota
            
            nota = 0.0
            if nota_loc.count() > 0:
                nota_txt = nota_loc.first.inner_text().strip().replace(",", ".")
                try:
                    nota = float(nota_txt)
                except ValueError:
                    nota = 0.0
            else:
                # Tenta outra classe no google maps
                nota_alt_loc = page.locator('div.fontDisplayLarge')
                if nota_alt_loc.count() > 0:
                    nota_txt = nota_alt_loc.first.inner_text().strip().replace(",", ".")
                    try:
                        nota = float(nota_txt)
                    except ValueError:
                        pass
                
            if nota > 0 and nota < min_rating:
                print(f"    [-] Pulando '{nome}' (Nota: {nota}) - Abaixo do mínimo exigido ({min_rating}).")
                continue
                
            # ====== EXTRAÇÃO DO HORÁRIO / STATUS ABERTO ======
            horario_loc = page.locator('span[class*="t39EBf"]') # Classe comum dos horários (Aberto/Fechado)
            status_aberto = "Desconhecido"
            
            if horario_loc.count() > 0:
                # O Google às vezes separa em várias tags, juntamos os textos
                status_aberto = " ".join(horario_loc.first.inner_text().split()).replace('\n', ' ')
            else:
                # Segunda tentativa caso a classe mude
                alt_loc = page.locator('div[aria-label^="Ocultar horário"]')
                if alt_loc.count() > 0:
                    status_aberto = " ".join(alt_loc.first.inner_text().split()).replace('\n', ' ')

            if apenas_abertos and "Fechado" in status_aberto:
                print(f"    [-] Pulando '{nome}' - Está Fechado no momento.")
                continue
                
            # ====== EXTRAÇÃO DE COORDENADAS E DISTÂNCIA ======
            distancia_km = None
            if origin_lat and origin_lon and max_radius and link != "Link indisponível":
                import re
                from geopy.distance import geodesic
                # Tenta extrair coordenadas no link (ex: !3d-23.5!4d-46.6 ou @-23.5,-46.6)
                match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', link)
                if not match:
                    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', link)
                
                if match:
                    dest_lat = float(match.group(1))
                    dest_lon = float(match.group(2))
                    distancia_km = geodesic((origin_lat, origin_lon), (dest_lat, dest_lon)).kilometers
                    
                    if distancia_km > max_radius:
                        print(f"    [-] Pulando '{nome}' (Distância: {distancia_km:.1f}km) - Fora do raio de {max_radius}km.")
                        continue
                        
            # 3. Endereço
            end_loc = page.locator('button[data-item-id="address"]')
            endereco = end_loc.inner_text() if end_loc.count() > 0 else "Não informado"
            
            # 4. Telefone
            tel_loc = page.locator('button[data-item-id^="phone:tel:"]')
            telefone = tel_loc.inner_text() if tel_loc.count() > 0 else "Sem telefone"
            
            dados = {
                "nome": nome.replace('\n', ' '),
                "telefone": telefone.replace('\n', ' '),
                "endereco": endereco.replace('\n', ', '),
                "avaliacao": nota,
                "status_aberto": status_aberto,
                "link": link
            }
            if distancia_km is not None:
                dados["distancia_km"] = distancia_km
                
            resultados.append(dados)
            adicionados += 1
            dist_print = f" | Dist: {distancia_km:.1f}km" if distancia_km is not None else ""
            print(f"    [+] Extraído: {nome} | Nota: {nota} | Tel: {telefone}{dist_print}")
            
        except Exception as e:
            print(f"    [!] Erro ao processar o card {i+1}: {e}")
            
    return resultados
