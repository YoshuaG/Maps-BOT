import os

desktop_dir = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop')
bat_path = os.path.join(desktop_dir, 'Abrir Bot do Maps.bat')
vbs_path = os.path.join(desktop_dir, 'Abrir Bot do Maps (Oculto).vbs')

# Arquivo BAT (opcional, mas bom pra quem gosta do console piscar e sumir)
bat_content = '''@echo off
cd /d "c:\\Users\\yoshu\\OneDrive\\Desktop\\bot pesquisa"
start "" "venv\\Scripts\\pythonw.exe" "maps_bot\\gui.py"
exit
'''

# Arquivo VBS - Cria um atalho que abre 100% invisível (Apenas a interface gráfica e sem janela preta).
vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """c:\\Users\\yoshu\\OneDrive\\Desktop\\bot pesquisa\\venv\\Scripts\\pythonw.exe"" ""c:\\Users\\yoshu\\OneDrive\\Desktop\\bot pesquisa\\maps_bot\\gui.py""", 0, False
'''

try:
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    print(f"[*] CRIADO NA ÁREA DE TRABALHO: {bat_path}")
    
    with open(vbs_path, 'w', encoding='utf-8') as f:
        f.write(vbs_content)
    print(f"[*] CRIADO NA ÁREA DE TRABALHO: {vbs_path}")
    
except Exception as e:
    print(f"[!] Erro ao criar arquivos na Área de Trabalho: {e}")
