# Art direction — AS-BUILT

The profile is a set of engineering drawing sheets for the platform Kevin builds. It is not a website shrunk into an image. Each piece is a poster-like plate drawn in the language of an as-built drawing: frame, zone markers, dimension lines, callout balloons, detail symbols, a revision table, a title block and rubber stamps. The metaphor is the content; nothing is decoration for its own sake.

## Palette (kevinm.tech, pushed toward cyanotype)
| Token | Hex | Use |
|---|---|---|
| `NAVY` | `#0c1626` | Every plate's ground (blueprint paper) |
| `LINE` | `#d7e6f5` | Primary linework and text on navy (14:1) |
| `DIM` | `#8ea6c0` | Secondary text, dimension and leader lines (7.2:1 on navy) |
| `GOLD` | `#e6c98a` | Single accent: the GitOps path, the latest revision, stamp ink, the one word of emphasis |
| `RULE` | `#6f8aa8` | Graphics drawn outside plates on GitHub's own background (3.6:1 on white, 5.3:1 on dark). No text is ever set outside a plate, because no single mid-tone reaches 4.5:1 on both themes |

Texture: a 10 px minor grid and a 50 px major grid at 4–9 % opacity, plus fractal-noise grain at 7 %. No gradients on text, no glow, no glass and no soft drop shadows. Depth comes only from the drawing itself (axonometric layers).

## Type (embedded, OFL)
- **IBM Plex Sans Condensed Bold 700** is the display face: the name, sheet titles and project names. Tracking runs from -1 to 0.
- **IBM Plex Sans Condensed Medium 500** is used for body text and BOM parts.
- **IBM Plex Sans Condensed Italic 400** is used only for the tagline.
- **IBM Plex Mono Medium 500** is used only for measurements and drawing data: dimensions, sheet numbers, dates and title-block fields. It is never a "tech costume" for prose.
- Fonts are embedded as base64 woff2 and subset per SVG, so GitHub's `<img>` sandbox renders them.

## Motif rules
- Plates are navy shapes with a 1 px frame. The sheet frame carries zone markers only on the hero.
- There is no same-size card grid, no chip wall, no big-number-plus-label stat row and no eyebrow above headings.
- Numbers belong to the drawing. The GitHub record lives in the title block; balloons 1–3 on the hero cross-reference BOM items 1–3.
- Icons are authored line drawings at a 1.3 px stroke. There are no emoji and no Unicode arrows; arrows are drawn as SVG markers.
- Copy is EN and first person. There is one paragraph only (the general note). Only facts from `profile.config.json` and `assets/profile.json` are used.

## Sections → sheets
| Sheet | Piece | Metaphor |
|---|---|---|
| 01 | `hero.svg` | General arrangement: name, role as a dimension, tagline, exploded axonometric (Cloud / Cluster / Observe) pierced by the GitOps sync path, and a title block with the record |
| 02 | `h-bom.svg` + `bom.svg` | Bill of materials: the general note (the single paragraph) and a BOM table with one row per stack assembly |
| 03 | `h-details.svg` + `detail-N.svg` | Detail drawings: each project is a detail plate with a detail symbol (letter over sheet number) and an authored line drawing, stepping down diagonally |
| 04 | `h-revisions.svg` + `rev-N.svg` + `all-revisions.svg` | Revision history: each blog post is a revision row (delta triangle, date, description); the latest revision is in gold |
| 05 | `h-stamps.svg` + `stamp-N.svg` | Stamps: each contact is a rubber stamp in gold ink, set at a slight hand angle |

Section headers are navy title tabs followed by a scale bar drawn in `RULE`.

## Motion
GitHub serves the SVGs as `<img>` through camo, so hover does not work. All motion is automatic, slow and staggered across pieces. Content is complete at t=0, and every animation only adds to a drawing that is already visible.

| Piece | Entrance (once) | Loop (≥6 s, staggered) |
|---|---|---|
| Hero | Gold plotter pass over the axonometric (~2.4 s); the RECORD digits roll one odometer turn and land on the real value | CAD cursor wanders the sheet (22 s); GitOps pulse climbs Git → Argo CD and lights the reconciled pod (6 s) |
| Sheet tabs | Tab outline traced by the pen | A read-head scans the scale bar (9 s alternate, offset 2.3 s per sheet) |
| BOM | Row rules traced top to bottom | An inspection bar steps through the BOM items (2 s per item) |
| Detail plates | Detail symbol circle traced | The pen redraws the icon in gold, A → B → C → D (12 s cycle, 3 s apart) |
| Revisions | Older rows: bottom rule traced | Latest row: active gold marker, a playhead along the rule (8 s), and the triangle breathes (6 s) |
| All notes | none | The arrow nudges (6 s) |
| Stamps | Stamped in (scale 1.1 → 1, staggered) | A light re-press every 16 s, offset per stamp |

With `prefers-reduced-motion: reduce`, every animation stops and the overlays are hidden. The generator is deterministic, so fonts are subset without timestamps and the daily run commits only real changes.

## Light and dark
Every piece paints its own navy ground or plate. Anything outside a plate uses `RULE`, which reads on `#ffffff` and on `#0d1117`. Both themes are checked at 830 px.
