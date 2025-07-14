import plotly.graph_objects as go
from datetime import datetime
from git import Repo
import os
import re

# Ruta al repositorio local
repo_path = os.path.join(os.path.dirname(__file__), '..', 'repo2')
repo = Repo(repo_path)

# Obtener commits ordenados cronológicamente
rama_activa = repo.active_branch.name
commits = list(repo.iter_commits(rama_activa))

commits.sort(key=lambda c: c.committed_datetime)

# Buscar el primer commit de cada fase detectada
primer_commit_por_fase = {}
for commit in commits:
    mensaje = commit.message.strip()
    match = re.match(r'\[(.*?)\]', mensaje)
    if match:
        fase = match.group(1).lower()
        if fase not in primer_commit_por_fase:
            primer_commit_por_fase[fase] = commit.committed_datetime

# Ordenar fases por fecha de su primer commit
fases_ordenadas = sorted(primer_commit_por_fase.items(), key=lambda x: x[1])
fases = [f[0] for f in fases_ordenadas]
fechas = [f[1] for f in fases_ordenadas]

# Calcular duración entre fases
duraciones = [(fechas[i+1] - fechas[i]).total_seconds() for i in range(len(fechas)-1)]
duraciones.append(3600)  # duración estimada de la última fase

# Calcular proporciones
total = sum(duraciones)
porcentajes = [d / total for d in duraciones]

# Colores
colores_base = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0', '#00BCD4']
colores = colores_base[:len(fases)]

# Crear una traza por fase
trazas_fases = []
inicio = 0
for i, (fase, porcentaje) in enumerate(zip(fases, porcentajes)):
    traza = go.Bar(
        x=[porcentaje],
        y=['Fases'],
        orientation='h',
        marker=dict(color=colores[i]),
        name=fase,
        text=f"{fase} ({round(porcentaje * 100)}%)",
        textposition='inside',
        hoverinfo='text',
        base=inicio  # <-- esto posiciona la barra justo después de la anterior
    )
    trazas_fases.append(traza)
    inicio += porcentaje

# Calcular tiempo total del proyecto
fecha_inicio = commits[0].committed_datetime
fecha_fin = commits[-1].committed_datetime
duracion_total = (fecha_fin - fecha_inicio).total_seconds()

import re

# Calcular tiempo total del proyecto
fecha_inicio = commits[0].committed_datetime
fecha_fin = commits[-1].committed_datetime
duracion_total = (fecha_fin - fecha_inicio).total_seconds()

# Colores por fase
colores_por_fase = {
    'idea': '#4CAF50',
    'diseño': '#2196F3',
    'construccion': '#FFC107',
    'uso': '#F44336',
    'historico': '#9C27B0',
    'otra': '#00BCD4'
}

# Clasificar commits por fase
x_vals = []
y_vals = []
colores = []
textos = []

for c in commits:
    mensaje = c.message.strip()
    match = re.match(r'\[(.*?)\]', mensaje)
    fase = match.group(1).lower() if match else 'historico'
    color = colores_por_fase.get(fase, colores_por_fase['otra'])

    tiempo_relativo = (c.committed_datetime - fecha_inicio).total_seconds() / duracion_total

    x_vals.append(tiempo_relativo)
    y_vals.append(0.5)
    colores.append(color)
    textos.append(f"{mensaje}")

puntos_commits = go.Scatter(
    x=x_vals,
    y=y_vals,
    mode='markers',
    marker=dict(color=colores, size=6),
    text=textos,
    hoverinfo='text',
    name='Commits'
)


# Crear figura
fig = go.Figure(data=trazas_fases + [puntos_commits])

# Ajustes de layout
fig.update_layout(
    title='Proporción temporal entre fases del proyecto',
    barmode='stack',
    height=250,
    xaxis=dict(title='Progreso del proyecto (%)', range=[0, 1], showgrid=False),
    yaxis=dict(showticklabels=False),
    showlegend=False,
    margin=dict(l=20, r=20, t=40, b=20)
)

# Mostrar o guardar
fig.write_html(os.path.join(os.path.dirname(__file__), '..', 'static', 'fases_interactivo.html'))
