from flask import Blueprint, render_template, send_file, abort,session,request
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
'''
@timeline_bp.route('/comparar/<commit1>/<commit2>/<path:archivo>')
def comparar_archivos(commit1, commit2, archivo):
    diff = obtener_diff_entre_commits(commit1, commit2, archivo)
    return render_template('comparar_archivos.html', diff=diff, archivo=archivo, commit1=commit1,
                                   commit2=commit2)
       #no lo necessito                            
'''

@timeline_bp.route('/seleccionar-archivos', methods=['POST'])
def seleccionar_archivos_para_comparar():
    commit_hashes = request.form.getlist('commits')
    fase = request.form.get('fase')

    if len(commit_hashes) != 2:
        return "Debes seleccionar exactamente dos commits.", 400

    commit1, commit2 = commit_hashes
    repo = Repo(REPO_PATH)

    archivos_commit1 = {blob.path for blob in repo.commit(commit1).tree.traverse() if blob.type == 'blob'}
    archivos_commit2 = {blob.path for blob in repo.commit(commit2).tree.traverse() if blob.type == 'blob'}
    todos_los_archivos = sorted(archivos_commit1 | archivos_commit2)

    if 'archivos' in request.form:
        archivos_seleccionados = request.form.getlist('archivos')
        diffs = []

        for archivo in archivos_seleccionados:
            if archivo in archivos_commit1 and archivo in archivos_commit2:
                diff = obtener_diff_entre_commits(commit1, commit2, archivo)
            elif archivo in archivos_commit1:
                diff = f"⚠️ El archivo '{archivo}' fue eliminado en el segundo commit."
            elif archivo in archivos_commit2:
                diff = f"🆕 El archivo '{archivo}' fue añadido en el segundo commit."
            else:
                diff = f"❓ El archivo '{archivo}' no se encuentra en ninguno de los commits."

            es_ifc = archivo.lower().endswith('.ifc')
            diffs.append({
                'archivo': archivo,
                'diff': diff,
                'es_ifc': es_ifc,
                'commit1': commit1,
                'commit2': commit2
            })

        return render_template('seleccionar_archivo_para_diff.html',
                               archivos=todos_los_archivos,
                               commit1=commit1,
                               commit2=commit2,
                               fase=fase,
                               diffs=diffs)

    return render_template('seleccionar_archivo_para_diff.html',
                           archivos=todos_los_archivos,
                           commit1=commit1,
                           commit2=commit2,
                           fase=fase,
                           diffs=None)


@timeline_bp.route('/ver-diferencias-ifc', methods=['POST'])
def ver_diferencias_ifc():
    import tempfile
    import subprocess
    from git import Repo

    archivo = request.form.get('archivo')
    commit1 = request.form.get('commit1')
    commit2 = request.form.get('commit2')

    repo = Repo(REPO_PATH)

    # Crear archivos temporales para las versiones del archivo IFC
    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = os.path.join(tmpdir, 'version1.ifc')
        path2 = os.path.join(tmpdir, 'version2.ifc')

        try:
            blob1 = repo.commit(commit1).tree / archivo
            with open(path1, 'wb') as f:
                f.write(blob1.data_stream.read())
        except Exception:
            path1 = None

        try:
            blob2 = repo.commit(commit2).tree / archivo
            with open(path2, 'wb') as f:
                f.write(blob2.data_stream.read())
        except Exception:
            path2 = None

        # Ejecutar ifc-diff si ambos archivos existen
        if path1 and path2:
            try:
                result = subprocess.run(
                    ['ifc-diff', path1, path2],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                resultado_ifc_diff = result.stdout
            except subprocess.CalledProcessError as e:
                resultado_ifc_diff = f"❌ Error al ejecutar ifc-diff:\n{e.stderr}"
        else:
            resultado_ifc_diff = "⚠️ No se pudo extraer uno o ambos archivos IFC de los commits seleccionados."

    return render_template('ver_diferencias_ifc.html',
                           archivo=archivo,
                           commit1=commit1,
                           commit2=commit2,
                           resultado=resultado_ifc_diff)




