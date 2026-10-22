"""Candidate test inputs for cmark 0.31.2. pbkit records the expected results from the gold binary.

Sources:
  harvested  inputs of the upstream spec, smart-punctuation, regression, entity and
             pathological tests (only the inputs; expectations come from the gold binary)
  probe      command-line behaviour, renderer x option matrix, edge inputs
  coverage   added after reading authoring/coverage/uncovered.txt
  fuzz       seeded random documents built from a block/inline grammar
"""

import random
import re

PROG = "cmark"
CASES = []


def C(id, group, args, stdin=None, files=None, doc=None, source="probe"):
    CASES.append({"id": id, "group": group, "args": list(args), "stdin": stdin, "files": files, "doc": doc, "source": source})


def spec_examples(path):
    """Yield (section, markdown) from a CommonMark spec-format file."""
    text = path.read_text(encoding="utf-8")
    section = "intro"
    fence = "`" * 32
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^#{1,6} (.*)", line)
        if m:
            section = m.group(1)
        if line.startswith(fence + " example"):
            md = []
            i += 1
            while lines[i] != ".":
                md.append(lines[i])
                i += 1
            while not lines[i].startswith(fence):
                i += 1
            out.append((section, ("\n".join(md) + "\n").replace("→", "\t")))
        i += 1
    return out


RENDER = {"html": [], "xml": ["-t", "xml"], "man": ["-t", "man"], "commonmark": ["-t", "commonmark"], "latex": ["-t", "latex"]}


def harvested(src):
    test = src / "test"
    spec = spec_examples(test / "spec.txt")
    for n, (section, md) in enumerate(spec, 1):
        sid = re.sub(r"\W+", "_", section).strip("_").lower()
        C(f"spec_{n:03d}", "spec_html", [], stdin=md, source="harvested", doc=f"CommonMark spec example {n} ({section})")
        # Every spec input through one other renderer, rotating, so all five writers see every construct family.
        name = ["xml", "commonmark", "man", "latex"][n % 4]
        C(f"spec_{n:03d}_{name}", f"spec_{name}", RENDER[name], stdin=md, source="harvested",
          doc=f"spec example {n} ({sid}) rendered as {name}")
    for n, (_s, md) in enumerate(spec_examples(test / "smart_punct.txt"), 1):
        C(f"smart_{n:02d}", "smart", ["--smart"], stdin=md, source="harvested")
        C(f"smart_{n:02d}_off", "smart", [], stdin=md, source="harvested")
        C(f"smart_{n:02d}_latex", "smart", ["--smart", "-t", "latex"], stdin=md, source="harvested")
        C(f"smart_{n:02d}_commonmark", "smart", ["--smart", "-t", "commonmark"], stdin=md, source="harvested")
    for n, (_s, md) in enumerate(spec_examples(test / "regression.txt"), 1):
        C(f"regression_{n:02d}", "regression", [], stdin=md, source="harvested")
        C(f"regression_{n:02d}_xml", "regression", ["-t", "xml", "--sourcepos"], stdin=md, source="harvested")
    entities = re.findall(r'^\{\(unsigned char\*\)"([^"]+)"', (src / "src" / "entities.inc").read_text(), re.M)
    for k in range(0, len(entities), 120):
        chunk = entities[k:k + 120]
        C(f"entities_{k // 120:02d}", "entities", [], stdin=" ".join(f"&{e};" for e in chunk) + "\n", source="harvested")
    # Pathological inputs, at sizes that stay fast for a linear-time implementation.
    path = {
        "nested_strong_emph": "*a **a " * 3000 + "b" + " a** a*" * 3000,
        "emph_closers_no_openers": "a_ " * 5000,
        "emph_openers_no_closers": "_a " * 5000,
        "link_closers_no_openers": "a]" * 5000,
        "link_openers_no_closers": "[a" * 5000,
        "mismatched_openers_closers": "*a_ " * 5000,
        "issue_389": "*a " * 3000 + "_a*_ " * 3000,
        "openers_closers_mult3": "a**b" + "c* " * 5000,
        "link_openers_emph_closers": "[ a_" * 5000,
        "pattern_bracket_paren": "[ (](" * 5000,
        "pattern_image_brackets": "![[]()" * 5000,
        "hard_link_emph": "**x [a*b**c*](d)",
        "nested_brackets": "[" * 3000 + "a" + "]" * 3000,
        "nested_block_quotes": "> " * 3000 + "a",
        "deeply_nested_lists": "".join("  " * x + "* a\n" for x in range(200)),
        "nul_in_input": "abc\u0000de\u0000",
        "backticks": "".join("e" + "`" * x for x in range(1, 400)),
        "unclosed_links_a": "[a](<b" * 5000,
        "unclosed_links_b": "[a](b" * 5000,
        "unclosed_html_comment": "<!--" + "-" * 5000,
        "many_references": "".join(f"[x{i}]: /url{i}\n" for i in range(3000)) + "[x2999]\n",
        "reference_collisions": "".join(f"[x{i}]: /u\n\n[x{i}y]\n\n" for i in range(800)),
        "tabs_in_list": "- " + "\t" * 2000 + "x",
        "many_emph_pairs": "*a* " * 10000,
        "long_line_entities": "&amp;" * 20000,
    }
    for name, md in path.items():
        C(f"pathological_{name}", "pathological", [], stdin=md, source="harvested")


