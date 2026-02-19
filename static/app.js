function handleSubmit(btnId, formId) {
  const btn = document.getElementById(btnId);
  const form = document.getElementById(formId);

  form.addEventListener("submit", function () {
    btn.disabled = true;
    btn.innerText = "Processing...";
  });
}
function handleSubmit(btnId, formId) {
  const btn = document.getElementById(btnId);
  const form = document.getElementById(formId);

  form.addEventListener("submit", function () {
    btn.disabled = true;
    btn.innerText = "Creating Account...";
  });
}

function handleSubmit(btnId, formId) {
  const btn = document.getElementById(btnId);
  const form = document.getElementById(formId); 
  caches.keys().then(function (cacheNames) {
    cacheNames.forEach(function (cacheName) {
      caches.delete(cacheName);
    });