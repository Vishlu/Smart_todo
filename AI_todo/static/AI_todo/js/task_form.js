// static/AI_todo/js/task_form.js
const API = '/api/';

async function loadCategoriesToSelect(){
  const cats = await getJSON(API + 'categories/');
  const sel = document.getElementById('category');
  sel.innerHTML = '<option value="">Select Category</option>';
  cats.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.name;
    sel.appendChild(opt);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadCategoriesToSelect();

  const form = document.getElementById('task-form');
  const aiBtn = document.getElementById('ai-suggest');
  const feedback = document.getElementById('ai-feedback');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      title: document.getElementById('title').value,
      description: document.getElementById('description').value,
      deadline: document.getElementById('deadline').value || null,
      status: document.getElementById('status').value,
      category_id: document.getElementById('category').value || null,
      priority_score: parseFloat(document.getElementById('priority_score').value) || 0
    };

    const res = await postJSON(API + 'tasks/', payload);
    if(res.ok){
      feedback.textContent = 'Saved successfully!';
      // optional: redirect to dashboard
      window.location.href = '/';
    } else {
      feedback.textContent = 'Error saving task';
    }
  });


  aiBtn.addEventListener('click', async () => {
    feedback.textContent = 'Getting AI suggestion...';
    aiBtn.disabled = true;
    try {
      const title = document.getElementById('title').value;
      const description = document.getElementById('description').value;

      const res = await postJSON(API + 'ai/suggest/', { title, description, context_ids: [] });
      if(!res.ok){
        feedback.textContent = 'AI request failed';
        aiBtn.disabled = false;
        return;
      }
      const s = await res.json();

      // Fill each field with AI suggestion (user can edit afterwards)
      if(s.suggested_title) document.getElementById('title').value = s.suggested_title;
      if(s.enhanced_description) document.getElementById('description').value = s.enhanced_description;
      if(s.suggested_deadline) document.getElementById('deadline').value = s.suggested_deadline;

      // category: try to select existing category by exact name, if not found add temp option
      if(s.category){
        const sel = document.getElementById('category');
        let matched = false;
        for(let i=0;i<sel.options.length;i++){
          if(sel.options[i].text.trim().toLowerCase() === s.category.trim().toLowerCase()){
            sel.selectedIndex = i;
            matched = true;
            break;
          }
        }
        if(!matched){
          // create an option (will not exist server-side yet; user can create a category manually if needed)
          const opt = document.createElement('option');
          opt.value = ''; // no id
          opt.textContent = s.category;
          opt.selected = true;
          sel.appendChild(opt);
        }
      }

      // Set priority_score hidden input
      if(typeof s.priority_score !== 'undefined'){
        document.getElementById('priority_score').value = s.priority_score;
      }

      feedback.textContent = `AI suggested priority ${s.priority_score} • category: ${s.category}`;
    } catch (err) {
      console.error(err);
      feedback.textContent = 'AI suggestion error';
    } finally {
      aiBtn.disabled = false;
    }
  });
});



