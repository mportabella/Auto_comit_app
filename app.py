from flask import Flask, request, render_template, redirect
from git import Repo
import os
from datetime import datetime
import shutil
import subprocess

from timeline.routes import timeline_bp
from timeline.git_utils import contar_commits_por_fase

app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        categoria = request.form['categoria']
        comentario = request.form['comentario']
        dia_hora = request.form['dia_hora']
        archivos = request.files.getlist('archivos')

        # Limpiar el directorio repo2 antes de guardar nuevos archivos
        limpiar_directorio(REPO_PATH)

        # Guardar archivos
        for archivo in archivos:
            archivo.save(os.path.join(REPO_PATH, archivo.filename))

        # Crear mensaje de commit
        ahora = dia_hora
        mensaje = f"[{categoria}] {ahora} {comentario}"

        # Hacer commit
        repo = Repo(REPO_PATH)
        repo.git.add(A=True)
        repo.index.commit(mensaje)
        origin = repo.remote(name='origin')
        origin.push()

        return redirect('/')

    # GET: mostrar las fases con conteo de commits
    conteo = contar_commits_por_fase()

    # 🔁 Ejecutar el script que genera el gráfico de fases
    script_path = os.path.join(os.path.dirname(__file__), 'Visualizaciones', 'grafico_fases.py')
    subprocess.run(['python', script_path], check=True)

    # 🔁 Ejecutar el script que genera el gráfico de fases
    script_path = os.path.join(os.path.dirname(__file__), 'Visualizaciones', 'grafico_fases_plotly.py')
    subprocess.run(['python', script_path], check=True)

    return render_template('index.html', conteo=conteo, grafico_url='/static/fases.png')

if __name__ == '__main__':
    app.run(debug=True)



