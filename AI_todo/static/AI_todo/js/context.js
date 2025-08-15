// // context.js
// const API = '/api/';

// async function loadContextList(){
//   const data = await getJSON(API + 'context/');
//   const container = document.getElementById('context-list');
//   container.innerHTML = '';
//   data.forEach(c => {
//     const el = document.createElement('div');
//     el.className = 'card';
//     el.innerHTML = `
//       <p class="small"><strong>${escapeHtml(c.source_type)}</strong> • ${new Date(c.created_at).toLocaleString()}</p>
//       <p>${escapeHtml(c.content)}</p>
//     `;
//     container.appendChild(el);
//   });
// }

// function escapeHtml(text){
//   return text ? text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])) : '';
// }

// document.addEventListener('DOMContentLoaded', () => {
//   loadContextList();
//   document.getElementById('context-form').addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const payload = {
//       content: document.getElementById('content').value,
//       source_type: document.getElementById('source_type').value
//     };
//     const res = await postJSON(API + 'context/', payload);
//     if(res.ok){
//       document.getElementById('content').value = '';
//       loadContextList();
//     } else {
//       alert('Failed to add context');
//     }
//   });
// });



document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("context-form");
    const contextList = document.getElementById("context-list");

    // Fetch and display contexts
    function fetchContexts() {
        fetch("/api/context/") // Replace with your actual Django API endpoint
            .then(response => response.json())
            .then(data => {
                contextList.innerHTML = "";
                data.forEach(item => renderContext(item));
            })
            .catch(error => console.error("Error fetching contexts:", error));
    }

    // Render a single context card
    function renderContext(item) {
        const card = document.createElement("div");
        card.className = "context-card";
        card.dataset.id = item.id;

        card.innerHTML = `
            <button class="delete-icon" data-id="${item.id}">✖</button>
            <p>${item.content}</p>
            <div class="context-meta">Source: ${item.source_type}</div>
        `;

        contextList.appendChild(card);
    }

    // Handle new context submission
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const content = document.getElementById("content").value;
        const sourceType = document.getElementById("source_type").value;

        fetch("/api/context/", { // Replace with your Django API endpoint
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                content: content,
                source_type: sourceType
            })
        })
        .then(response => response.json())
        .then(newItem => {
            renderContext(newItem);
            form.reset();
        })
        .catch(error => console.error("Error adding context:", error));
    });

    // Handle delete button clicks
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("delete-icon")) {
            const id = e.target.dataset.id;

            fetch(`/api/context/${id}/`, {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            })
            .then(response => {
                if (response.ok) {
                    document.querySelector(`.context-card[data-id="${id}"]`).remove();
                } else {
                    console.error("Failed to delete context");
                }
            })
            .catch(error => console.error("Error deleting context:", error));
        }
    });

    // Utility: Get CSRF token from cookies
    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const c = cookie.trim();
            if (c.startsWith(name + "=")) {
                return c.substring(name.length + 1);
            }
        }
        return "";
    }

    // Initial fetch
    fetchContexts();
});
