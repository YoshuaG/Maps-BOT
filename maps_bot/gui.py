import os
import sys
import threading
import webbrowser
import tkinter as tk
from PIL import Image, ImageEnhance
import customtkinter as ctk
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import ai_interpreter
import maps_search
import scraper
import formatter

# Configuração Padrão do Tema CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BOT INTELIGENTE DE BUSCA - GOOGLE MAPS")
        self.geometry("800x600")
        self.minsize(800, 600)

        # Configurar pasta de assets para os GIFs
        self.assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        
        self.idle_gif_path = os.path.join(self.assets_dir, "idle.gif")
        self.search_gif_path = os.path.join(self.assets_dir, "search.gif")
        
        self.current_gif_frames = []
        self.gif_frame_idx = 0
        self.gif_after_id = None

        self.is_running = False
        self.resultados = []
        
        # Background Image (Fosco)
        bg_path = os.path.join(self.assets_dir, "background.jpg")
        if os.path.exists(bg_path):
            try:
                bg_pil = Image.open(bg_path).convert("RGBA")
                enhancer = ImageEnhance.Brightness(bg_pil)
                bg_pil = enhancer.enhance(0.3) # 30% do brilho (Efeito Fosco Escurecido)
                
                # Tamanho HD para preencher as laterais sob os frames
                bg_img = ctk.CTkImage(light_image=bg_pil, size=(1920, 1080))
                self.bg_label = ctk.CTkLabel(self, text="", image=bg_img)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            except Exception as e:
                print(f"Erro ao carregar fundo: {e}")

        self.create_widgets()

    def create_widgets(self):
        # Frame Principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ---- Seção Superior (Entradas) ----
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.input_frame, text="O que deseja buscar? (Ex: hamburgueria, conserto celular):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0))
        self.entry_query = ctk.CTkEntry(self.input_frame, width=400, placeholder_text="Digite aqui...")
        self.entry_query.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="Localização (Ex: Av Paulista, SP):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 0))
        self.entry_location = ctk.CTkEntry(self.input_frame, width=400, placeholder_text="Deixe vazio para busca global...")
        self.entry_location.grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="Raio Máx (km):").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
        self.entry_radius = ctk.CTkEntry(self.input_frame, width=100)
        self.entry_radius.insert(0, "5")
        self.entry_radius.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="Qtd. Máxima de Resultados:").grid(row=4, column=1, sticky="w", padx=10, pady=(10, 0))
        self.entry_max_results = ctk.CTkEntry(self.input_frame, width=130)
        self.entry_max_results.insert(0, "5")
        self.entry_max_results.grid(row=5, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.input_frame, text="Nota Mínima (0 a 5.0):").grid(row=4, column=2, sticky="w", padx=10, pady=(10, 0))
        self.entry_min_rating = ctk.CTkEntry(self.input_frame, width=100)
        self.entry_min_rating.insert(0, "0.0")
        self.entry_min_rating.grid(row=5, column=2, sticky="w", padx=10, pady=5)
        
        self.var_abertos = ctk.BooleanVar(value=False)
        self.checkbox_abertos = ctk.CTkCheckBox(self.input_frame, text="Apenas locais abertos agora", variable=self.var_abertos)
        self.checkbox_abertos.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        self.btn_search = ctk.CTkButton(self.input_frame, text="INICIAR BUSCA", font=ctk.CTkFont(size=14, weight="bold"), command=self.start_search_thread)
        self.btn_search.grid(row=1, column=3, rowspan=6, sticky="nsew", padx=20, pady=10)

        # Espaço reservado para o GIF de Loading/Idle
        self.lbl_gif = ctk.CTkLabel(self.input_frame, text="")
        self.lbl_gif.grid(row=1, column=4, rowspan=6, sticky="nsew", padx=20, pady=10)
        
        # Iniciar GIF Idle
        self.play_gif(self.idle_gif_path)

        # ---- PanedWindow (Para permitir redimensionamento) ----
        self.paned_window = tk.PanedWindow(self.main_frame, orient="vertical", bg="#2b2b2b", bd=0, sashwidth=6, sashrelief="flat")
        self.paned_window.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame Superior (Logs)
        self.pane_top = ctk.CTkFrame(self.paned_window, fg_color="transparent")
        self.paned_window.add(self.pane_top, minsize=100)
        
        # Frame Inferior (Resultados)
        self.pane_bottom = ctk.CTkFrame(self.paned_window, fg_color="transparent")
        self.paned_window.add(self.pane_bottom, minsize=150)

        # ---- Seção do Meio (Logs do Processo) ----
        ctk.CTkLabel(self.pane_top, text="Console de Execução:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0,5))
        self.textbox_log = ctk.CTkTextbox(self.pane_top, corner_radius=5)
        self.textbox_log.pack(fill="both", expand=True)
        self.textbox_log.configure(state="disabled")

        # ---- Seção de Resultados na Tela ----
        ctk.CTkLabel(self.pane_bottom, text="Resultados Encontrados:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10,5))
        self.results_frame = ctk.CTkScrollableFrame(self.pane_bottom, corner_radius=5)
        self.results_frame.pack(fill="both", expand=True)

        # ---- Seção Inferior (Resultados e Exportação) ----
        self.export_frame = ctk.CTkFrame(self.main_frame)
        self.export_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.export_frame, text="Exportar Resultados:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
        
        self.btn_export_csv = ctk.CTkButton(self.export_frame, text="Exportar CSV", width=120, state="disabled", command=lambda: self.exportar_resultados("csv"))
        self.btn_export_csv.pack(side="left", padx=5)

        self.btn_export_json = ctk.CTkButton(self.export_frame, text="Exportar JSON", width=120, state="disabled", command=lambda: self.exportar_resultados("json"))
        self.btn_export_json.pack(side="left", padx=5)

        self.btn_export_excel = ctk.CTkButton(self.export_frame, text="Exportar Excel", width=120, state="disabled", command=lambda: self.exportar_resultados("excel"))
        self.btn_export_excel.pack(side="left", padx=5)
        
        # Botão para corrigir Playwright
        self.btn_fix_playwright = ctk.CTkButton(self.export_frame, text="Corrigir Navegador", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=self.fix_playwright)
        self.btn_fix_playwright.pack(side="right", padx=10)

    def log(self, message):
        """Adiciona uma mensagem ao bloco de log e rola para o final."""
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    def toggle_inputs(self, state):
        """Habilita ou desabilita as entradas enquanto roda."""
        self.entry_query.configure(state=state)
        self.entry_location.configure(state=state)
        self.entry_radius.configure(state=state)
        self.entry_max_results.configure(state=state)
        self.entry_min_rating.configure(state=state)
        self.checkbox_abertos.configure(state=state)
        if state == "normal":
            self.btn_search.configure(state="normal", text="INICIAR BUSCA")
        else:
            self.btn_search.configure(state="disabled", text="BUSCANDO...")

    def toggle_export_buttons(self, enable=True):
        state = "normal" if enable else "disabled"
        self.btn_export_csv.configure(state=state)
        self.btn_export_json.configure(state=state)
        self.btn_export_excel.configure(state=state)

    def start_search_thread(self):
        query = self.entry_query.get().strip()
        location = self.entry_location.get().strip()

        if not query:
            self.log("[!] Aviso: Por favor, digite o que deseja buscar.")
            return

        try:
            radius = float(self.entry_radius.get().replace(",", "."))
        except ValueError:
            radius = 5.0
            self.entry_radius.delete(0, "end")
            self.entry_radius.insert(0, "5")

        try:
            max_results = int(self.entry_max_results.get())
        except ValueError:
            max_results = 5
            self.entry_max_results.delete(0, "end")
            self.entry_max_results.insert(0, "5")

        try:
            min_rating = float(self.entry_min_rating.get().replace(",", "."))
        except ValueError:
            min_rating = 0.0
            self.entry_min_rating.delete(0, "end")
            self.entry_min_rating.insert(0, "0.0")

        # Captura o valor da checkbox (Apenas locais abertos)
        apenas_abertos = self.var_abertos.get()

        if self.is_running:
            return

        self.is_running = True
        self.resultados = []
        self.toggle_inputs("disabled")
        self.toggle_export_buttons(False)
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("0.0", "end") # Limpar logs anteriores
        self.textbox_log.configure(state="disabled")
        
        # Limpar painel de resultados visuais
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Atualizar gif
        self.play_gif(self.search_gif_path)

        # Inicia a thread para não travar a interface
        thread = threading.Thread(target=self.run_bot_logic, args=(query, location, radius, max_results, min_rating, apenas_abertos), daemon=True)
        thread.start()

    def run_bot_logic(self, entrada, location, radius, max_results, min_rating, apenas_abertos):
        try:
            load_dotenv()
            
            self.log("[*] Iniciando processamento...")
            
            # Parte 1: Transformar localização em coordenadas
            lat, lon = None, None
            if location:
                self.log(f"[*] Buscando coordenadas para: '{location}'...")
                from geopy.geocoders import Nominatim
                geolocator = Nominatim(user_agent="maps_bot_assistant")
                try:
                    loc_data = geolocator.geocode(location)
                    if loc_data:
                        lat, lon = loc_data.latitude, loc_data.longitude
                        self.log(f"    [+] Encontrado: {loc_data.address}")
                    else:
                        self.log(f"    [!] Localização '{location}' não encontrada.")
                except Exception as e:
                    self.log(f"    [!] Erro na geolocalização: {e}")
            else:
                self.log("[*] Nenhuma localização digitada. Detectando localização atual pelo IP...")
                import urllib.request
                import json
                try:
                    req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode())
                        if data.get("status") == "success":
                            lat, lon = data.get("lat"), data.get("lon")
                            city, region = data.get("city"), data.get("regionName")
                            self.log(f"    [+] Localização detectada: {city}, {region} (Lat: {lat}, Lon: {lon})")
                        else:
                            self.log("    [!] Não foi possível detectar a localização pelo IP.")
                except Exception as e:
                    self.log(f"    [!] Erro ao detectar localização: {e}")

            self.log("[*] Consultando a Inteligência Artificial para otimizar o termo de busca...")
            
            # Redirecionar stdout temporariamente para capturar prints internos (opcional)
            # Mas os módulos atuais tem prints, vamos criar um wrapper para stdout
            
            class StdoutRedirector:
                def __init__(self, app_log_func):
                    self.app_log_func = app_log_func
                def write(self, s):
                    if s.strip():
                        # Use call_after se der erro de thread no Tk
                        app.after(0, self.app_log_func, s.strip())
                def flush(self):
                    pass
            
            old_stdout = sys.stdout
            sys.stdout = StdoutRedirector(self.log)

            query_google = ai_interpreter.interpretar_busca(entrada)
            self.log(f"🧠 A IA otimizou sua busca para: '{query_google}'")

            # --- PLAYWRIGHT ---
            self.log("[*] Abrindo navegador em segundo plano...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="pt-BR",
                    viewport={"width": 1280, "height": 720}
                )
                page = context.new_page()
                
                try:
                    self.log("[*] Pesquisando no Google Maps...")
                    maps_search.iniciar_busca(page, query_google, lat=lat, lon=lon, radius=radius)
                    
                    self.log(f"[*] Extraindo até {max_results} resultados (Raio máx: {radius}km, Nota mín: {min_rating})...")
                    self.resultados = scraper.extrair_dados_resultados(page, max_results=max_results, min_rating=min_rating, origin_lat=lat, origin_lon=lon, max_radius=radius, apenas_abertos=apenas_abertos)
                    
                except Exception as e:
                    self.log(f"[!] Erro durante navegação/raspagem: {e}")
                finally:
                    self.log("[*] Fechando o navegador...")
                    browser.close()
                    
            sys.stdout = old_stdout # Restaurar stdout original

            if self.resultados:
                self.log(f"\n[✔] Sucesso! Encontrados {len(self.resultados)} resultados válidos.")
                self.after(0, self.toggle_export_buttons, True)
                
                # Exibir resultados na interface gráfica em vez de só no log
                self.after(0, self.display_results_in_gui)
            else:
                self.log("\n[!] Nenhum resultado foi encontrado (ou todos foram filtrados).")

        except Exception as e:
            self.log(f"\n[!] Erro fatal na execução: {e}")
        finally:
            self.is_running = False
            self.after(0, lambda: self.toggle_inputs("normal"))
            self.after(0, lambda: self.play_gif(self.idle_gif_path))

    def display_results_in_gui(self):
        """Popula o frame de resultados com os itens encontrados."""
        for i, item in enumerate(self.resultados, 1):
            # A extração retorna 'nome', 'avaliacao' e 'telefone', baseado em scraper.py
            nome = item.get("nome", "N/A")
            nota = item.get("avaliacao", "N/A")
            tel = item.get("telefone", "Sem telefone")
            onda = item.get("status_aberto", "Desconhecido")
            dist = item.get("distancia_km", None)
            link = item.get("link", "")
            
            # Criar um card para cada resultado
            card = ctk.CTkFrame(self.results_frame, corner_radius=5, fg_color=("gray85", "gray20"))
            card.pack(fill="x", pady=2, padx=5)
            
            # Formatação do texto
            status_cor = "🟢" if "Aberto" in onda else ("🔴" if "Fechado" in onda else "⚪")
            status_str = f" | {status_cor} {onda}" if onda != "Desconhecido" else ""
            dist_str = f" | 📍 {dist:.1f}km" if dist is not None else ""
            info_text = f"{i}. {nome} | ⭐ {nota} | 📞 {tel}{dist_str}{status_str}"
            
            lbl = ctk.CTkLabel(card, text=info_text, font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(anchor="w", padx=10, pady=(5, 0))
            
            if link and link != "Link indisponível":
                # Mostra o link e usa uma fonte menor, com evento de clique e hover
                link_lbl = ctk.CTkLabel(card, text=f"🔗 {link}", font=ctk.CTkFont(size=10, underline=True), text_color=("blue", "cyan"), cursor="hand2")
                link_lbl.pack(anchor="w", padx=10, pady=(0, 5))
                link_lbl.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

    def exportar_resultados(self, formato):
        if not self.resultados:
            self.log("[!] Erro: Nenhum dado para exportar.")
            return
            
        try:
            self.log(f"[*] Exportando dados para {formato.upper()}...")
            # Como a conversão de nome de arquivo usa formatação no formatter, chamamos diretamente
            if formato == "csv":
                arquivo = "resultados_busca.csv"
            elif formato == "json":
                arquivo = "resultados_busca.json"
            elif formato == "excel":
                arquivo = "resultados_busca.xlsx"
            
            formatter.exportar_dados(self.resultados, formato)
            
            # Tentar abrir o arquivo no Windows
            try:
                if os.path.exists(arquivo):
                    os.startfile(arquivo)
            except AttributeError:
                pass # Ignora erro de SO (se não for Windows, os.startfile não existe)
            self.log(f"[✔] Dados exportados com sucesso! Verifique a pasta raiz.")
        except Exception as e:
            self.log(f"[!] Erro ao exportar para {formato}: {e}")
            
    def fix_playwright(self):
        """Roda a instalação do playwright para corrigir problemas esporádicos do browser."""
        self.log("\n[*] Iniciando correção/download dos navegadores do Playwright...")
        self.btn_fix_playwright.configure(state="disabled", text="Corrigindo...")
        
        def run_fix():
            import subprocess
            try:
                # Roda o comando no sistema para instalar o chromium
                result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                                        capture_output=True, text=True)
                self.after(0, lambda: self.log(f"[*] Playwright Setup Finalizado.\n{result.stdout[:200]}..."))
            except Exception as e:
                self.after(0, lambda: self.log(f"[!] Erro ao corrigir Playwright: {e}"))
            finally:
                self.after(0, lambda: self.btn_fix_playwright.configure(state="normal", text="Corrigir Navegador"))
                
        threading.Thread(target=run_fix, daemon=True).start()

    def play_gif(self, path):
        # Cancelar animação atual de gif se existir
        if self.gif_after_id:
            self.after_cancel(self.gif_after_id)
            self.gif_after_id = None
            
        self.current_gif_frames = []
        self.gif_frame_idx = 0
        
        if not os.path.exists(path):
            self.lbl_gif.configure(image=None, text=f"Faltando:\n{os.path.basename(path)}\n(Crie a pasta assets)")
            return
            
        try:
            gif = Image.open(path)
            while True:
                # Converter para RGBA para evitar problemas de transparência
                frame = gif.copy().convert("RGBA")
                
                # Redimensionar para caber no espaço (agora maior)
                frame.thumbnail((250, 250), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=frame, size=frame.size)
                
                # Pega a duração do frame ou fallback para 80ms
                duration = gif.info.get("duration", 80)
                if duration == 0:
                    duration = 80
                    
                self.current_gif_frames.append((ctk_img, duration))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
            
        if self.current_gif_frames:
            self.lbl_gif.configure(text="")
            self.update_gif_frame()
            
    def update_gif_frame(self):
        if not self.current_gif_frames:
            return
            
        img, duration = self.current_gif_frames[self.gif_frame_idx]
        self.lbl_gif.configure(image=img)
        
        self.gif_frame_idx = (self.gif_frame_idx + 1) % len(self.current_gif_frames)
        self.gif_after_id = self.after(duration, self.update_gif_frame)

if __name__ == "__main__":
    app = App()
    app.mainloop()
