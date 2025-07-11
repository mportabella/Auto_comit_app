from git import Repo
import os
import re
REPO_PATH = os.path.join(os.path.dirname(__file__), '..', 'repo2')

def obtener_commits_por_fase(fase):
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits('main'))
    resultado = []

    for commit in commits:
        mensaje = commit.message.strip()
        match = re.match(r'\[(.*?)\]', mensaje)
        fase_detectada = match.group(1).lower() if match else 'historico'

        if fase == 'historico':
            resultado.append({
                'hash': commit.hexsha[:7],
                'mensaje': mensaje,
                'fecha': commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                'fase': fase_detectada  # ✅ Añadido
            })
        elif fase_detectada == fase.lower():
            resultado.append({
                'hash': commit.hexsha[:7],
                'mensaje': mensaje,
                'fecha': commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                'fase': fase_detectada  # ✅ Añadido
            })

    return resultado




def contar_commits_por_fase():
    fases = ['historico', 'idea', 'diseño', 'construccion', 'uso']
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits('main'))

    conteo = {fase: 0 for fase in fases}

    for commit in commits:
        mensaje = commit.message.lower()
        for fase in fases:
            if fase != 'historico' and mensaje.startswith(f"[{fase}]"):
                conteo[fase] += 1
                break

    # El total de commits es el valor de 'historico'
    conteo['historico'] = len(commits)

    return conteo


