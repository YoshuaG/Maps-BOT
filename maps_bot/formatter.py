import json
import pandas as pd
from colorama import init, Fore, Style

# Inicializa o colorama para dar cor no terminal (Windows/Linux)
init(autoreset=True)

def exibir_no_terminal(resultados: list):
    """
    Recebe os locais em formato de lista de dicionários e exibe no CLI organizados.
    """
    if not resultados:
        print(Fore.YELLOW + "\nNenhum resultado foi selecionado (ou os resultados não atingiram os critérios de filtro).\n")
        return
        
    print(Style.BRIGHT + Fore.CYAN + "\n" + "="*60)
    print(Style.BRIGHT + Fore.CYAN + "📍 RESULTADOS ENCONTRADOS 📍".center(60))
    print(Style.BRIGHT + Fore.CYAN + "="*60 + "\n")
    
    for i, res in enumerate(resultados, 1):
        print(f"{Fore.GREEN}{i}️⃣  {Style.BRIGHT}{res['nome']}")
        print(f"   📞 {Fore.YELLOW}Telefone:{Style.RESET_ALL} {res['telefone']}")
        print(f"   🏠 {Fore.YELLOW}Endereço:{Style.RESET_ALL} {res['endereco']}")
        print(f"   ⭐ {Fore.YELLOW}Avaliação:{Style.RESET_ALL} {res['avaliacao']}")
        print(f"   🔗 {Fore.YELLOW}Link Maps:{Style.RESET_ALL} {res['link'][:80]}...")
        print("-" * 60)

def exportar_dados(resultados: list, formato: str):
    """
    Exporta a lista de dicionários para JSON, CSV ou Excel.
    """
    if not resultados:
        return
        
    formato = formato.lower().strip()
    try:
        if formato == 'json':
            # Usa ensure_ascii=False para manter acentuação correta
            pd.DataFrame(resultados).to_json("resultados_busca.json", orient="records", force_ascii=False, indent=4)
            print(Fore.GREEN + "[*] Dados salvos com sucesso em: resultados_busca.json")
            
        elif formato == 'csv':
            # Usa utf-8-sig para Microsoft Excel abrir o CSV com acentos direitinho
            pd.DataFrame(resultados).to_csv("resultados_busca.csv", index=False, encoding="utf-8-sig")
            print(Fore.GREEN + "[*] Dados salvos com sucesso em: resultados_busca.csv")
            
        elif formato == 'excel':
            pd.DataFrame(resultados).to_excel("resultados_busca.xlsx", index=False)
            print(Fore.GREEN + "[*] Dados salvos com sucesso em: resultados_busca.xlsx")
            
        elif formato in ('não', 'nao', 'n', ''):
            pass
        else:
            print(Fore.RED + "[!] Formato desconhecido. Não foi possível exportar. Use: json, csv ou excel.")
    except Exception as e:
        print(Fore.RED + f"[!] Erro ao tentar exportar arquivos: {e}")
