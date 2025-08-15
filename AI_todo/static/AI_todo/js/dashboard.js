// // dashboard.js
// const API = '/api/';
// let TASKS_CACHE = [];

// async function loadCategoriesIntoFilter(){
//   const cats = await getJSON(API + 'categories/');
//   const sel = document.getElementById('filter-category');
//   sel.innerHTML = '<option value="">All Categories</option>';
//   cats.forEach(c => {
//     const o = document.createElement('option'); o.value = c.name; o.textContent = c.name; sel.appendChild(o);
//   });
// }

// function renderTasks(tasks){
//   const list = document.getElementById('task-list');
//   list.innerHTML = '';
//   if(!tasks.length){ list.innerHTML = '<p class="muted">No tasks yet.</p>'; return; }
//   tasks.forEach(t => {
//     const priorityClass = t.priority_score >= 7 ? 'high' : (t.priority_score >= 4 ? 'medium' : 'low');
//     const card = document.createElement('div');
//     card.className = `card ${priorityClass}`;
//     card.innerHTML = `
//       <h3>${escapeHtml(t.title)}</h3>
//       <p>${escapeHtml(t.description || '')}</p>
//       <p class="small"><strong>Deadline:</strong> ${t.deadline || '—'} • <strong>Status:</strong> ${t.status || '—'}</p>
//       <p class="small"><strong>Category:</strong> ${t.category ? t.category.name : '—'} • <strong>Priority:</strong> ${t.priority_score}</p>
//     `;
//     list.appendChild(card);
//   });
// }

// function applyFilters(){
//   const cat = document.getElementById('filter-category').value;
//   const status = document.getElementById('filter-status').value;
//   const pr = document.getElementById('filter-priority').value;
//   let filtered = TASKS_CACHE.slice();

//   if(cat) filtered = filtered.filter(t => (t.category && t.category.name === cat));
//   if(status) filtered = filtered.filter(t => t.status === status);
//   if(pr){
//     filtered = filtered.filter(t => {
//       const p = t.priority_score || 0;
//       if(pr==='high') return p>=7;
//       if(pr==='medium') return p>=4 && p<7;
//       return p<4;
//     });
//   }
//   renderTasks(filtered);
// }

// async function fetchAndShowTasks(){
//   const data = await getJSON(API + 'tasks/');
//   TASKS_CACHE = data;
//   applyFilters();
// }

// function escapeHtml(text){
//   return text ? text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])) : '';
// }

// document.addEventListener('DOMContentLoaded', async () => {
//   await loadCategoriesIntoFilter();
//   await fetchAndShowTasks();
//   document.getElementById('filter-category').addEventListener('change', applyFilters);
//   document.getElementById('filter-status').addEventListener('change', applyFilters);
//   document.getElementById('filter-priority').addEventListener('change', applyFilters);
//   document.getElementById('refresh').addEventListener('click', fetchAndShowTasks);
// });





const API = '/api/';
let TASKS_CACHE = [];

// Fetch categories into the filter dropdown
async function loadCategoriesIntoFilter() {
  const cats = await getJSON(API + 'categories/');
  const sel = document.getElementById('filter-category');
  sel.innerHTML = '<option value="">All Categories</option>';
  cats.forEach(c => {
    const o = document.createElement('option');
    o.value = c.name;
    o.textContent = c.name;
    sel.appendChild(o);
  });
}

// Render all tasks
function renderTasks(tasks) {
  const list = document.getElementById('task-list');
  list.innerHTML = '';
  if (!tasks.length) {
    list.innerHTML = '<p class="muted">No tasks yet.</p>';
    return;
  }

  tasks.forEach(t => {
    const priorityClass = t.priority_score >= 7 ? 'high' :
                         (t.priority_score >= 4 ? 'medium' : 'low');

    const card = document.createElement('div');
    card.className = `card ${priorityClass}`;
    card.innerHTML = `
      <div class="card-header">
        <h3>${escapeHtml(t.title)}</h3>
        <button class="delete-btn" data-id="${t.id}" title="Delete Task">
          ❌
        </button>
      </div>
      <p>${escapeHtml(t.description || '')}</p>
      <p class="small"><strong>Deadline:</strong> ${t.deadline || '—'} • <strong>Status:</strong> ${t.status || '—'}</p>
      <p class="small"><strong>Category:</strong> ${t.category ? t.category.name : '—'} • <strong>Priority:</strong> ${t.priority_score}</p>
    `;

    list.appendChild(card);
  });

  // Attach delete button events
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const taskId = e.target.getAttribute('data-id');
      if (confirm('Are you sure you want to delete this task?')) {
        await deleteTask(taskId);
      }
    });
  });
}

// Delete task API call
async function deleteTask(taskId) {
  const res = await fetch(API + `tasks/${taskId}/`, {
    method: 'DELETE',
    headers: { 'X-CSRFToken': getCSRFToken() }
  });
  if (res.ok) {
    TASKS_CACHE = TASKS_CACHE.filter(t => t.id != taskId);
    applyFilters();
  } else {
    alert('Error deleting task.');
  }
}

// Apply filters
function applyFilters() {
  const cat = document.getElementById('filter-category').value;
  const status = document.getElementById('filter-status').value;
  const pr = document.getElementById('filter-priority').value;
  let filtered = TASKS_CACHE.slice();

  if (cat) filtered = filtered.filter(t => (t.category && t.category.name === cat));
  if (status) filtered = filtered.filter(t => t.status === status);
  if (pr) {
    filtered = filtered.filter(t => {
      const p = t.priority_score || 0;
      if (pr === 'high') return p >= 7;
      if (pr === 'medium') return p >= 4 && p < 7;
      return p < 4;
    });
  }
  renderTasks(filtered);
}

// Fetch tasks from backend
async function fetchAndShowTasks() {
  const data = await getJSON(API + 'tasks/');
  TASKS_CACHE = data;
  applyFilters();
}

// Escape HTML to avoid XSS
function escapeHtml(text) {
  return text
    ? text.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
    : '';
}

// Get CSRF token (Django)
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}

// On page load
document.addEventListener('DOMContentLoaded', async () => {
  await loadCategoriesIntoFilter();
  await fetchAndShowTasks();

  document.getElementById('filter-category').addEventListener('change', applyFilters);
  document.getElementById('filter-status').addEventListener('change', applyFilters);
  document.getElementById('filter-priority').addEventListener('change', applyFilters);
  document.getElementById('refresh').addEventListener('click', fetchAndShowTasks);
});
