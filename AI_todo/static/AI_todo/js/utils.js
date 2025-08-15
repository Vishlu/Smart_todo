// utils.js - include in base.html
function getCookie(name) {
  const v = `; ${document.cookie}`;
  const parts = v.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
const csrftoken = getCookie('csrftoken');

async function postJSON(url, payload){
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(payload)
  });
  return res;
}

async function getJSON(url){
  const res = await fetch(url);
  return res.json();
}
