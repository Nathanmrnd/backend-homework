document.addEventListener("DOMContentLoaded", () => {
  // Pour chaque checkbox "done-toggle"
  document.querySelectorAll(".done-toggle").forEach((checkbox) => {
    // Initialiser la classe sur la note en fonction de la checkbox
    toggleDoneClass(checkbox);

    // Écouter les changements
    checkbox.addEventListener("change", (event) => {
      toggleDoneClass(checkbox);

      // Ici tu peux appeler ton API pour sauvegarder l'état, par exemple :
      const done = checkbox.checked;
      const id = checkbox.dataset.id;
      fetch(`/api/notes/${id}/done`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ done }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.ok) {
            console.log("Note mise à jour");
          } else {
            console.error("Erreur lors de la mise à jour");
          }
        });
    });
  });
});

// Fonction pour ajouter ou enlever la classe done sur la note
function toggleDoneClass(checkbox) {
  const noteDiv = checkbox.closest(".note");
  if (checkbox.checked) {
    noteDiv.classList.add("done");
  } else {
    noteDiv.classList.remove("done");
  }
}
