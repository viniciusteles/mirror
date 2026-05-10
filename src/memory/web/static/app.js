const tree = document.querySelector('#docs-tree');
const content = document.querySelector('#content');
const currentPath = document.querySelector('#current-path');
let currentDocPath = null;

async function loadTree() {
  const response = await fetch('/api/docs/tree');
  const nodes = await response.json();

  tree.innerHTML = '';
  const list = document.createElement('ul');
  list.className = 'doc-tree';
  for (const node of nodes) {
    list.appendChild(renderNode(node, 0));
  }
  tree.appendChild(list);

  const firstFile = findFirstFile(nodes);
  if (firstFile) {
    await loadDoc(firstFile.path);
  }
}

function renderNode(node, depth = 0) {
  const item = document.createElement('li');
  item.className = `tree-node ${node.type}`;

  if (node.type === 'directory') {
    const details = document.createElement('details');
    details.open = depth === 0;
    const summary = document.createElement('summary');
    summary.textContent = node.title;
    if (node.path) {
      summary.title = node.path;
      summary.addEventListener('click', () => loadDoc(node.path));
    }
    details.appendChild(summary);

    const list = document.createElement('ul');
    for (const child of node.children || []) {
      list.appendChild(renderNode(child, depth + 1));
    }
    details.appendChild(list);
    item.appendChild(details);
    return item;
  }

  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = node.title;
  button.title = node.path;
  button.addEventListener('click', () => loadDoc(node.path));
  item.appendChild(button);
  return item;
}

function findFirstFile(nodes) {
  for (const node of nodes) {
    if (node.type === 'file') return node;
    const found = findFirstFile(node.children || []);
    if (found) return found;
  }
  return null;
}

async function loadDoc(path) {
  const response = await fetch(`/api/docs/file?path=${encodeURIComponent(path)}`);
  const doc = await response.json();

  if (!response.ok) {
    currentPath.textContent = path;
    content.innerHTML = `<pre>${escapeHtml(doc.error || 'Could not load document')}</pre>`;
    return;
  }

  currentDocPath = doc.path;
  currentPath.textContent = doc.path;
  content.innerHTML = doc.html;
}

content.addEventListener('click', async (event) => {
  const link = event.target.closest('a');
  if (!link || !currentDocPath) return;

  const href = link.getAttribute('href');
  if (!href || isExternalLink(href) || href.startsWith('#')) return;

  const resolved = resolveDocHref(currentDocPath, href);
  if (!resolved || !resolved.path.endsWith('.md')) return;

  event.preventDefault();
  await loadDoc(resolved.path);
  if (resolved.hash) {
    document.querySelector(resolved.hash)?.scrollIntoView();
  }
});

function isExternalLink(href) {
  return /^(https?:|mailto:|tel:)/.test(href);
}

function resolveDocHref(basePath, href) {
  const [rawPath, rawHash] = href.split('#');
  if (!rawPath) return null;

  const baseParts = basePath.split('/');
  baseParts.pop();
  const parts = rawPath.startsWith('/') ? [] : baseParts;

  for (const part of rawPath.split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') {
      parts.pop();
    } else {
      parts.push(part);
    }
  }

  return {
    path: parts.join('/'),
    hash: rawHash ? `#${CSS.escape(rawHash)}` : null,
  };
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

loadTree().catch((error) => {
  content.innerHTML = `<pre>${escapeHtml(String(error))}</pre>`;
});