def cli():
    g = "cli"
    md = "# Title\n\nSome *text* and `code`.\n"
    C("help_long", g, ["--help"])
    C("help_short", g, ["-h"])
    C("version", g, ["--version"])
    C("version_then_help", g, ["--version", "--help"])
    C("help_then_version", g, ["--help", "--version"])
    C("unknown_long_option", g, ["--nope"], stdin=md)
    C("unknown_short_option", g, ["-x"], stdin=md)
    C("single_dash", g, ["-"], stdin=md)
    C("double_dash", g, ["--"], stdin=md)
    C("width_missing", g, ["--width"], stdin=md)
    C("width_bad", g, ["--width", "12abc"], stdin=md)
    C("width_empty", g, ["--width", ""], stdin=md)
    C("width_negative", g, ["--width", "-5", "-t", "commonmark"], stdin="word " * 30)
    C("width_huge", g, ["--width", "99999999999", "-t", "commonmark"], stdin="word " * 30)
    C("width_spaces", g, ["--width", " 20", "-t", "commonmark"], stdin="word " * 30)
    C("width_plus", g, ["--width", "+20", "-t", "commonmark"], stdin="word " * 30)
    C("to_missing", g, ["-t"], stdin=md)
    C("to_long_missing", g, ["--to"], stdin=md)
    C("to_unknown", g, ["-t", "pdf"], stdin=md)
    C("to_uppercase", g, ["-t", "HTML"], stdin=md)
    C("to_twice_last_wins", g, ["-t", "xml", "-t", "man"], stdin=md)
    C("to_long", g, ["--to", "latex"], stdin=md)
    C("equals_form_not_supported", g, ["--to=xml"], stdin=md)
    C("file_argument", g, ["in.md"], files={"in.md": md})
    C("two_files_concatenated", g, ["a.md", "b.md"], files={"a.md": "# A\n\npara one\n", "b.md": "continued\n\n- x\n"})
    C("files_join_mid_paragraph", g, ["a.md", "b.md"], files={"a.md": "line without newline", "b.md": " joined\n"})
    C("files_join_fence", g, ["a.md", "b.md"], files={"a.md": "```\ncode\n", "b.md": "more\n```\n"})
    C("same_file_twice", g, ["a.md", "a.md"], files={"a.md": "[x]\n\n[x]: /u\n"})
    C("missing_file", g, ["nope.md"])
    C("missing_second_file", g, ["a.md", "nope.md"], files={"a.md": "ok\n"})
    C("directory_argument", g, ["d"], files={"d/x": "1"})
    C("stdin_ignored_with_file", g, ["a.md"], stdin="from stdin\n", files={"a.md": "from file\n"})
    C("options_after_file", g, ["a.md", "-t", "xml"], files={"a.md": "*x*\n"})
    C("file_named_like_format", g, ["-t", "xml", "html"], files={"html": "*x*\n"})
    C("big_file_over_buffer", g, ["big.md"], files={"big.md": ("para " * 50 + "\n\n") * 100})
    C("big_stdin_over_buffer", g, [], stdin=("> quote *line* " * 40 + "\n") * 60)
    C("empty_input", g, [], stdin="")
    for name, args in RENDER.items():
        C(f"empty_input_{name}", g, args, stdin="")
        C(f"only_whitespace_{name}", g, args, stdin="   \n\n\t\n")
    C("all_flags", g, ["--sourcepos", "--hardbreaks", "--nobreaks", "--smart", "--safe", "--unsafe", "--validate-utf8"],
      stdin='Line "one"\nline two -- <b>raw</b> [l](javascript:x)\n')


