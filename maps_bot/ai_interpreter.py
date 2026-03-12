import os
from g4f.client import Client
from dotenv import load_dotenv

load_dotenv()

def interpretar_busca(usuario_input: str) -> str:
    """
    Usa IA para interpretar a entrada do usuário e gerar a melhor query para o Google Maps.
    """
    try:
        prompt = f"""
        Você é um assistente especialista em SEO local e buscas no Google Maps.
        Seu objetivo é transformar o texto livre do usuário no melhor termo de pesquisa possível para encontrar estabelecimentos no Google Maps.
        
        Regras:
        - Responda APENAS com o termo de busca final, sem aspas, sem explicacoes.
        - Não use pontuação final.
        - Não inclua NENHUM texto promocional ou links na resposta.
        
        Exemplos de entrada -> saída:
        "quero comer fritas" -> "batata frita restaurante"
        "dor de cabeca" -> "farmácia"
        "onde tem gasolina barata" -> "posto de gasolina"
        
        Entrada atual do usuário: "{usuario_input}"
        """
        
        from g4f.client import Client
        
        print("[*] Interpretando busca com inteligência artificial...")
        client = Client()
        
        # Chamando de forma que a lib distribua para os provedores gratuitos disponíveis
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        query = response.choices[0].message.content.strip().replace('"', '')

        
        # A API gratuita g4f às vezes adiciona textos promocionais, quebras de linha ou links de proxy.
        # Vamos pegar apenas a primeira linha útil:
        if "\n" in query:
            query = query.split("\n")[0].strip()
            
        # Limpar mensagens patrocinadas ou placeholders caso existam na mesma linha
        lower_query = query.lower()
        stopwords = ["http", "://", "need proxies", "here is", "sure", "o termo é"]
        
        for word in stopwords:
            if word in lower_query:
                # Corta a string antes da interrupção (case-insensitive find)
                idx = lower_query.find(word)
                if idx != -1:
                    query = query[:idx].strip()
                    break
            
        return query
    except Exception as e:
        print(f"[!] Erro na IA: {e}")
        # Lógica de fallback simples
        if "comer" in usuario_input.lower() or "fome" in usuario_input.lower() or "jantar" in usuario_input.lower():
            return f"{usuario_input} restaurante"
        return usuario_input
