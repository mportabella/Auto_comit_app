import matplotlib.pyplot as plt
from datetime import datetime
from git import Repo
import os
import re

# Ruta al repositorio local
repo_path = os.path.join(os.path.dirname(__file__), '..', 'repo2')
repo = Repo(repo_path)

# Obtener commits ordenados cronológicamente
commits = list(repo.iter_commits('main'))
commits.sort(key=lambda c: c.committed_datetime)

# Buscar el primer commit de cada fase detectada
primer_commit_por_fase = {}

for commit in commits:
    mensaje = commit.message.strip()
    match = re.match(r'\[(.*?)\]', mensaje)
    if match:
        fase = match.group(1)
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

# Colores (puedes personalizar más si hay más fases)
colores_base = ['#4CAF50', '#2196F3', '#FFC107', '#F44336', '#9C27B0', '#00BCD4']
colores = colores_base[:len(fases)]

# Crear gráfico
fig, ax = plt.subplots(figsize=(10, 1.5))
inicio = 0
for i, p in enumerate(porcentajes):
    ax.barh(0, width=p, left=inicio, height=0.1, color=colores[i], edgecolor='black')
    porcentaje_texto = f"{fases[i]} ({round(p * 100)}%)"
    ax.text(inicio + p/2, 0, porcentaje_texto, ha='center', va='center', fontsize=9, color='white')
    inicio += p


# Estética
ax.set_xlim(0, 1)
ax.set_yticks([])
ax.set_xticks([])
ax.set_title('Proporción temporal entre fases del proyecto', fontsize=12)
plt.box(False)
plt.tight_layout()

# Calcular tiempo total del proyecto
fecha_inicio = commits[0].committed_datetime
fecha_fin = commits[-1].committed_datetime
duracion_total = (fecha_fin - fecha_inicio).total_seconds()

# Añadir commits como puntos
for commit in commits:
    tiempo_relativo = (commit.committed_datetime - fecha_inicio).total_seconds() / duracion_total
    ax.plot(tiempo_relativo, 0.05, 'o', color='black', markersize=4)


# Guardar gráfico
plt.savefig(os.path.join(os.path.dirname(__file__), '..', 'static', 'fases.png'))



