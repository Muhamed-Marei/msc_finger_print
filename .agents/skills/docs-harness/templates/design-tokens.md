# Design Tokens — {{PROJECT}} · الرموز التصميمية

Source of truth. These values MUST match the token file in code — that match is checkable,
so check it. Arbitrary values in components are forbidden by `01-architecture/rules.md`.

Token file in code: <!-- FILL: path -->

## Colour
| Token | Value | Use | الاستخدام |
|---|---|---|---|
| `color.brand.primary` | `#______` | <!-- --> | <!-- --> |
| `color.surface` | `#______` | | |
| `color.text.primary` | `#______` | | |
| `color.danger` | `#______` | | |

Contrast: every text/background pair MUST meet WCAG 2.1 AA (4.5:1 body, 3:1 large).

## Spacing
`4 · 8 · 12 · 16 · 24 · 32 · 48` — values off this scale MUST NOT be authored.

## Radius
| Token | Value | Applies to |
|---|---|---|

## Type scale
| Token | Size / line-height | Latin weight | Arabic weight |
|---|---|---|---|

## Direction
- Logical properties only: `margin-inline-start`, never `margin-left`.
- Icons that carry direction (arrows, chevrons) MUST mirror in RTL. Icons that do not (clock, logo) MUST NOT.
- Numerals: <!-- FILL: Western / Eastern Arabic — one choice, applied everywhere. -->