SAMPLE_DOCS = {
    "kitchen_sink": """# Heading *one*

Setext heading
--------------

A paragraph with *emph*, **strong**, ***both***, `code`, a [link](http://example.com "Title"),
an ![image](img.png "Img"), <http://auto.link>, <me@example.com>, a hard\\
break and a soft
break. Entities: &copy; &#x27; &#39; &nbsp;. Backslash \\* escapes.

> A block quote
> with *two* lines
>
> > nested quote

1. first
2. second
   - nested bullet
   - another

     with a paragraph
3. third

- [ ] not a task list
* different bullet

```python
def f(x):
    return x * 2
```

    indented code block

<div class="raw">
*not emph*
</div>

Inline <span>html</span> and <!-- comment -->.

***

[ref link][ref] and [collapsed][] and [shortcut].

[ref]: /url "ref title"
[collapsed]: </with spaces>
[shortcut]: http://x.y 'single'
""",
    "lists": "- a\n- b\n\n- c\n\n1) x\n2) y\n\n10. ten\n11. eleven\n\n* loose\n\n  para\n* tight\n",
    "quotes_and_dashes": "\"Hello,\" said the spider. 'Shelob' is my name -- or --- maybe... it's 1990's.\n",
    "special_chars": "Special: \\ { } $ & # ^ _ % ~ < > \" ' | and . at line start\n\n.SH not a macro\n'quote\n",
    "long_paragraph": ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                       "incididunt ut labore et dolore magna aliqua. ") * 6 + "\n",
    "links_and_urls": "[a](<b c>) [d](e(f)g) [h](i\\)j) [k](l \"m\" ) [n](javascript:alert(1)) [o](data:image/png;base64,x) "
                      "[p](vbscript:x) [q](file:///etc) ![r](data:text/html;x) <javascript:y>\n",
    "raw_html": "<script>alert(1)</script>\n\n<p onclick=\"x\">p</p>\n\nInline <b onmouseover=x>b</b> <?php ?> <!DOCTYPE x> <![CDATA[ y ]]>\n",
    "headings": "# h1\n## h2 ##\n### h3 #\n#### h4\n##### h5\n###### h6\n####### not\n\nH\n=\n\nH2\n---\n",
    "code": "``` js {.class}\nconsole.log(`x`);\n```\n\n~~~~\n~~~\n~~~~\n\n`` a`b ``\n\n````\n```\n````\n",
    "breaks": "line one\nline two  \nline three\\\nline four\n",
    "unicode": "Ünïcödé — “quotes” ‘single’ 日本語 *強調* 😀  nbsp\n",
    "tables_not_supported": "| a | b |\n|---|---|\n| 1 | 2 |\n",
    "nested_structure": "> 1. > - a\n>    >   b\n> 2. c\n>\n>        code in list\n",
}
WIDTHS = ["0", "1", "10", "20", "40", "72", "120"]


def matrix():
    for dname, md in SAMPLE_DOCS.items():
        for rname, rargs in RENDER.items():
            g = f"render_{rname}"
            C(f"{dname}_{rname}", g, rargs, stdin=md)
            C(f"{dname}_{rname}_sourcepos", "sourcepos", rargs + ["--sourcepos"], stdin=md)
            C(f"{dname}_{rname}_hardbreaks", "breaks", rargs + ["--hardbreaks"], stdin=md)
            C(f"{dname}_{rname}_nobreaks", "breaks", rargs + ["--nobreaks"], stdin=md)
            C(f"{dname}_{rname}_smart", "smart", rargs + ["--smart"], stdin=md)
            C(f"{dname}_{rname}_unsafe", "safety", rargs + ["--unsafe"], stdin=md)
            C(f"{dname}_{rname}_safe", "safety", rargs + ["--safe"], stdin=md)
            if rname in ("commonmark", "man", "latex"):
                for w in WIDTHS:
                    C(f"{dname}_{rname}_width_{w}", "width", rargs + ["--width", w], stdin=md)
                C(f"{dname}_{rname}_width_hardbreaks", "width", rargs + ["--width", "30", "--hardbreaks"], stdin=md)
                C(f"{dname}_{rname}_width_nobreaks", "width", rargs + ["--width", "30", "--nobreaks"], stdin=md)


def edge_inputs():
    g = "input_bytes"
    inputs = {
        "crlf": b"# t\r\n\r\npara\r\nline\r\n",
        "cr_only": b"# t\r\rpara\rline\r",
        "no_trailing_newline": b"para without newline",
        "bom": b"\xef\xbb\xbf# heading after BOM\n",
        "bom_twice": b"\xef\xbb\xbf\xef\xbb\xbfx\n",
        "nul_bytes": b"a\x00b\n\n`\x00`\n",
        "invalid_utf8": b"bad \xff\xfe bytes \xc3\x28 and \xe2\x82\n",
        "overlong_utf8": b"\xc0\xaf \xe0\x80\xaf\n",
        "surrogate_utf8": b"\xed\xa0\x80\n",
        "truncated_utf8_end": b"end \xe2\x82",
        "tabs_mixed": b"-\tfoo\n\n\tbar\n  \tbaz\n",
        "form_feed": b"a\x0cb\n\n\x0c# h\n",
        "control_chars": b"\x01\x02\x1b[31mred\x1b[0m\x7f\n",
        "very_long_line": b"x" * 100000 + b"\n",
        "many_blank_lines": b"\n" * 5000 + b"x\n",
        "deep_list_indent": b"".join(b" " * (2 * i) + b"- l\n" for i in range(60)),
    }
    for name, data in inputs.items():
        C(name, g, [], stdin=data)
        C(f"{name}_validate", g, ["--validate-utf8"], stdin=data)
        C(f"{name}_xml", g, ["-t", "xml", "--validate-utf8"], stdin=data)
        C(f"{name}_commonmark", g, ["-t", "commonmark"], stdin=data)


