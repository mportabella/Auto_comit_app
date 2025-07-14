from flask import Blueprint, render_template, send_file, abort,session
from git import Repo
import os
import io
from .git_utils import obtener_commits_por_fase, REPO_PATH, obtener_diff_entre_commits

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/timeline/<fase>')
def timeline(fase):
    rama = session.get('rama','main')
    commits = obtener_commits_por_fase(fase, rama)
    return render_template('timeline.html', fase=fase, commits=commits,rama_actual = rama )

@timeline_bp.route('/ver-archivos/<commit_hash>')
def ver_archivos(commit_hash):
    repo = Repo(REPO_PATH)
    try:
        commit = repo.commit(commit_hash)
    except Exception:
        abort(404)

    archivos = []
    for item in commit.tree.traverse():
        if item.type == 'blob':
            archivos.append({
                'nombre': item.path,
                'ruta': f"/descargar-archivo/{commit_hash}/{item.path}"
            })

    return render_template('ver_archivos.html', commit=commit, archivos=archivos)

@timeline_bp.route('/descargar-archivo/<commit_hash>/<path:archivo>')
def descargar_archivo(commit_hash, archivo):
    repo = Repo(REPO_PATH)
    try:
        blob = repo.commit(commit_hash).tree / archivo
        contenido = blob.data_stream.read()
        return send_file(
            io.BytesIO(contenido),
            as_attachment=True,
            download_name=os.path.basename(archivo)
        )
    except Exception:
        abort(404)

@timeline_bp.route('/comparar/<commit1>/<commit2>/<path:archivo>')
def comparar_archivos(commit1, commit2, archivo):
    diff = obtener_diff_entre_commits(commit1, commit2, archivo)
    return render_template('comparar_archivos.html', diff=diff, archivo=archivo, commit1=commit1,
                                   commit2=commit2)


