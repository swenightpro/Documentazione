document.addEventListener('DOMContentLoaded', () => {
  const docsBtn = document.getElementById("docs-btn");
  const aboutBtn = document.getElementById("about-btn");
  const docsSection = document.getElementById("docs-section");
  const aboutSection = document.getElementById("about-section");
  const searchInput = document.getElementById('document-search');
  const filtersContainer = document.getElementById("section-filters");
  const container = document.getElementById('sections-container');
  const teamGrid = document.getElementById("team-grid");
  const teamBody = document.getElementById("team-table-body");
  const siteLogo = document.getElementById("site-logo");

  const themeBtn = document.getElementById("theme-button");
  const themeMenu = document.getElementById("theme-menu");

  function setLogo() {
    const dark = document.documentElement.classList.contains("dark-mode");
    siteLogo.src = dark ? "./assets/images/logo_bianco.png" : "./assets/images/logo.png";
  }

  function applyTheme() {
    const sysDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const t = localStorage.theme;

    if (t === "dark" || (!t && sysDark)) {
      document.documentElement.classList.add("dark-mode");
      document.documentElement.classList.remove("light-mode");
      themeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    } else {
      document.documentElement.classList.add("light-mode");
      document.documentElement.classList.remove("dark-mode");
      themeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    }

    if (!t) themeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>';
    setLogo();
  }

  applyTheme();

  themeBtn.onclick = () => themeMenu.classList.toggle("hidden");

  themeMenu.onclick = e => {
    const item = e.target.closest("[data-theme]");
    if (!item) return;
    const mode = item.dataset.theme;

    if (mode === "system") localStorage.removeItem("theme");
    else localStorage.theme = mode;

    themeMenu.classList.add("hidden");
    applyTheme();
  };

  document.addEventListener("click", e => {
    if (!e.target.closest(".theme-wrapper")) themeMenu.classList.add("hidden");
  });

  window.matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      if (!localStorage.theme) applyTheme();
    });

  const teamMembers = [
    {name:"Biasuzzi Davide", git:"biasuzzi-davide", id:"2111000"},
    {name:"Bilato Leonardo", git:"towsatt", id:"2071084"},
    {name:"Ponso Giovanni", git:"sass0lino", id:"2000558"},
    {name:"Zanella Francesco", git:"frazane04", id:"2116442"},
    {name:"Romascu Mihaela-Mariana", git:"Mihaela-Mariana", id:"2079726"},
    {name:"Perozzo Samuele", git:"samuele-perozzo", id:"2110989"},
    {name:"Ogniben Michele", git:"Micheleogniben", id:"2042325"}
  ];

  // Render team as modern card grid
  if (teamGrid) {
    teamMembers.forEach(m => {
      const card = document.createElement("div");
      card.className = "team-card";
      card.innerHTML = `
        <a href="https://github.com/${m.git}" target="_blank" class="tooltip-link" data-tooltip="Apri profilo ${m.name}" style="text-decoration: none; color: inherit; display: block;">
          <img src="https://github.com/${m.git}.png" alt="${m.name}" loading="lazy">
          <div class="member-name">${m.name}</div>
          <div class="member-id">${m.id}</div>
          <div class="member-github">@${m.git}</div>
        </a>
      `;
      teamGrid.appendChild(card);
    });
  }

  // Fallback: also populate the old table (hidden) for compatibility
  if (teamBody) {
    teamMembers.forEach(m => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><img src="https://github.com/${m.git}.png" alt="${m.name}"></td>
        <td>${m.name}</td>
        <td><a href="https://github.com/${m.git}" target="_blank">@${m.git}</a></td>
      `;
      teamBody.appendChild(row);
    });
  }

  const projectBtn = document.getElementById("project-btn");
  const projectSection = document.getElementById("project-section");

  function switchTab(activeBtn, activeSection) {
    [docsBtn, projectBtn, aboutBtn].forEach(b => b.classList.remove("active"));
    [docsSection, projectSection, aboutSection].forEach(s => s.classList.add("hidden"));
    activeBtn.classList.add("active");
    activeSection.classList.remove("hidden");
  }

  docsBtn.onclick = () => switchTab(docsBtn, docsSection);
  projectBtn.onclick = () => switchTab(projectBtn, projectSection);
  aboutBtn.onclick = () => switchTab(aboutBtn, aboutSection);

  let docsTree = {};
  let currentSection = "";

  function getMaxDate(items) {
    let max = "";
    if (!items) return max;
    for (const it of items) {
      if (it.type === 'file' && it.date && it.date > max) {
        max = it.date;
      }
      if (it.children) {
        let cm = getMaxDate(it.children);
        if (cm > max) max = cm;
      }
    }
    return max;
  }

  async function loadDocsTree() {
    const r = await fetch('./docs_tree.json');
    docsTree = await r.json();
    const keys = Object.keys(docsTree);
    if (keys.length) {
      currentSection = keys[0];
      let maxDate = "";
      keys.forEach(sec => {
        let m = getMaxDate(docsTree[sec]);
        if (m > maxDate) { maxDate = m; currentSection = sec; }
      });
    }
    populateFilters();
    if (currentSection) showSection(currentSection);
  }

  function populateFilters() {
    const keys = Object.keys(docsTree);
    filtersContainer.innerHTML = "";
    if (keys.length <= 1) {
      filtersContainer.style.display = "none";
      return;
    }
    filtersContainer.style.display = "flex";
    keys.forEach(sec => {
      const chip = createChip(sec);
      if (sec === currentSection) chip.classList.add("active");
      filtersContainer.appendChild(chip);
    });
  }

  function createChip(name) {
    const chip = document.createElement("div");
    chip.textContent = name;
    chip.className = "filter-chip";
    chip.onclick = () => {
      document.querySelectorAll(".filter-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentSection = name;
      searchInput.value = "";
      showSection(name);
    };
    return chip;
  }

  function buildTree(items) {
    const ul = document.createElement("ul");
    items.forEach(item => {
      const li = document.createElement("li");
      if (item.type === "folder") {
        const t = document.createElement("div");
        t.className = "folder-toggle";
        t.textContent = item.name;
        const cont = document.createElement("div");
        cont.className = "folder-content";
        if (item.children?.length) cont.appendChild(buildTree(item.children));
        li.append(t, cont);
      } else {
        const row = document.createElement("div");
        row.className = "pdf_row";
        const version = item.version ? ` v${item.version.replace(/^v+/, "")}` : "";
        const date = (item.name.toLowerCase().startsWith("verbale") && item.date) ? ` ${item.date}` : "";
        const signed = item.signed ? `<span class="signed-badge">Firmato</span>` : "";
        const link = document.createElement("a");
        link.className = "file-name";
        link.href = item.path;
        link.target = "_blank";
        link.innerHTML = `<img src="./assets/images/pdf.svg" class="icon-pdf"> ${item.name}${date}${version} ${signed}`;
        const dl = document.createElement("a");
        dl.href = item.path;
        dl.download = "";
        dl.className = "download-button";
        row.append(link, dl);
        li.appendChild(row);
      }
      ul.appendChild(li);
    });
    return ul;
  }

function showSection(name, filtered=null) {
  container.innerHTML = "";

  const source = filtered || docsTree;
  const sections = name === "Tutto" ? Object.keys(source) : [name];

  sections.forEach(section => {
    const wrapper = document.createElement("div");

    const toggle = document.createElement("div");
    toggle.className = "folder-toggle";
    toggle.textContent = section;

    const content = document.createElement("div");
    content.className = "folder-content";

    const treeData = filtered ? source[section] : docsTree[section];
    content.appendChild(buildTree(treeData));

    wrapper.append(toggle, content);
    container.appendChild(wrapper);
  });

  document.querySelectorAll(".folder-content").forEach(c => c.classList.remove("collapsed"));
  document.querySelectorAll(".folder-toggle").forEach(t => t.classList.remove("collapsed"));

  searchInput.placeholder = name === "Tutto" ? "Cerca in Documentazione..." : `Cerca in ${name}...`;
}


  document.body.addEventListener("click", e => {
    const t = e.target.closest(".folder-toggle");
    if (!t) return;
    t.classList.toggle("collapsed");
    t.nextElementSibling.classList.toggle("collapsed");
  });

  function normalizeQuery(q) { return q.replace(/[-/.]/g, " ").trim(); }
  function filterTree(items, qRaw) {
    const words = normalizeQuery(qRaw.toLowerCase()).split(/\s+/).filter(Boolean);
    const out = [];
    for (const it of items) {
      if (it.type === "file") {
        let text = (it.search_name || it.name || "").toLowerCase();
        if (it.date) text += " " + it.date.replace(/-/g, " ");
        let ok = true, tmp = text;
        for (const w of words) {
          const i = tmp.indexOf(w);
          if (i === -1) { ok = false; break; }
          tmp = tmp.slice(0,i)+tmp.slice(i+w.length);
        }
        if (ok) out.push(it);
      } else {
        const kids = filterTree(it.children || [], qRaw);
        if (kids.length) out.push({...it, children:kids});
      }
    }
    return out;
  }

  searchInput.oninput = () => {
    const q = searchInput.value.trim();
    if (!q) return showSection(currentSection);
    const sections = currentSection === "Tutto" ? Object.keys(docsTree) : [currentSection];
    let results = {}, count=0;
    sections.forEach(sec=>{
      const f = filterTree(docsTree[sec], q);
      if (f.length) results[sec]=f, count+=f.length;
    });
    if (!count) {
      container.innerHTML = `<p style="text-align:center;margin-top:2rem;color:var(--muted);font-style:italic;">Nessun risultato trovato.</p>`;
      return;
    }
    showSection(currentSection, results);
  };

  loadDocsTree();
});
