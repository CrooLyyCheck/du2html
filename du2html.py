import sys
import json

def parse_du_output(filename):
    """
    Parses the du output file with lines: <size><TAB><path>
    Builds a nested dictionary tree with sizes.
    """
    tree = {}
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # Skip noisy lines like "nohup: ignoring input"
            if "ignoring" in line or "nohup:" in line:
                continue
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            size, path = parts
            path = path.lstrip("/")
            if not path:
                continue
            node = tree
            components = path.split("/")
            for c in components[:-1]:
                node = node.setdefault(c, {"_children": {}, "_size": None})
                node = node["_children"]
            leaf = node.setdefault(components[-1], {"_children": {}, "_size": None})
            leaf["_size"] = size
    return tree

def to_js_tree_format(tree):
    """
    Converts internal tree format to a simple JSON-compatible dict
    """
    js_tree = {}
    for key, val in tree.items():
        js_tree[key] = {
            "size": val["_size"],
            "children": to_js_tree_format(val["_children"])
        }
    return js_tree

def render_html_level(tree, level=0):
    """
    Renders only the first level of tree as HTML list with toggle buttons.
    """
    html = '<ul class="list-group ms-{}">'.format(level * 3)
    for key, val in sorted(tree.items()):
        size = val["_size"] if val["_size"] is not None else ""
        has_children = bool(val["_children"])
        if has_children:
            html += (
                f'<li class="list-group-item">'
                f'<button class="btn btn-sm btn-outline-primary me-1 toggle-btn" '
                f'type="button" aria-expanded="false" data-key="{key}">+</button>'
                f'<span class="folder fw-bold">{key}/</span>'
                f'<span class="badge bg-secondary ms-2">{size}</span>'
                f'<div class="children-container ms-3" style="display:none;"></div>'
                '</li>'
            )
        else:
            html += (
                f'<li class="list-group-item">'
                f'<span class="file">{key}</span>'
                f'<span class="badge bg-light text-dark ms-2">{size}</span>'
                '</li>'
            )
    html += '</ul>'
    return html

def main():
    if len(sys.argv) != 3:
        print("Usage: python du2html.py input.txt output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    tree = parse_du_output(input_file)
    js_tree = to_js_tree_format(tree)
    first_level_html = render_html_level(tree)

    json_data = json.dumps(js_tree)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>du output visualization (lazy loading)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background: #f6f8fa; }}
.folder {{ color: #084298; cursor: pointer; }}
.file {{ color: #212529; }}
ul.list-group {{ margin-bottom: 0; }}
li.list-group-item {{ border: none; border-radius: 0; background: #fff; }}
li.list-group-item:hover {{ background: #f0f4fa; }}
.toggle-btn {{
    width: 32px; height: 32px; padding: 0; font-weight: bold;
    vertical-align: middle;
    user-select:none;
}}
.children-container {{
    margin-top: 5px;
}}
</style>
</head>
<body>
<div class="container mt-4 mb-5">
    <div class="card shadow">
        <div class="card-header bg-primary text-white"><h3 class="mb-0">Directory Structure from du output</h3></div>
        <div class="card-body">
            <div class="alert alert-info mb-3">Click the <b>+</b> button next to a folder to expand subfolders.</div>
            {first_level_html}
        </div>
    </div>
</div>

<!-- Full tree structure in JSON -->
<script id="tree-data" type="application/json">
{json_data}
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
// Parse tree JSON data
const treeData = JSON.parse(document.getElementById("tree-data").textContent);

// Function to recursively render a subtree (HTML)
function renderSubtree(node) {{
    let html = '<ul class="list-group ms-3">';
    for (const [key, val] of Object.entries(node)) {{
        const size = val.size || "";
        const children = val.children || {{}};
        const hasChildren = Object.keys(children).length > 0;
        if (hasChildren) {{
            html += `<li class="list-group-item">
                <button class="btn btn-sm btn-outline-primary me-1 toggle-btn" type="button" aria-expanded="false" data-key="${{key}}">+</button>
                <span class="folder fw-bold">${{key}}/</span>
                <span class="badge bg-secondary ms-2">${{size}}</span>
                <div class="children-container ms-3" style="display:none;"></div>
            </li>`;
        }} else {{
            html += `<li class="list-group-item">
                <span class="file">${{key}}</span>
                <span class="badge bg-light text-dark ms-2">${{size}}</span>
            </li>`;
        }}
    }}
    html += '</ul>';
    return html;
}}

// Returns subtree object by walking the path array
function getSubtreeByPath(pathArray) {{
    let node = treeData;
    for (const part of pathArray) {{
        if (node && node[part]) {{
            node = node[part].children;
        }} else {{
            return null;
        }}
    }}
    return node;
}}

// Event delegation for toggle buttons
document.addEventListener('click', function(event) {{
    if (event.target.classList.contains('toggle-btn')) {{
        const btn = event.target;
        const li = btn.parentElement;
        const container = li.querySelector('.children-container');

        if (container.style.display === 'none') {{
            if (!container.hasChildNodes()) {{
                // Build path array by traversing up the tree
                let path = [];
                let currentLi = li;
                while (currentLi && currentLi.tagName === 'LI') {{
                    let folderSpan = currentLi.querySelector('span.folder');
                    if (folderSpan) {{
                        let name = folderSpan.textContent.replace(/\/$/, '');
                        path.unshift(name);
                    }}
                    currentLi = currentLi.parentElement.closest('li');
                }}
                const subtree = getSubtreeByPath(path);
                if (subtree) {{
                    container.innerHTML = renderSubtree(subtree);
                }} else {{
                    container.innerHTML = '<div class="text-muted fst-italic">No subfolders.</div>';
                }}
            }}
            container.style.display = 'block';
            btn.textContent = '-';
            btn.setAttribute('aria-expanded', 'true');
        }} else {{
            container.style.display = 'none';
            btn.textContent = '+';
            btn.setAttribute('aria-expanded', 'false');
        }}
    }}
}});
</script>

</body>
</html>
''')

if __name__ == "__main__":
    main()
