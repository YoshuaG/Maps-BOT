# 🗺️ Google Maps Intelligent Scraper Bot

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Playwright](https://img.shields.io/badge/Automation-Playwright-green)
![AI](https://img.shields.io/badge/AI-GPT%20Interpreter-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

Um **bot inteligente de automação para o Google Maps** capaz de pesquisar estabelecimentos automaticamente, interpretar buscas em linguagem natural com Inteligência Artificial e extrair dados comerciais estruturados.

Ideal para **prospecção de clientes, marketing local, análise de mercado e criação de bases de dados comerciais**.

---

# 📌 Visão Geral

O **Google Maps Intelligent Scraper Bot** automatiza pesquisas dentro do Google Maps e coleta dados relevantes dos estabelecimentos encontrados.

O usuário simplesmente descreve o que procura:

```
restaurantes que vendem batata frita perto de mim
```

ou

```
clínicas odontológicas em São Paulo
```

A Inteligência Artificial interpreta essa frase e transforma em uma **consulta otimizada para o Google Maps**, permitindo que o bot encontre resultados de forma muito mais eficiente.

Depois disso o sistema extrai automaticamente:

* 🏢 Nome do estabelecimento
* ⭐ Avaliação
* 📍 Endereço
* ☎️ Telefone
* 🕒 Status (aberto ou fechado)
* 📏 Distância do ponto de busca

Todos os dados são organizados e exportados em:

* **Excel (.xlsx)**
* **CSV**
* **JSON**

---

# 🖥️ Interface do Sistema

### Tela Principal

![Interface](docs/images/interface.png)

### Extração de Dados

![Resultados](docs/images/results.png)

---

# 🚀 Principais Funcionalidades

✔ Pesquisa automática no Google Maps
✔ Interpretação de buscas com IA
✔ Extração automática de dados comerciais
✔ Filtro de distância por raio
✔ Detecção de estabelecimentos fechados
✔ Exportação em múltiplos formatos
✔ Interface moderna com Dark Mode
✔ Execução estável usando Playwright

---

# 🧠 Tecnologias Utilizadas

## Python

Linguagem principal do projeto, utilizada para automação, análise de dados e integração com IA.

---

## Playwright

Motor de automação web criado pela Microsoft.

Vantagens:

* extremamente rápido
* melhor controle de páginas dinâmicas
* menos erros de automação
* suporte a navegação assíncrona

---

## Inteligência Artificial (g4f)

Utilizado para interpretar a busca do usuário.

Exemplo:

Entrada do usuário:

```
tem algum lugar que venda torta perto de mim?
```

Consulta otimizada gerada pela IA:

```
restaurante torta perto de mim
```

Isso melhora drasticamente a qualidade da busca no Maps.

---

## Geopy

Utilizado para cálculos geográficos.

Permite:

* converter endereços em latitude/longitude
* calcular distância real entre pontos
* aplicar filtros por raio de busca

---

## CustomTkinter

Framework de interface gráfica moderno baseado em Tkinter.

Recursos:

* interface moderna
* modo escuro
* cantos arredondados
* melhor experiência visual

---

## Pandas + Openpyxl

Usados para organizar os dados e exportar arquivos Excel estruturados.

Isso evita problemas comuns de codificação que acontecem em arquivos CSV.

---

# ⚙️ Instalação

## 1. Clone o projeto

```
git clone https://github.com/seu-usuario/google-maps-bot.git
```

```
cd google-maps-bot
```

---

## 2. Criar ambiente virtual (recomendado)

```
python -m venv venv
```

Windows:

```
venv\Scripts\activate
```

Linux / Mac:

```
source venv/bin/activate
```

---

## 3. Instalar dependências

```
pip install -r requirements.txt
```

---

## 4. Instalar navegador do Playwright

```
playwright install chromium
```

---

## 5. Executar o sistema

```
python maps_bot/gui.py
```

---

# 🧩 Estrutura do Projeto

```
google-maps-bot
│
├── maps_bot
│   ├── gui.py
│   ├── ai_interpreter.py
│   ├── maps_search.py
│   ├── scraper.py
│   ├── formatter.py
│
├── docs
│   ├── images
│
├── requirements.txt
├── README.md
```

---

# 🔄 Fluxo do Sistema

1️⃣ Usuário digita o que deseja pesquisar
2️⃣ IA interpreta a frase
3️⃣ Sistema gera consulta otimizada para o Google Maps
4️⃣ Playwright abre o navegador automaticamente
5️⃣ O scraper percorre os resultados
6️⃣ Dados são coletados e filtrados
7️⃣ Resultados são exportados para Excel / CSV / JSON

---

# 📊 Exemplos de Uso

## Prospecção Comercial

Encontrar restaurantes de uma cidade para oferecer serviços.

```
restaurantes hamburguer natal rn
```

---

## Marketing Local

Criar lista de contatos de clínicas odontológicas.

```
clinicas odontologicas recife
```

---

## Pesquisa de Mercado

Mapear concorrentes em determinada região.

```
academias em fortaleza
```

---

# 🛣️ Roadmap

### Versão 1.0

* Automação do Google Maps
* Extração de dados
* Exportação para Excel
* Interface gráfica

### Versão 1.5

* Filtros avançados
* Exportação para banco de dados
* Melhorias de desempenho

### Versão 2.0

* API REST
* Dashboard web
* Processamento em lote
* Integração com CRM

### Versão 3.0

* SaaS completo
* Painel online
* Multiusuários
* Sistema de créditos

---

# 💼 Versão Comercial

Este projeto também pode ser transformado em um **produto comercial**.

Possíveis modelos:

* software de geração de leads
* ferramenta de marketing local
* plataforma SaaS de prospecção
* sistema de análise de mercado

Possíveis recursos premium:

* exportação ilimitada
* múltiplas cidades simultâneas
* automação em massa
* API para integração

---

# 🤝 Contribuição

Contribuições são bem-vindas!

Você pode ajudar com:

* melhorias de código
* correção de bugs
* novas funcionalidades
* otimização de performance

---

# 📄 Licença

Este projeto está sob a licença **MIT**.

Você pode usar, modificar e distribuir livremente.

---

# ⭐ Apoie o Projeto

Se este projeto foi útil para você:

⭐ Deixe uma estrela no repositório
🍴 Faça um fork
📢 Compartilhe com outras pessoas
