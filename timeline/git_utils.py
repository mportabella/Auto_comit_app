from git import Repo
import os
import re
REPO_PATH = os.path.join(os.path.dirname(__file__), '..', 'repo2')

def obtener_commits_por_fase(fase,rama='main'):
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits(f'{rama}'))
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




def contar_commits_por_fase(rama='main'):
    fases = ['historico', 'idea', 'diseño', 'construccion', 'uso']
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits(rama))

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

def obtener_diff_entre_commits(commit_hash1, commit_hash2, archivo):
    repo = Repo(REPO_PATH)
    try:
        diff = repo.git.diff(commit_hash1, commit_hash2, '--', archivo)
        return diff
    except Exception as e:
        return f"Error al obtener diff: {e}"