# ---- fuzz: random documents from a small block/inline grammar ----------------------------------

INLINE_ATOMS = ["word", "two words", "*em*", "_em_", "**strong**", "__strong__", "*a **b** c*", "`code`", "``a`b``",
                "[link](/u)", "[ref]", "[ref][]", "![img](/i.png)", "<http://x.y>", "<a@b.c>", "&amp;", "&#123;",
                "&bogus;", "\\*", "\\", "<b>", "</b>", "<!-- c -->", "*", "_", "**", "[", "]", "(", ")", "!",
                "'s", '"q"', "--", "...", "a_b_c", "*a*b*", "**a*", "~", "#", "|", "é", "\U0001f600"]


def inline(rng, n=None):
    parts = [rng.choice(INLINE_ATOMS) for _ in range(n or rng.randint(1, 8))]
    joiners = [" ", " ", " ", "", "\n", "  \n", "\\\n"]
    out = parts[0]
    for p in parts[1:]:
        out += rng.choice(joiners) + p
    return out


def block(rng, depth=0):
    r = rng.random()
    if depth > 3 or r < 0.3:
        return inline(rng) + "\n"
    if r < 0.4:
        return "#" * rng.randint(1, 7) + " " + inline(rng, 3) + rng.choice(["", " #", " ##"]) + "\n"
    if r < 0.47:
        return inline(rng, 3) + "\n" + rng.choice(["===", "---", "-", "= ="]) + "\n"
    if r < 0.55:
        return rng.choice(["***", "---", "___", "* * *", "- - -"]) + "\n"
    if r < 0.63:
        f = rng.choice(["```", "~~~", "````"])
        return f + rng.choice(["", "py", " c x"]) + "\n" + inline(rng) + "\n" + rng.choice([f, f + "`", ""]) + "\n"
    if r < 0.68:
        return "    " + inline(rng, 3) + "\n"
    if r < 0.73:
        return rng.choice(["<div>\n", "<pre>\n", "<!--\n", "<x-tag a=1>\n"]) + inline(rng) + "\n" + rng.choice(["</div>", "-->", ""]) + "\n"
    if r < 0.78:
        dest = rng.choice(["/url", "<a b>", "http://x"])
        title = rng.choice(["", ' "t"', " (t)"])
        return f"[ref]: {dest}{title}\n"
    if r < 0.88:
        body = "".join(block(rng, depth + 1) for _ in range(rng.randint(1, 3)))
        return "".join("> " + line + "\n" for line in body.rstrip("\n").split("\n"))
    marker = rng.choice(["-", "*", "+", "1.", "2)", "10."])
    items = []
    for _ in range(rng.randint(1, 4)):
        body = "".join(block(rng, depth + 1) for _ in range(rng.randint(1, 2)))
        lines = body.rstrip("\n").split("\n")
        pad = " " * (len(marker) + 1)
        items.append(marker + " " + lines[0] + "\n" + "".join(pad + l + "\n" for l in lines[1:]))
    return rng.choice(["", "\n"]).join(items)


def fuzz(n=500, seed=31337):
    rng = random.Random(seed)
    flags = ["--sourcepos", "--hardbreaks", "--nobreaks", "--smart", "--unsafe", "--validate-utf8"]
    for i in range(n):
        doc = rng.choice(["", "\n"]).join(block(rng) for _ in range(rng.randint(1, 6)))
        rname = rng.choice(list(RENDER))
        args = list(RENDER[rname]) + [f for f in flags if rng.random() < 0.15]
        if rname in ("commonmark", "man", "latex") and rng.random() < 0.4:
            args += ["--width", rng.choice(WIDTHS)]
        C(f"fuzz_{i:03d}", "fuzz", args, stdin=doc, source="fuzz")


def generate(src):
    harvested(src)
    cli()
    matrix()
    edge_inputs()
    fuzz()
    return CASES
