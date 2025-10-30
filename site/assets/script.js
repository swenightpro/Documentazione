document.addEventListener('DOMContentLoaded', () => {
    const nav = document.getElementById('nav-navigation');
    const container = document.getElementById('sections-container');
    const searchInput = document.getElementById('document-search');
    const searchContainer = document.getElementById('search-container');
    const sectionsWrapper = document.getElementById('sections-wrapper');

    let docsTree = {};
    let currentSection = null;

    async function loadDocsTree() {
        try {
            const res = await fetch('./docs_tree.json');
            docsTree = await res.json();
            buildNavigation();
            showSection('Archivio');
        } catch (err) {
            container.innerHTML = `<p style="color:#888;">Errore nel caricamento dei documenti.</p>`;
        }
    }

    function buildNavigation() {
        nav.innerHTML = '';

        const ArchivioLi = document.createElement('li');
        const ArchivioA = document.createElement('a');
        ArchivioA.href = '#';
        ArchivioA.dataset.section = 'Archivio';
        ArchivioA.textContent = 'Archivio';
        ArchivioA.classList.add('active', 'show-arrow');
        ArchivioLi.appendChild(ArchivioA);
        nav.appendChild(ArchivioLi);

        Object.keys(docsTree).forEach(section => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = '#';
            a.dataset.section = section;
            a.textContent = section;
            li.appendChild(a);
            nav.appendChild(li);
        });

        if (nav.children.length <= 2) {
            nav.classList.add('hidden_button');
            document.querySelector('header').classList.add('center-logo');
        }
    }

    function buildTree(items, currentPath = '') {
        const ul = document.createElement('ul');

        items.forEach(item => {
            const li = document.createElement('li');
            const fullPath = currentPath ? `${currentPath}/${item.name}` : item.name;

            if (item.type === 'folder') {
                const folderToggle = document.createElement('div');
                folderToggle.className = 'folder-toggle';
                const label = document.createElement('span');
                label.className = 'toggle-data';
                label.textContent = item.name;
                folderToggle.appendChild(label);

                const content = document.createElement('div');
                content.className = 'folder-content';

                if (item.children?.length > 0) {
                    content.appendChild(buildTree(item.children, fullPath));
                }

                li.append(folderToggle, content);
            } else {
                const p = document.createElement('p');
                p.className = 'pdf_row';
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';

                const link = document.createElement('a');
                link.className = 'file-name';
                link.href = item.path;
                link.target = '_blank';

                const readableName = item.name;
                const versionLabel = item.version ? ` ${item.version}` : '';
                const dateLabel = item.date ? ` ${item.date}` : '';
                const signedLabel = item.signed ? ' <span class="signed-badge">Firmato</span>' : '';

                link.innerHTML = `${readableName}${dateLabel}${versionLabel}${signedLabel}`;
                link.dataset.fullPath = fullPath;

                fileInfo.appendChild(link);

                const download = document.createElement('a');
                download.className = 'download-button';
                download.href = item.path;
                download.download = '';
                download.title = 'Scarica file';

                p.append(fileInfo, download);
                li.appendChild(p);
            }

            ul.appendChild(li);
        });

        const wrapper = document.createElement('div');
        wrapper.className = 'dynamic-content-container';
        wrapper.appendChild(ul);
        return wrapper;
    }

    function showSection(name, filtered = null) {
        currentSection = name;
        container.innerHTML = '';
        document.querySelectorAll('.file-path').forEach(p => p.remove());

        document.querySelectorAll('#nav-navigation a').forEach(a => {
            const active = a.dataset.section === name;
            a.classList.toggle('active', active);
            a.classList.toggle('show-arrow', active);
        });

        searchInput.placeholder = name === 'Archivio' ? 'Cerca…' : `Cerca in ${name}…`;

        if (!sectionsWrapper.contains(searchContainer)) {
            sectionsWrapper.insertBefore(searchContainer, container);
        }

        if (name === 'Archivio') {
            let title = sectionsWrapper.querySelector('.repo-title');
            if (!title) {
                title = document.createElement('h1');
                title.className = 'repo-title';
                title.textContent = 'Documentazione di Progetto';
                sectionsWrapper.insertBefore(title, searchContainer);
            }

            const source = filtered || docsTree;
            Object.keys(source).forEach(section => {
                const sectionContainer = document.createElement('div');
                const toggle = document.createElement('div');
                toggle.className = 'folder-toggle';
                const label = document.createElement('span');
                label.className = 'toggle-data';
                label.textContent = section;
                toggle.appendChild(label);

                const content = document.createElement('div');
                content.className = 'folder-content';
                content.appendChild(buildTree(source[section], section));

                sectionContainer.append(toggle, content);
                container.appendChild(sectionContainer);
            });
        } else {
            const oldTitle = sectionsWrapper.querySelector('.repo-title');
            if (oldTitle) oldTitle.remove();

            const rootToggle = document.createElement('div');
            rootToggle.className = 'folder-toggle';
            const label = document.createElement('span');
            label.className = 'toggle-data';
            label.textContent = name;
            rootToggle.appendChild(label);

            const content = document.createElement('div');
            content.className = 'folder-content';
            const treeData = filtered ? filtered[name] : docsTree[name];
            content.appendChild(buildTree(treeData, name));

            container.append(rootToggle, content);
        }
    }

    function filterTree(items, query) {
        const results = [];
        for (const item of items) {
            if (item.type === 'file') {
                const text = (item.search_name || item.name).toLowerCase();
                
                const words = query.split(/\s+/).filter(Boolean);
                            
                let remainingText = text;
                let match = true;
                            
                for (const w of words) {
                    const idx = remainingText.indexOf(w);
                    if (idx === -1) {
                        match = false;
                        break;
                    }
                    remainingText =
                        remainingText.slice(0, idx) + remainingText.slice(idx + w.length);
                }
                
                if (match) results.push(item);



            } else if (item.type === 'folder' && item.children?.length) {
                const filteredChildren = filterTree(item.children, query);
                if (filteredChildren.length > 0) {
                    results.push({ ...item, children: filteredChildren });
                }
            }
        }
        return results;
    }

    document.body.addEventListener('click', e => {
        const toggle = e.target.closest('.folder-toggle');
        if (!toggle) return;
        toggle.classList.toggle('collapsed');
        const next = toggle.nextElementSibling;
        if (next?.classList.contains('folder-content')) {
            next.classList.toggle('collapsed');
        }
    });

    nav.addEventListener('click', e => {
        const link = e.target.closest('a[data-section]');
        if (!link) return;
        e.preventDefault();
        searchInput.value = '';
        showSection(link.dataset.section);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        const msgOld = container.querySelector('.no-results-message');
        if (msgOld) msgOld.remove();

        if (query === '') {
            showSection(currentSection);
            searchInput.focus();
            return;
        }

        let filteredData = {};
        let matchCount = 0;

        if (currentSection === 'Archivio') {
            Object.keys(docsTree).forEach(section => {
                const filtered = filterTree(docsTree[section], query);
                if (filtered.length > 0) {
                    filteredData[section] = filtered;
                    matchCount += filtered.length;
                }
            });
        } else {
            const filtered = filterTree(docsTree[currentSection], query);
            if (filtered.length > 0) {
                filteredData[currentSection] = filtered;
                matchCount = filtered.length;
            }
        }

        container.innerHTML = '';

        if (matchCount === 0) {
            const msg = document.createElement('p');
            msg.className = 'no-results-message';
            msg.textContent = 'Nessun risultato trovato.';
            msg.style.textAlign = 'center';
            msg.style.color = '#777';
            msg.style.fontStyle = 'italic';
            msg.style.marginTop = '2rem';
            container.appendChild(msg);
            searchInput.focus();
            return;
        }

        showSection(currentSection, filteredData);
        searchInput.focus();
    });

    loadDocsTree();
});
