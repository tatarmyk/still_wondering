"""Markdown rendering with section IDs and custom media extensions.

Each block-level element (paragraph, heading, blockquote, list) gets a stable
section ID based on its position, enabling section-targeted comments.

Custom syntax:
  !youtube[VIDEO_ID](start-end)  → sandboxed YouTube iframe
  !audio[URL]                    → HTML5 <audio> element
"""
import re
import hashlib

import markdown
import bleach

# Allowed HTML tags in rendered output (after Markdown processing)
ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "em", "strong", "a", "br", "hr", "img",
    "div", "span", "section", "iframe", "audio", "source",
    "figure", "figcaption",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "iframe": ["src", "width", "height", "frameborder", "allow",
               "allowfullscreen", "sandbox", "loading"],
    "audio": ["controls", "preload"],
    "source": ["src", "type"],
    "div": ["class", "id", "data-section"],
    "section": ["class", "id", "data-section"],
    "span": ["class", "id"],
    "p": ["id", "data-section"],
    "h1": ["id", "data-section"],
    "h2": ["id", "data-section"],
    "h3": ["id", "data-section"],
    "h4": ["id", "data-section"],
    "h5": ["id", "data-section"],
    "h6": ["id", "data-section"],
    "blockquote": ["id", "data-section"],
    "ul": ["id", "data-section"],
    "ol": ["id", "data-section"],
    "pre": ["id", "data-section"],
}

# YouTube video ID pattern (11 chars, alphanumeric + _ -)
YOUTUBE_RE = re.compile(
    r'!youtube\[([a-zA-Z0-9_-]{11})\](?:\((\d+)?-?(\d+)?\))?'
)

# Audio embed pattern
AUDIO_RE = re.compile(
    r'!audio\[(https?://[^\]]+)\]'
)


def _youtube_replace(match):
    """Replace !youtube[ID](start-end) with sandboxed iframe."""
    video_id = match.group(1)
    start = match.group(2)
    end = match.group(3)

    params = []
    if start:
        params.append(f"start={start}")
    if end:
        params.append(f"end={end}")

    query = "&".join(params)
    src = f"https://www.youtube-nocookie.com/embed/{video_id}"
    if query:
        src += f"?{query}"

    return (
        f'<div class="media-embed media-youtube">'
        f'<iframe src="{src}" width="560" height="315" '
        f'frameborder="0" loading="lazy" '
        f'sandbox="allow-scripts allow-same-origin allow-presentation" '
        f'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" '
        f'allowfullscreen></iframe>'
        f'</div>'
    )


def _audio_replace(match):
    """Replace !audio[URL] with HTML5 audio element."""
    url = match.group(1)
    return (
        f'<div class="media-embed media-audio">'
        f'<audio controls preload="none"><source src="{url}"></audio>'
        f'</div>'
    )


def _process_media(text: str) -> str:
    """Process custom media syntax before Markdown rendering."""
    text = YOUTUBE_RE.sub(_youtube_replace, text)
    text = AUDIO_RE.sub(_audio_replace, text)
    return text


def _add_section_ids(html: str) -> str:
    """Add data-section attributes to block-level elements for commenting."""
    block_tags = r'(<(?:p|h[1-6]|blockquote|ul|ol|pre))([ >])'
    counter = [0]

    def replacer(match):
        tag_start = match.group(1)
        rest = match.group(2)
        counter[0] += 1
        section_id = f"s{counter[0]}"
        return f'{tag_start} id="{section_id}" data-section="{section_id}"{rest}'

    return re.sub(block_tags, replacer, html)


def render_essay(body_md: str) -> str:
    """Render Markdown essay to safe HTML with section IDs and media embeds."""
    # Process custom media syntax first
    text = _process_media(body_md)

    # Render Markdown
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "smarty"],
        output_format="html"
    )

    # Add section IDs for commenting
    html = _add_section_ids(html)

    # Sanitize output (allowlist approach)
    html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )

    return html
