document.addEventListener("DOMContentLoaded", () => {
  const files = document.querySelectorAll(".file-item");
  const folders = document.querySelectorAll(".folder-item");
  const parentDrop = document.getElementById("parent-drop");
  const uploadDrop = document.getElementById("upload-drop");
  const uploadForm = document.getElementById("upload-form");
  const fileInput = uploadForm
    ? uploadForm.querySelector('input[type="file"]')
    : null;
  const newFolderBtn = document.getElementById("new-folder");
  const folderForm = document.getElementById("folder-form");
  const folderModal = document.getElementById("folder-modal");
  const folderInput = document.getElementById("folder-name-input");
  const folderCreate = document.getElementById("folder-create-btn");
  const folderCancel = document.getElementById("folder-cancel-btn");
  const renameModal = document.getElementById("rename-modal");
  const renameInput = document.getElementById("rename-input");
  const renameConfirm = document.getElementById("rename-confirm-btn");
  const renameCancel = document.getElementById("rename-cancel-btn");
  let renameUrl = "";
  let renameField = "";

  function closeAllMenus() {
    document.querySelectorAll(".file-menu").forEach((m) => {
      if (!m.hasAttribute("hidden")) {
        m.setAttribute("hidden", "");
      }
    });
  }

  files.forEach((item) => {
    item.addEventListener("dragstart", (e) => {
      e.dataTransfer.setData("text/plain", `file:${item.dataset.fileId}`);
    });
    const menuBtn = item.querySelector(".file-menu-btn");
    const menu = item.querySelector(".file-menu");
    if (menuBtn && menu) {
      menuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllMenus();
        if (menu.hasAttribute("hidden")) {
          menu.removeAttribute("hidden");
        } else {
          menu.setAttribute("hidden", "");
        }
      });
      menuBtn.draggable = false;
    }
  });

  folders.forEach((item) => {
    const id = item.dataset.folderId;
    if (id) {
      item.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("text/plain", `folder:${id}`);
      });
    }
    const menuBtn = item.querySelector(".file-menu-btn");
    const menu = item.querySelector(".file-menu");
    if (menuBtn && menu) {
      menuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeAllMenus();
        if (menu.hasAttribute("hidden")) {
          menu.removeAttribute("hidden");
        } else {
          menu.setAttribute("hidden", "");
        }
      });
      menuBtn.draggable = false;
    }
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".file-menu") && !e.target.closest(".file-menu-btn")) {
      closeAllMenus();
    }
  });

  function enableDrop(el, folderId) {
    el.addEventListener("dragover", (e) => {
      e.preventDefault();
      el.classList.add("drag-over");
    });
    el.addEventListener("dragleave", () => {
      el.classList.remove("drag-over");
    });
    el.addEventListener("drop", (e) => {
      e.preventDefault();
      const data = e.dataTransfer.getData("text/plain");
      const [type, id] = data.split(":");
      if (type === "file") {
        moveFile(id, folderId);
      } else if (type === "folder") {
        moveFolder(id, folderId);
      }
      el.classList.remove("drag-over");
    });
  }

  folders.forEach((folder) => enableDrop(folder, folder.dataset.folderId));
  if (parentDrop) enableDrop(parentDrop, parentDrop.dataset.folderId);

  if (uploadDrop) {
    if (fileInput) {
      uploadDrop.addEventListener("click", () => fileInput.click());
      fileInput.addEventListener("change", () => {
        if (!fileInput.files.length) return;
        uploadForm.submit();
      });
    }
    uploadDrop.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadDrop.classList.add("drag-over");
    });
    uploadDrop.addEventListener("dragleave", () => {
      uploadDrop.classList.remove("drag-over");
    });
    uploadDrop.addEventListener("drop", (e) => {
      e.preventDefault();
      const csrf = document.querySelector(
        '#upload-form input[name="csrfmiddlewaretoken"]',
      ).value;
      const file = e.dataTransfer.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file);
      fetch(window.location.pathname + window.location.search, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
        body: formData,
      }).then((res) => {
        if (res.ok) window.location.reload();
      });
      uploadDrop.classList.remove("drag-over");
    });
  }

  if (
    newFolderBtn &&
    folderForm &&
    folderModal &&
    folderInput &&
    folderCreate &&
    folderCancel
  ) {
    newFolderBtn.addEventListener("click", () => {
      folderInput.value = "";
      folderModal.removeAttribute("hidden");
      folderInput.focus();
    });
    folderCancel.addEventListener("click", () => {
      folderModal.setAttribute("hidden", "");
    });
    folderCreate.addEventListener("click", () => {
      const name = folderInput.value.trim();
      if (!name) return;
      const csrf = folderForm.querySelector(
        'input[name="csrfmiddlewaretoken"]',
      ).value;
      const formData = new FormData(folderForm);
      formData.set("name", name);
      fetch(window.location.pathname + window.location.search, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
        body: formData,
      }).then((res) => {
        if (res.ok) window.location.reload();
      });
      folderModal.setAttribute("hidden", "");
    });
    
    folderInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        folderCreate.click();
      } else if (e.key === "Escape") {
        folderCancel.click();
      }
    });
  }

  if (renameModal && renameInput && renameConfirm && renameCancel) {
    document.querySelectorAll(".rename-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        renameUrl = link.dataset.url;
        renameField = link.dataset.field || "name";
        renameInput.value = link.dataset.current || "";
        renameModal.removeAttribute("hidden");
        renameInput.focus();
      });
    });
    renameCancel.addEventListener("click", () => {
      renameModal.setAttribute("hidden", "");
    });
    renameConfirm.addEventListener("click", () => {
      const value = renameInput.value.trim();
      if (!value || !renameUrl) return;
      const csrfEl = document.querySelector(
        'input[name="csrfmiddlewaretoken"]',
      );
      const csrf = csrfEl ? csrfEl.value : "";
      const formData = new FormData();
      formData.set(renameField, value);
      fetch(renameUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
        body: formData,
      }).then((res) => {
        if (res.ok) window.location.reload();
      });
      renameModal.setAttribute("hidden", "");
    });
    
    renameInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        renameConfirm.click();
      } else if (e.key === "Escape") {
        renameCancel.click();
      }
    });
  }

  function moveFile(fileId, targetId) {
    const csrf = document.querySelector(
      '.upload-form input[name="csrfmiddlewaretoken"]',
    ).value;
    fetch(`/move/${fileId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `target_folder=${encodeURIComponent(targetId)}`,
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  }

  function moveFolder(folderId, targetId) {
    const csrf = document.querySelector(
      '.upload-form input[name="csrfmiddlewaretoken"]',
    ).value;
    fetch(`/move_folder/${folderId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `target_folder=${encodeURIComponent(targetId)}`,
    }).then((res) => {
      if (res.ok) {
        window.location.reload();
      }
    });
  }
});
