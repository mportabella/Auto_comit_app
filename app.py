from flask import Flask, request, render_template, redirect, session
from git import Repo
import os
from datetime import datetime
import shutil
import subprocess

from timeline.routes import timeline_bp
from timeline.git_utils import contar_commits_por_fase

app = Flask(__name__)
app.secret_key = 'clave-super-secreta-para-dev'
UPLOAD_FOLDER = 'uploads'
REPO_PATH = 'repo2'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(timeline_bp)




def limpiar_directorio(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if item == '.git':

            continue
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Error eliminando {item_path}: {e}")

            # Página para seleccionar proyecto

@app.route('/selector', methods=['GET', 'POST'])
def seleccionar_proyecto():
    repo = Repo(REPO_PATH)
    ramas = [head.name for head in repo.heads]

    if request.method == 'POST':
        proyecto = request.form['proyecto']
        session['rama'] = proyecto

        if repo.active_branch.name != proyecto:
            repo.git.checkout(proyecto)

        return redirect('/')

    return render_template('selector.html', ramas=ramas)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'rama' not in session:
        return redirect('/selector')

    rama_actual = session.get('rama', 'main')
    repo = Repo(REPO_PATH)

    # Cambiar a la rama seleccionada si no está activa
    if repo.active_branch.name != rama_actual:
        repo.git.checkout(rama_actual)

    if request.method == 'POST':
        categoria = request.form['categoria']
        comentario = request.form['comentario']
        dia_hora_raw = request.form['dia_hora']
        archivos = request.files.getlist('archivos')

        # Convertir formato de fecha y hora
        dia_hora = datetime.strptime(dia_hora_raw, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M")

        # Limpiar el directorio repo2 antes de guardar nuevos archivos
        #limpiar_directorio(REPO_PATH)

        # Guardar archivos
        for archivo in archivos:
            archivo.save(os.path.join(REPO_PATH, archivo.filename))

        # Crear mensaje de commit
        mensaje = f"[{categoria}] {dia_hora} {comentario}"

        # Establecer la fecha del commit como variable de entorno
        env = os.environ.copy()
        env["GIT_COMMITTER_DATE"] = dia_hora

        # Hacer el commit con la fecha personalizada
        subprocess.run(["git", "add", "."], cwd=REPO_PATH)
        subprocess.run(["git", "commit", "-m", mensaje, "--date", dia_hora], cwd=REPO_PATH, env=env)

        # Push a origin
        origin = repo.remote(name='origin')
        rama = repo.active_branch.name

        # Verifica si la rama tiene upstream
        if repo.head.reference.tracking_branch() is None:
            origin.push(refspec=f"{rama}:{rama}", set_upstream=True)
        else:
            origin.push()

        return redirect('/')

    # GET: mostrar las fases con conteo de commits de la rama actual
    conteo = contar_commits_por_fase(rama_actual)

    # Ejecutar scripts de visualización
    script_path = os.path.join(os.path.dirname(__file__), 'Visualizaciones', 'grafico_fases.py')
    import sys
    commits = list(repo.iter_commits(session.get('rama', 'main')))
    hay_fases = any('[' in c.message and ']' in c.message for c in commits)

    if hay_fases:
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'Visualizaciones', 'grafico_fases.py')
            subprocess.run([sys.executable, script_path], check=True)
            script_path = os.path.join(os.path.dirname(__file__), 'Visualizaciones', 'grafico_fases_plotly.py')
            subprocess.run([sys.executable, script_path], check=True)
        except Exception as e:
            print(f"Error al generar gráficos: {e}")
    else:
        print("No hay commits con formato de fase. Se omite la generación de gráficos.")

    return render_template(
        'index.html',
        conteo=conteo,
        grafico_url='/static/fases.png',
        rama_actual=rama_actual
    )


if __name__ == '__main__':
    app.run(debug=True)



