function handleSubmit(btnId, formId) {
  const btn = document.getElementById(btnId);
  const form = document.getElementById(formId);

  form.addEventListener("submit", function () {
    btn.disabled = true;
    btn.innerText = "Processing...";
  });
}
