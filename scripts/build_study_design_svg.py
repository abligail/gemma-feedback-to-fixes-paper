"""Build the authored Study B Figure 1 SVG using the standard library.

The final R03/R04 budget is checked before writing. All shapes and text are
native vectors. PNG and PDF exports are fingerprinted separately so the
default paper rebuild does not require a browser or an image-generation API.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def el(parent, tag, **attrs):
    node = ET.SubElement(parent, f"{{{NS}}}{tag}")
    node.attrib.update({key.replace("_", "-"): str(value) for key, value in attrs.items()})
    return node


def group(parent, name=None, **attrs):
    if name:
        attrs["id"] = name
    return el(parent, "g", **attrs)


def rect(parent, x, y, w, h, fill, stroke="none", sw=0, rx=0, **attrs):
    return el(parent, "rect", x=x, y=y, width=w, height=h, rx=rx,
              fill=fill, stroke=stroke, stroke_width=sw, **attrs)


def path(parent, d, stroke, sw=3, fill="none", **attrs):
    return el(parent, "path", d=d, fill=fill, stroke=stroke,
              stroke_width=sw, stroke_linecap="round", stroke_linejoin="round", **attrs)


def line(parent, x1, y1, x2, y2, stroke, sw=3, **attrs):
    return el(parent, "line", x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke,
              stroke_width=sw, stroke_linecap="round", **attrs)


def circle(parent, cx, cy, r, fill, stroke="none", sw=0, **attrs):
    return el(parent, "circle", cx=cx, cy=cy, r=r, fill=fill,
              stroke=stroke, stroke_width=sw, **attrs)


def text(parent, x, y, content, size=25, weight=400, anchor="start", fill="#10151b", **attrs):
    node = el(parent, "text", x=x, y=y, font_size=size, font_weight=weight,
              text_anchor=anchor, fill=fill, **attrs)
    node.text = content
    return node


def use(parent, name, x, y, w, h, color=None):
    attrs = {"href": f"#{name}", "x": x, "y": y, "width": w, "height": h}
    if color:
        attrs["color"] = color
    return el(parent, "use", **attrs)


SLATE = "#405778"
BLUE = "#147cf2"
TEAL = "#00a3ac"
ORANGE = "#ff6c19"
PURPLE = "#8742eb"
MUTED = "#abb6c5"
INK = "#102338"


svg = ET.Element(f"{{{NS}}}svg", {
    "width": "1536", "height": "1024", "viewBox": "0 0 1536 1024",
    "version": "1.1", "role": "img", "aria-labelledby": "figure-title figure-desc",
})
el(svg, "title", id="figure-title").text = "Study B: shared frozen draft and matched continuation arms"
el(svg, "desc", id="figure-desc").text = (
    "R03/R04 design. Generate and freeze draft D. A read-only constructor proposes a "
    "public check and expected outcome using at most one file read. Run the check on D "
    "at most once, with a 30-second timeout, when available. C and F share D, the public "
    "issue, the check specification and the expected outcome. Only F receives the "
    "precomputed output or unavailable notice in advance. Both arms have the same tools "
    "and budgets, fresh contexts, matched seed, and no draft conversation history."
)
defs = el(svg, "defs")
el(defs, "style").text = (
    "text{font-family:Arial,'Liberation Sans',Helvetica,sans-serif;}"
    "svg{shape-rendering:geometricPrecision;text-rendering:geometricPrecision;}"
)


def marker(name, color):
    node = el(defs, "marker", id=name, viewBox="0 0 18 20", refX=17, refY=10,
              markerWidth=18, markerHeight=20, markerUnits="userSpaceOnUse", orient="auto")
    el(node, "path", d="M 0 0 L 18 10 L 0 20 Z", fill=color)


marker("arrow-neutral", INK)
marker("arrow-result", ORANGE)


def document(parent, x, y, w, h, stroke=SLATE, sw=3.3, fill="#fcfdff", fold=24,
             fold_stroke="#98a8bd", fold_fill="#e4ebf5"):
    d = (f"M {x+7} {y} H {x+w-fold} L {x+w} {y+fold} V {y+h-7} "
         f"Q {x+w} {y+h} {x+w-7} {y+h} H {x+7} Q {x} {y+h} {x} {y+h-7} "
         f"V {y+7} Q {x} {y} {x+7} {y} Z")
    path(parent, d, stroke, sw, fill)
    path(parent, f"M {x+w-fold} {y} V {y+fold} H {x+w}", fold_stroke, sw-0.4, fold_fill)


def code_glyph(parent, x, y, color, size=37, sw=5):
    path(parent, f"M {x+9} {y-size/3} L {x} {y} L {x+9} {y+size/3}", color, sw)
    line(parent, x+20, y+size*0.43, x+30, y-size*0.43, color, sw)
    path(parent, f"M {x+41} {y-size/3} L {x+50} {y} L {x+41} {y+size/3}", color, sw)


def lock(parent, x, y, r, color):
    circle(parent, x, y, r, color, "#ffffff", 5)
    rect(parent, x-r*0.40, y-r*0.12, r*0.8, r*0.72, "#ffffff", rx=3)
    path(parent, f"M {x-r*0.24} {y-r*0.13} V {y-r*0.34} "
                 f"A {r*0.24} {r*0.24} 0 0 1 {x+r*0.24} {y-r*0.34} V {y-r*0.13}", "#ffffff", 4)
    circle(parent, x, y+r*0.16, r*0.08, color)
    line(parent, x, y+r*0.20, x, y+r*0.37, color, 3)


def clipped_card(parent, name, x, y, w, h, border, header, band, header_h=60, band_h=40, rx=18):
    clip = el(defs, "clipPath", id=f"clip-{name}")
    rect(clip, x, y, w, h, "#ffffff", rx=rx)
    card = group(parent, name)
    inside = group(card, clip_path=f"url(#clip-{name})")
    rect(inside, x, y, w, h, "#fcfdff")
    rect(inside, x, y, w, header_h, header)
    rect(inside, x, y+header_h, w, band_h, band)
    # The entire frame is one rect: the top edge cannot form a bump near the badge.
    rect(card, x, y, w, h, "none", border, 2, rx=rx, id=f"border-{name}")
    return card


# Reusable vector icons make both continuation arms visually and semantically matched.
agent = el(defs, "symbol", id="agent-laptop", viewBox="0 0 140 115")
el(agent, "ellipse", cx=72, cy=107, rx=69, ry=4, fill="#d2dee7")
line(agent, 54, 19, 54, 12, "#243c50", 4)
circle(agent, 54, 8, 6.3, "currentColor", "#243c50", 3.6)
rect(agent, 23, 33, 15, 24, "currentColor", "#243c50", 3.7, rx=6)
rect(agent, 68, 33, 15, 24, "currentColor", "#243c50", 3.7, rx=6)
rect(agent, 33, 23, 42, 43, "#fcfdff", "#243c50", 3.8, rx=14)
path(agent, "M 21 106 V 89 Q 22 71 43 71 H 63 Q 79 75 80 92 V 106 Z", "#243c50", 3.8, "#fcfdff")
line(agent, 36, 87, 36, 105, "#243c50", 3.8)
path(agent, "M 84 66 H 133 L 121 106 H 71 Z", "#243c50", 3.8, "#9cabb9")
circle(agent, 107, 87, 3.6, "#eef4fa")

inspect = el(defs, "symbol", id="tool-inspect", viewBox="0 0 76 80")
document(inspect, 12, 9, 45, 61, fold=15, sw=3.5)
for yy, length in [(26, 19), (37, 18), (49, 13)]:
    line(inspect, 23, yy, 23+length, yy, BLUE, 4)
circle(inspect, 53, 52, 11.5, "#f7fbff", BLUE, 4)
line(inspect, 61, 61, 72, 72, BLUE, 4.6)

edit = el(defs, "symbol", id="tool-edit", viewBox="0 0 76 80")
document(edit, 12, 9, 45, 61, fold=15, sw=3.5)
for yy, length in [(26, 20), (38, 18), (49, 11)]:
    line(edit, 23, yy, 23+length, yy, BLUE, 4)
path(edit, "M 40 62 L 44 49 L 63 30 Q 65 28 67 30 L 73 36 Q 75 38 73 40 L 54 59 Z", "#274b73", 2.6, "#65a8f4")
line(edit, 60, 34, 70, 44, "#274b73", 2.7)
line(edit, 45, 51, 53, 58, "#274b73", 2.5)
path(edit, "M 40 62 L 44 49 L 54 59 Z", "#274b73", 1.8, "#e1ecfa")

run = el(defs, "symbol", id="tool-run", viewBox="0 0 76 80")
rect(run, 2, 9, 72, 64, "#2b4053", rx=7)
path(run, "M 18 30 L 29 41 L 18 52", "#ffffff", 4)
line(run, 37, 52, 48, 52, "#ffffff", 4)

result_icon = el(defs, "symbol", id="result-document", viewBox="0 0 68 90")
document(result_icon, 4, 3, 58, 83, stroke=ORANGE, sw=3.5, fold=21, fill="#fffaf4",
         fold_stroke=ORANGE, fold_fill="#ffe8d1")
for yy, length in [(27, 14), (41, 30), (55, 27), (69, 21)]:
    line(result_icon, 17, yy, 17+length, yy, ORANGE, 4)

rect(svg, 0, 0, 1536, 1024, "#ffffff", id="canvas")
text(svg, 37, 38, "Study B | R03/R04", 28, 700, fill="#0b1930", id="study-label")

# Independent route groups make the F-only result channel explicit and editable.
routes = group(svg, "information-routes")
line(routes, 467, 211, 560, 211, INK, 3.2, marker_end="url(#arrow-neutral)", id="draft-to-proposal")
line(routes, 968, 211, 1073, 211, INK, 3.2, marker_end="url(#arrow-neutral)", id="proposal-to-execution")
path(routes, "M 266 328 V 347 Q 266 357 276 357 H 758 Q 768 357 768 367", INK, 3.1, id="draft-to-shared")
line(routes, 768, 328, 768, 390, INK, 3.1, marker_end="url(#arrow-neutral)", id="proposal-to-shared")
path(routes, "M 768 621 V 634", INK, 3.1, id="shared-to-split")
path(routes, "M 768 634 H 430 Q 424 634 424 640 V 665", INK, 3.1,
     marker_end="url(#arrow-neutral)", id="shared-to-C")
path(routes, "M 768 634 H 1096 Q 1102 634 1102 640 V 665", INK, 3.1,
     marker_end="url(#arrow-neutral)", id="shared-to-F")
line(routes, 1314, 328, 1314, 442, ORANGE, 3.1,
     marker_end="url(#arrow-result)", id="execution-to-result")
line(routes, 1314, 567, 1314, 665, ORANGE, 3.1,
     marker_end="url(#arrow-result)", id="result-to-F-only")

# Three preparation panels, preserving the approved positions and illustration types.
draft = clipped_card(svg, "stage-draft", 66, 60, 400, 268, "#006cff", "#cce4ff", "#eff6ff")
circle(draft, 116, 90, 23, "#125ba6", id="badge-stage-1")
text(draft, 116, 101, "1", 31, 700, "middle", "#ffffff")
text(draft, 160, 101, "Generate & freeze D", 26.5, 700, id="label-stage-1")
text(draft, 266, 148, "240 s | 16 tool calls", 23, anchor="middle", fill="#34495b", id="budget-draft")
editor = group(draft, "frozen-code-editor")
rect(editor, 122, 168, 289, 144, "#eef5fc", "#344e6c", 3, rx=9)
editor_clip = el(defs, "clipPath", id="clip-code-editor")
rect(editor_clip, 122, 168, 289, 144, "#ffffff", rx=8)
editor_fill = group(editor, clip_path="url(#clip-code-editor)")
rect(editor_fill, 122, 168, 289, 25, "#364e68")
rect(editor_fill, 122, 193, 65, 119, "#425f7d")
for xx, color in [(137, "#fc6c64"), (153, "#ffd263"), (169, "#a5e87b")]:
    circle(editor, xx, 181, 5, color)
for yy, length in [(205, 34), (222, 25), (237, 22), (253, 27), (269, 25), (285, 20)]:
    line(editor, 136, yy, 136+length, yy, "#86a5c1" if yy != 205 else "#60b6cf", 5.5)
for yy in [204, 217, 231, 245, 259, 273, 288, 300]:
    circle(editor, 200, yy, 2.5, "#5c7eab")
for xx, yy, length, color in [
    (213, 204, 9, BLUE), (217, 217, 34, BLUE), (261, 217, 29, "#ee9a50"),
    (231, 231, 15, BLUE), (250, 231, 9, "#36a58e"), (271, 231, 7, "#e09b5f"),
    (239, 245, 42, BLUE), (290, 245, 9, "#40b485"), (310, 245, 44, "#bdc9d7"),
    (218, 259, 37, BLUE), (267, 259, 41, "#ee9a50"), (318, 259, 26, "#b8c5d6"),
    (232, 273, 26, "#27a67e"), (268, 273, 8, "#bf9a76"),
]:
    line(editor, xx, yy, xx+length, yy, color, 5.1)
line(editor, 392, 202, 392, 250, "#d0dce8", 3.4)
path(editor, "M 222 229 Q 217 229 222 235 M 223 281 Q 228 281 223 288 M 219 291 Q 224 291 219 298", BLUE, 3.5)
lock(draft, 403, 286, 33, "#2584ef")

proposal = clipped_card(svg, "stage-proposal", 567, 60, 400, 268, "#e89500", "#ffecb7", "#fff9ee")
circle(proposal, 614, 90, 23, "#73500b", id="badge-stage-2")
text(proposal, 614, 101, "2", 31, 700, "middle", "#ffffff")
text(proposal, 658, 101, "Propose a check", 26.5, 700, id="label-stage-2")
text(proposal, 767, 148, "Read-only | 120 s | ≤1 file read", 21.5, anchor="middle", fill="#34495b", id="budget-proposal")
document(proposal, 692, 167, 136, 148, fold=26)
code_glyph(proposal, 712, 199, PURPLE, size=32, sw=4.6)
for yy, length in [(231, 68), (258, 62), (285, 54)]:
    rect(proposal, 711, yy-5, 12, 12, "#fcfdff", SLATE, 2.8, rx=1)
    line(proposal, 740, yy-5, 740+length, yy-5, MUTED, 5)
    line(proposal, 740, yy+10, 740+length-9, yy+10, MUTED, 5)
circle(proposal, 831, 289, 33, "#ffd773", "#ffffff", 5)
path(proposal, "M 812 289 Q 831 266 850 289 Q 831 312 812 289 Z", "#715118", 4)
circle(proposal, 831, 289, 9, "none", "#715118", 3.7)

execution = clipped_card(svg, "stage-execution", 1080, 60, 416, 268, "#27974a", "#d0ecd8", "#f0f8f8")
circle(execution, 1127, 90, 23, "#276c49", id="badge-stage-3")
text(execution, 1127, 101, "3", 31, 700, "middle", "#ffffff")
text(execution, 1171, 101, "Run the check on D", 26.5, 700, id="label-stage-3")
text(execution, 1288, 148, "30 s timeout | at most once", 22.5, anchor="middle", fill="#34495b", id="budget-execution")
terminal = group(execution, "single-execution-terminal")
rect(terminal, 1158, 170, 260, 143, "#192633", "#657a96", 4.4, rx=9)
terminal_clip = el(defs, "clipPath", id="clip-terminal")
rect(terminal_clip, 1158, 170, 260, 143, "#ffffff", rx=8)
bar = group(terminal, clip_path="url(#clip-terminal)")
rect(bar, 1158, 170, 260, 22, "#3b5068")
for xx, color in [(1172, "#ff7364"), (1187, "#ffce66"), (1203, "#75d598")]:
    circle(terminal, xx, 181, 5, color)
path(terminal, "M 1180 209 L 1191 219 L 1180 229", "#ffffff", 4.2)
line(terminal, 1199, 230, 1208, 230, "#ffffff", 4)
for xx, yy, length, color in [
    (1227, 224, 80, "#7b90a5"), (1183, 248, 26, "#7b90a5"), (1220, 248, 137, "#5ca79e"),
    (1183, 265, 19, "#7b90a5"), (1219, 265, 91, "#7b90a5"),
    (1183, 281, 15, "#7b90a5"), (1219, 281, 43, "#7b90a5"), (1276, 281, 72, "#7abfa4"),
]:
    line(terminal, xx, yy, xx+length, yy, color, 5.6)
circle(execution, 1422, 286, 34, "#3da25e", "#ffffff", 5.5)
path(execution, "M 1416 273 L 1436 286 L 1416 299 Z", "#ffffff", 2, "#ffffff")

# Shared artifacts and the independent precomputed-result receipt.
shared = group(svg, "shared-artifacts")
shared_clip = el(defs, "clipPath", id="clip-shared")
rect(shared_clip, 498, 396, 540, 225, "#ffffff", rx=16)
shared_fill = group(shared, clip_path="url(#clip-shared)")
rect(shared_fill, 498, 396, 540, 225, "#fcfdff")
rect(shared_fill, 498, 396, 540, 60, "#dfdff7")
rect(shared, 498, 396, 540, 225, "none", "#605ca8", 2, rx=16, id="border-shared-inputs")
stack = group(shared, "shared-document-stack")
document(stack, 575, 399, 33, 43, stroke="#2e5786", sw=2.7, fold=12)
document(stack, 565, 407, 33, 45, stroke="#2e5786", sw=2.7, fold=12)
for yy, length in [(428, 15), (436, 17), (444, 12)]:
    line(stack, 572, yy, 572+length, yy, "#4b82d0", 2.8)
text(shared, 802, 435, "Shared inputs to both arms", 25.5, 700, "middle", id="label-shared-inputs")
draft_material = group(shared, "input-frozen-draft", transform="translate(547 466) scale(0.88) translate(-543 -482)")
document(draft_material, 543, 482, 109, 111, fold=25)
code_glyph(draft_material, 559, 514, "#2482ef", size=30, sw=4.5)
for yy, length, color in [(543, 28, "#73b4f6"), (558, 54, "#68b9ca"), (574, 32, "#74b1c5")]:
    line(draft_material, 560, yy, 560+length, yy, color, 5)
line(draft_material, 604, 543, 634, 543, "#efad6e", 5)
lock(draft_material, 643, 575, 25, "#2789f4")
issue_material = group(shared, "input-public-issue", transform="translate(712 466) scale(0.88) translate(-704 -483)")
document(issue_material, 704, 483, 126, 110, fold=23)
circle(issue_material, 736, 514, 19, "#df4238")
text(issue_material, 736, 524, "!", 28, 700, "middle", "#ffffff")
for xx, yy, length in [(766, 503, 29), (766, 516, 45), (766, 529, 45),
                       (722, 548, 90), (722, 561, 60), (722, 574, 43)]:
    line(issue_material, xx, yy, xx+length, yy, MUTED, 5)
check_material = group(shared, "input-check-and-expectation", transform="translate(886 466) scale(0.88) translate(-882 -483)")
document(check_material, 882, 483, 114, 110, fold=24)
code_glyph(check_material, 898, 514, PURPLE, size=28, sw=4.5)
for yy, length in [(545, 51), (570, 34)]:
    rect(check_material, 899, yy-4, 12, 12, "#fcfdff", SLATE, 2.7, rx=1)
    line(check_material, 926, yy-4, 926+length, yy-4, MUTED, 5)
    line(check_material, 926, yy+9, 926+length-8, yy+9, MUTED, 5)
text(shared, 595, 596, "Frozen draft D", 20.5, anchor="middle", fill="#40536a", id="label-input-D")
text(shared, 767, 596, "Public issue", 20.5, anchor="middle", fill="#40536a", id="label-input-issue")
text(shared, 936, 583, "Check specification", 19.5, anchor="middle", fill="#40536a", id="label-input-check")
text(shared, 936, 605, "+ expected outcome", 19.5, anchor="middle", fill="#40536a", id="label-input-expectation")

receipt = group(svg, "F-only-precomputed-result")
rect(receipt, 1160, 446, 308, 121, "#fff4e9", ORANGE, 2, rx=16)
use(receipt, "result-document", 1176, 464, 68, 90)
text(receipt, 1255, 501, "Precomputed result", 21, 700, id="label-precomputed-result")
text(receipt, 1255, 532, "or unavailable notice", 20.5, id="label-result-unavailable")

# Exact shared geometry: both borders have the same y, width, height, rx and stroke.
C = clipped_card(svg, "arm-C", 165, 668, 564, 232, "#0878ff", "#cde4ff", "#eff6ff", header_h=62, band_h=38)
F = clipped_card(svg, "arm-F", 807, 668, 564, 232, "#00a6af", "#c6edf0", "#eff7f8", header_h=62, band_h=38)


def continuation_header(parent, x, letter, title, accent):
    circle(parent, x+50, 700, 23, accent, id=f"badge-arm-{letter}")
    text(parent, x+50, 711, letter, 30, 700, "middle", "#ffffff")
    text(parent, x+94, 710, title, 26.5, 700, id=f"label-arm-{letter}")
    text(parent, x+282, 758, "150 s | 8 tool calls", 23, anchor="middle", fill="#34495b", id=f"budget-arm-{letter}")


continuation_header(C, 165, "C", "Ordinary continuation", "#0d7cfa")
continuation_header(F, 807, "F", "Advance-result continuation", "#00a3ac")
use(C, "agent-laptop", 195, 780, 128, 105, BLUE)
use(F, "agent-laptop", 828, 780, 128, 105, TEAL)
line(C, 358, 778, 358, 886, "#d9e1e9", 2.6)
line(F, 962, 778, 962, 886, "#d9e1e9", 2.6)


def tool_tile(parent, x, y, w, h, name, label):
    rect(parent, x, y, w, h, "#eff4f8", "#dce5ed", 2.3, rx=10)
    use(parent, name, x+(w-64)/2, y+7, 64, 67)
    text(parent, x+w/2, y+99, label, 20.5, anchor="middle", fill="#40536a")


for xx, name, label in [(385, "tool-inspect", "Inspect"), (490, "tool-edit", "Edit"), (595, "tool-run", "Run")]:
    tool_tile(C, xx, 779, 90, 110, name, label)
for xx, name, label in [(985, "tool-inspect", "Inspect"), (1073, "tool-edit", "Edit"), (1161, "tool-run", "Run")]:
    tool_tile(F, xx, 779, 77, 110, name, label)
line(F, 1247, 774, 1247, 886, "#a7b5c4", 2.7)
rect(F, 1260, 779, 90, 110, "#fff6ec", rx=9)
use(F, "result-document", 1277, 784, 56, 74)
text(F, 1305, 878, "Result", 20.5, anchor="middle", fill="#b95621", id="label-F-result-icon")

footer = group(svg, "matching-and-capabilities-note")
rect(footer, 399, 924, 738, 78, "#eff2f5", "#cbd5df", 2, rx=18)
text(footer, 768, 958, "Fresh contexts | matched seed | no draft conversation history", 21.5, anchor="middle", id="label-context-matching")
text(footer, 768, 989, "Both arms may inspect, edit, and run checks.", 22, anchor="middle")


EXPECTED_BUDGET = {
    "draft_seconds": 240, "draft_calls": 16,
    "constructor_seconds": 120, "constructor_reads": 1,
    "execution_seconds": 30, "continuation_seconds": 150,
    "continuation_calls": 8,
}


def build_svg(path, budget):
    """Write the approved SVG after checking all displayed budget values."""
    assert budget == EXPECTED_BUDGET, "Figure 1 is authored for the frozen R03/R04 budget."
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(svg, space="  ")
    # Binary serialization keeps the approved artwork's line endings identical
    # on Windows and Unix, including after an LF-normalizing Git checkout.
    path.write_bytes(ET.tostring(svg, encoding="utf-8", xml_declaration=True) + b"\n")
    return [node.text or "" for node in svg.iter(f"{{{NS}}}text")]


if __name__ == "__main__":
    import argparse
    from public_inputs import PAPER
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PAPER / "figures/study-design-v04.svg")
    args = parser.parse_args()
    build_svg(args.output, EXPECTED_BUDGET)
    print(args.output.name)
