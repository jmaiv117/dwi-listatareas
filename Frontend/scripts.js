const form = document.getElementById('taskForm');
const taskInput = document.getElementById('taskInput');
const categoryInput = document.getElementById('categoryInput');
const descriptionInput = document.getElementById('descriptionInput');
const priorityInput = document.getElementById('priorityInput');
const finInput = document.getElementById('finInput');
const taskList = document.getElementById('taskList');
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const applyFilters = document.getElementById('applyFilters');
const clearFilters = document.getElementById('clearFilters');

let tasks = [];
let editingId = null;

async function fetchTasks() {
  const res = await fetch('http://localhost:8800/actividades');
  tasks = await res.json();
  renderTasks();
}

async function createTask(task) {
  const res = await fetch('http://localhost:8800/actividades', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  });
  if (res.ok) {
    await fetchTasks();
  }
}

async function updateTask(id, task) {
  const res = await fetch(`http://localhost:8800/actividades/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  });
  if (res.ok) {
    await fetchTasks();
  }
}

async function deleteTask(id) {
  const res = await fetch(`http://localhost:8800/actividades/${id}`, {
    method: 'DELETE'
  });
  if (res.ok) {
    await fetchTasks();
  }
}

function getTaskColor(task) {
  const now = new Date();
  const fin = new Date(task.Fin);
  const diffMs = fin - now;
  const diffDays = diffMs / (1000 * 60 * 60 * 24);
  if (diffDays < 0) {
    return 'task-red'; // Vencida
  } else if (diffDays <= 7) {
    return 'task-yellow'; // Menos de una semana
  } else {
    return 'task-green'; // Próximas
  }
}

function renderTasks() {
  taskList.innerHTML = '';
  const status = statusFilter.value;
  const category = categoryFilter.value.trim().toLowerCase();

  const filtered = tasks.filter(t => {
    const statusMatch = status === 'all' ||
      (status === 'pending' && t.Prioridad !== 'Completada') ||
      (status === 'completed' && t.Prioridad === 'Completada');
    const categoryMatch = !category || t.Categoria.toLowerCase().includes(category);
    return statusMatch && categoryMatch;
  });

  if (filtered.length === 0) {
    taskList.innerHTML = '<p>No hay tareas que coincidan con los filtros.</p>';
    return;
  }

  filtered.forEach((task) => {
    const div = document.createElement('div');
    div.className = `task ${getTaskColor(task)}`;
    div.dataset.id = task.id;
    div.innerHTML = `
      <div class="task-header">
        <span class="title ${task.Prioridad === 'Completada' ? 'completed' : ''}">
           ${task.Categoria ? `[${task.Categoria}]` : ''} <strong>${task.Nombre}</strong>
        </span>
        <div class="task-buttons">
          <button class="complete-btn">${task.Prioridad === 'Completada' ? 'Marcar Pendiente' : 'Completar'}</button>
          <button class="edit-btn">Editar</button>
          <button class="delete-btn">Eliminar</button>
        </div>
      </div>
      ${task.Descripcion ? `<p><strong>Descripción:</strong> ${task.Descripcion}</p>` : ''}
      <div class="task-dates">
        <small><strong>Creada:</strong> ${task.Fecha ? new Date(task.Fecha).toLocaleString() : ''}</small><br/>
        <small><strong>Fin:</strong> ${task.Fin ? new Date(task.Fin).toLocaleString() : ''}</small>
      </div>
      <div class="task-priority">
        <small><strong>Prioridad:</strong> ${task.Prioridad}</small>
      </div>
    `;
    taskList.appendChild(div);
  });
}

// Delegación de eventos para los botones
// Esto asegura que los botones funcionen aunque se regenere el HTML
taskList.addEventListener('click', async (e) => {
  const btn = e.target;
  const div = btn.closest('.task');
  if (!div) return;
  const id = div.dataset.id;
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  if (btn.classList.contains('complete-btn')) {
    const nuevaPrioridad = task.Prioridad === 'Completada' ? 'Pendiente' : 'Completada';
    await updateTask(id, { ...task, Prioridad: nuevaPrioridad });
  } else if (btn.classList.contains('edit-btn')) {
    taskInput.value = task.Nombre;
    categoryInput.value = task.Categoria;
    descriptionInput.value = task.Descripcion;
    priorityInput.value = task.Prioridad;
    finInput.value = task.Fin ? task.Fin.slice(0, 16) : '';
    editingId = id;
  } else if (btn.classList.contains('delete-btn')) {
    if (confirm('¿Eliminar esta tarea?')) {
      await deleteTask(id);
    }
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const Nombre = taskInput.value.trim();
  const Categoria = categoryInput.value.trim();
  const Descripcion = descriptionInput.value.trim();
  const Prioridad = priorityInput.value.trim();
  const Fin = finInput.value;
  if (Nombre) {
    const taskData = { Nombre, Categoria, Descripcion, Prioridad, Fin };
    if (editingId) {
      await updateTask(editingId, taskData);
      editingId = null;
    } else {
      await createTask(taskData);
    }
    form.reset();
    await fetchTasks();
  }
});

applyFilters.addEventListener('click', renderTasks);
clearFilters.addEventListener('click', () => {
  statusFilter.value = 'all';
  categoryFilter.value = '';
  renderTasks();
});

// Inicializar
fetchTasks();

document.addEventListener('DOMContentLoaded', function() {
  const finInput = document.getElementById('finInput');
  if (finInput) {
    const now = new Date();
    now.setHours(0,0,0,0);
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    const hh = '00';
    const min = '00';
    finInput.value = `${yyyy}-${mm}-${dd}T${hh}:${min}`;
  }
});