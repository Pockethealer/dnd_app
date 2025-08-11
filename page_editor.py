from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Page
import markdown
import bleach
import re
from slugify import slugify


page_editor = Blueprint('page_editor', __name__)

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + ["p", "pre", "span", "h1", "h2", "h3", "table", "thead", "tbody", "tr", "td", "th"]
# Mapping from style keywords to CSS properties
STYLE_MAP = {
    'bold': 'font-weight: bold',
    'italic': 'font-style: italic',
    'crossed': 'text-decoration: line-through',
    'underline': 'text-decoration: underline',
    # colors will be handled separately
}

@page_editor.route('/edit/', defaults={'slug': None})
@page_editor.route('/edit/<slug>')
@login_required
def edit_page(slug):
    page = None
    if slug:
        page = Page.query.filter_by(slug=slug).first_or_404()
    pages = Page.query.all()
    return render_template("page_editor.html", page=page, all_pages=pages, user=current_user)



def markdown_to_html(markdown_text):
    extensions = [
        "extra",          # Tables, fenced code blocks, etc.
        "abbr",           # Abbreviations
        "attr_list",      # Attribute lists
        "def_list",       # Definition lists
        "fenced_code",    # Triple backtick code blocks
        "footnotes",      # Footnotes support
        "tables",         # Tables support
        "toc",            # Table of contents
    ]
    # Convert Markdown to HTML
    text=expand_images(markdown_text)
    html = markdown.markdown(
        text,
        extensions=extensions,
        output_format="html5"
    )
    html = expand_styling(html)
    html_clean=html
    #html_clean=sanitize_html(html)
    html_clean=expand_custom_links(html_clean)
    return html_clean


def expand_custom_links(md_text):
    pattern_no_text = re.compile(r'\[\/(\w+)\/([\w\s-]+)\]')
    
    def replacer_no_text(match):
        model = match.group(1)
        raw_name = match.group(2)
        slug_name = slugify(raw_name)
        display_text = raw_name.title()
        return f'<a href="#" class="link" data-name="{slug_name}" data-model="{model}">{display_text}</a>'
    
    return pattern_no_text.sub(replacer_no_text, md_text)


def expand_styling(text):
    pattern = re.compile(r'\{([^}]+)\}:\s*([\w\s,]+)')

    def replacer(match):
        content = match.group(1)
        styles = [s.strip().lower() for s in match.group(2).split(',')]
        
        css_styles = []
        for style in styles:
            if style in STYLE_MAP:
                css_styles.append(STYLE_MAP[style])
            else:
                # Assume any style not in map is a color name
                css_styles.append(f'color: {style}')
        
        style_attr = '; '.join(css_styles)
        return f'<span style="{style_attr}">{content}</span>'
    
    return pattern.sub(replacer, text)


def add_unit(val):
    if not val:
        return None
    return val if val.endswith('%') else val + 'px'

def expand_images(md_text):
    pattern = r'!\[(.*?)\]\((.*?)\)(?::(\d*%?)x(\d*%?)(?:,\s*(left|right|center))?)?'

    def repl(match):
        alt_text = match.group(1)
        url = match.group(2)
        width = match.group(3)
        height = match.group(4)
        align = match.group(5)

        styles = []
        w = add_unit(width)
        h = add_unit(height)
        if w:
            styles.append(f'width:{w};')
        if h:
            styles.append(f'height:{h};')

        if align:
            if align in ['left', 'right']:
                styles.append(f'float:{align};')
            elif align == 'center':
                styles.append('display:block; margin-left:auto; margin-right:auto;')

        style_str = ' '.join(styles)

        if style_str:
            return f'<img src="{url}" alt="{alt_text}" style="{style_str}"/>'
        else:
            return f'<img src="{url}" alt="{alt_text}"/>'

    return re.sub(pattern, repl, md_text)



def sanitize_html(html):
    return bleach.clean(html, tags=ALLOWED_TAGS, strip=True)