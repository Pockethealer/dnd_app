// Function to render the tree recursively
export function renderPageTree(tree, parentElement) {
  const ul = document.createElement('ul');
  tree.forEach(node => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `/wiki/${node.slug}`;
    a.textContent = node.title;
    li.appendChild(a);

    if (node.children && node.children.length > 0) {
      renderPageTree(node.children, li);  // recursion for children
    }

    ul.appendChild(li);
  });
  parentElement.appendChild(ul);
}