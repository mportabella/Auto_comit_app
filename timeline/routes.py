from flask import Blueprint, render_template, send_file, abort
from git import Repo
import os
import io
from .git_utils import obtener_commits_por_fase, REPO_PATH

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/timeline/<fase>')
def timeline(fase):
    commits = obtener_commits_por_fase(fase)
    return render_template('timeline.html', fase=fase, commits=commits)

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

