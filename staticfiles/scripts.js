const form = document.getElementById('taskForm');
const taskInput = document.getElementById('taskInput');
const categoryInput = document.getElementById('categoryInput');
const descriptionInput = document.getElementById('descriptionInput');
const taskList = document.getElementById('taskList');
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const applyFilters = document.getElementById('applyFilters');
const clearFilters = document.getElementById('clearFilters');

let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

function saveTasks() {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

function renderTasks() {
  taskList.innerHTML = '';
  const status = statusFilter.value;
  const category = categoryFilter.value.trim().toLowerCase();

  const filtered = tasks.filter(t => {
    const statusMatch = status === 'all' ||
      (status === 'pending' && !t.completed) ||
      (status === 'completed' && t.completed);
    const categoryMatch = !category || t.category.toLowerCase().includes(category);
    return statusMatch && categoryMatch;
  });

  if (filtered.length === 0) {
    taskList.innerHTML = '<p>No hay tareas que coincidan con los filtros.</p>';
    return;
  }

  filtered.forEach((task, index) => {
    const div = document.createElement('div');
    div.className = 'task';
    div.innerHTML = `
      <div class="task-header">
        <span class="title ${task.completed ? 'completed' : ''}">
          ${task.text} ${task.category ? `[${task.category}]` : ''}
        </span>
        <div class="task-buttons">
          <button onclick="toggleComplete(${index})">${task.completed ? 'Marcar Pendiente' : 'Completar'}</button>
          <button onclick="editTask(${index})">Editar</button>
          <button onclick="deleteTask(${index})">Eliminar</button>
        </div>
      </div>
      ${task.description ? `<p>${task.description}</p>` : ''}
    `;
    taskList.appendChild(div);
  });
}

function toggleComplete(index) {
  tasks[index].completed = !tasks[index].completed;
  saveTasks();
  renderTasks();
}

function editTask(index) {
  const newText = prompt('Editar tarea:', tasks[index].text);
  if (newText !== null) {
    tasks[index].text = newText.trim();
    saveTasks();
    renderTasks();
  }
}

function deleteTask(index) {
  if (confirm('¿Eliminar esta tarea?')) {
    tasks.splice(index, 1);
    saveTasks();
    renderTasks();
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = taskInput.value.trim();
  const category = categoryInput.value.trim();
  const description = descriptionInput.value.trim();
  if (text) {
    tasks.push({ text, category, description, completed: false });
    saveTasks();
    renderTasks();
    form.reset();
  }
});

applyFilters.addEventListener('click', renderTasks);
clearFilters.addEventListener('click', () => {
  statusFilter.value = 'all';
  categoryFilter.value = '';
  renderTasks();
});

renderTasks();