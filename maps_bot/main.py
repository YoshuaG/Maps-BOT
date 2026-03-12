import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import ai_interpreter
import maps_search
import scraper
import formatter

def main():
    load_dotenv() # Carrega chaves do .env, caso exista
    
    print("="*60)
    print(" 🤖 BÔT INTELIGENTE DE BUSCA - GOOGLE MAPS ".center(60))
    print("="*60)
    
    # PASSO 1: Receber entrada do usuário
    entrada = input("\nDigite o que deseja buscar (Ex: batata frita, conserto celular): ").strip()
    if not entrada:
        print("Entrada vazia. Encerrando o sistema.")
        sys.exit()
        
    limite_str = input("Quantos resultados deseja extrair? (Padrão: 5, Máx: 10): ").strip()
    try:
        limite = int(limite_str) if limite_str else 5
    except ValueError:
        limite = 5
        
    nota_min_str = input("Nota mínima desejada (Deixe em branco p/ ignorar o filtro): ").strip()
    try:
        nota_min = float(nota_min_str.replace(",", ".")) if nota_min_str else 0.0
    except ValueError:
        nota_min = 0.0

    print("\n" + "-"*60)
    print("[*] Processando sua solicitação...")
    
    # PASSO 2: IA interpreta a query (Integração com LLM)
    query_google = ai_interpreter.interpretar_busca(entrada)
    print(f"🧠 A IA otimizou sua busca original para: '{query_google}'")
    print("-"*60 + "\n")

    resultados = []
    
    # PASSO 3 ao PASSO 9: Playwright (Automação / Scraping dinâmico)
    with sync_playwright() as p:
        # Iniciamos o browser de forma visual. Headless=False para acompanharmos o fluxo (Pode alterar para True futuramente)
        # Passamos um locale pt-BR para garantir resultados em português e user_agent humanizado.
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        try:
            # Passo 3 a 5 (Abrir maps e Pesquisar)
            maps_search.iniciar_busca(page, query_google)
            
            # Passo 6 a 9 (Iterar cards lado esquerdo, extrair dados e limitar)
            resultados = scraper.extrair_dados_resultados(page, max_results=limite, min_rating=nota_min)
            
        except Exception as e:
            print(f"[!] Erro crítico na automação do Playwright: {e}")
        finally:
            print("[*] Fechando o navegador...")
            browser.close()

    # PASSO 10: Formatar e Exibir/Exportar Resposta de maneira amigável
    formatter.exibir_no_terminal(resultados)
    
    if resultados:
        print("\n" + "-"*60)
        exportar = input("Deseja exportar os resultados? (json / csv / excel / n): ").strip()
        if exportar.lower() not in ['n', 'nao', 'não', '']:
            formatter.exportar_dados(resultados, exportar)
            
    print("\n[✔] Processo finalizado com sucesso!")

if __name__ == "__main__":
    main()
