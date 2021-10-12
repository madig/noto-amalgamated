from __future__ import annotations

import collections
import logging
from pathlib import Path

import glyphsLib
import glyphsLib.classes
import ufoLib2
import ufoLib2.objects

NOTO_SOURES = Path("../noto-source/src/")

amalgamated_fonts = collections.defaultdict(ufoLib2.Font)


def insert_glyphs_into_amalgamated_font(
    source: ufoLib2.Font, target: ufoLib2.Font, suffix: str | None
):
    for glyph in source:
        if suffix is not None:
            suffixed_name = f"{glyph.name}.{suffix}"
        else:
            suffixed_name = glyph.name
        if glyph.name in target:
            if suffixed_name not in target:
                # Add glyphs with a suffix just to drive up the glyph count.
                # No copy necessary because the source is dropped anyway.
                target.layers.defaultLayer.insertGlyph(
                    glyph, name=suffixed_name, copy=False
                )
            else:
                logging.warning(
                    "Glyph %s from %s already in amalgamated font %s",
                    glyph.name,
                    path.name,
                    amalgamated_name(source),
                )
        else:
            target.addGlyph(glyph)


def suffix_from_name(path: Path) -> str | None:
    stem = path.stem
    if "Display" in stem:
        return "display"
    elif "Mono" in stem:
        return "mono"
    elif "Serif" in stem:
        return "serif"
    elif "Sans" in stem:
        return "sans"
    return None


def amalgamated_name(ufo: ufoLib2.Font) -> str:
    if ufo.info.styleName is None:
        raise ValueError(f"Style name for {ufo} is None")
    name = ufo.info.styleName.replace(" ", "")
    if name == "Semibold":
        name = "SemiBold"
    return name


for path in sorted(NOTO_SOURES.glob("*.glyphs")):
    logging.warning("Processing %s", path.name)
    suffix = suffix_from_name(path)

    with open(path) as f:
        g: glyphsLib.classes.GSFont = glyphsLib.load(f)
    ufos: list[ufoLib2.Font] = glyphsLib.to_ufos(
        g, minimal=True, propagate_anchors=False
    )  # type: ignore

    for source in ufos:
        target = amalgamated_fonts[amalgamated_name(source)]
        insert_glyphs_into_amalgamated_font(source, target, suffix)
    print(amalgamated_fonts.keys())

for path in sorted(NOTO_SOURES.glob("**/*.ufo")):
    logging.warning("Processing %s", path.name)
    suffix = suffix_from_name(path)
    source = ufoLib2.Font.open(path)
    target = amalgamated_fonts[amalgamated_name(source)]
    insert_glyphs_into_amalgamated_font(source, target, suffix)

for style, ufo in amalgamated_fonts.items():
    logging.warning("Saving %s (%s glyphs)", ufo, len(ufo.keys()))
    ufo.save(f"NotoAmalgamated-{style.replace(' ', '')}.ufo", overwrite=True)
