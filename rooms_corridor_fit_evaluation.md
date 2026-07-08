# Rooms.md Corridor Fit Evaluation

Source files:
- `Rooms.md`
- `locked_two_room_connection_reference.txt`

Current locked rules from the room + horizontal corridor grammar:

1. Backticks are shared grid-line crossings/corners, not center dots.
2. A logical floor box is 5 columns × 3 rows when shared boundaries are counted; adjacent crossings step by 4 columns / 2 rows.
3. Room-to-room horizontal corridors overlap room mouths; they are not inserted between two closed boxes.
4. Same-level horizontal connectors should not read as a separate raised platform unless intentionally gated/special.
5. Structural origins are grid lines/support columns, not necessarily the first visible decorative glyph.
6. East/west/south wall glyphs must either leave the proper glyph space open or cover it until the next grid line.

## Best regular corridor candidate

### R24 — `Rooms.md:216-222` — `#pathway#`

```text
#pathway#
, -,- -,—-j` . |t--,- -,.
|_/___/__j ` . t__/___/,| 
|. ` . ` . ` . ` . ` .| |  
|. ` . ` . ` . ` . ` .'/|  
'- - - - -.` . `.- - -'-'
          |` . /|
```

Fit: **best base candidate for a regular vertical/offshoot pathway**, not a replacement for the locked same-level horizontal room-to-room corridor.

Why it fits:
- Uses the same grid language: `. ` / backtick crossings repeat on the floor plane.
- Uses structural `j`/`t` opposing supports, similar to the corridor/platform grammar.
- Has underside rows like `|_/___/__j` and `t__/___/,|`, compatible with the existing slash/underscore vocabulary.
- Includes a downward continuation tail:
  ```text
            |` . /|
  ```
  which makes it useful as a vertical connector/offshoot.

Caution:
- It is a standalone pathway block, not the locked side-door horizontal corridor.
- It has a visible front/south boundary row; only use that when the connector is a pathway/gate/shaft face, not for the same-level horizontal room-mouth connector.

## Special/gated variants

### R26 — `Rooms.md:224-231` — Special pathway

```text
#Special pathway#

, -,- -;;;J` . /L;;;- -,.
|_/___///J ` . L///___/,| 
|. ` . ` . ` . ` . ` .| |  
|. ` . ` . ` . ` . ` .'/|  
'- - - - -.` . `.- - -'-'
          |` . /|        
```

Fit: **good special/gated skin of R24**.

Use when the connector should read as special, dangerous, locked, or decorated. The `;;;J` / `L;;;` columns are gate posts, not ordinary room wall grammar.

### R28 — `Rooms.md:233-241` — Boss Gate

```text
#Boss Gate#

        _;,,;)),,));,;_
, -,- - ;;;J` ./ L;;;- -,
|_/__,///J ` . L///,__/,| 
|. ` . ` . ` . ` . ` .| |  
|. ` . ` . ` . ` . ` .'/|  
'- - - - -.` . `.- - -'-'
          |` . /|
```

Fit: **boss-gate variant**, not a normal corridor.

Use as a decorative gate overlay on top of the R26 special pathway logic.

## Larger vertical connector candidate

### R31 — `Rooms.md:263-279` — two-level special vertical connection

```text
  .-—-;;;J   / L;;;--,
  |_///J’    L///___/,| 
  |  `   `   `   `  | |
  |  `   `   `   `  '/|  
  '- - - .   `,+—— -'-'
         |   /,|       
         |   ‘,|
         |   /,|
  ,— -,—-'   ‘,t-,- -,.
  |__/__’    /__/___/,|
  |  `   `   `   `  | |
  |  `   `   `   `  '/|  
  '- - - .   `,,—— -'-'
         |   /,|       
         |   ‘ |
```

Fit: **best candidate for a full vertical transition connecting an upper corridor to a lower corridor**, especially if the connector is special/gated.

Why it fits:
- It includes both an upper and lower corridor mouth.
- It explicitly shows the vertical shaft between them:
  ```text
         |   /,|
         |   ‘,|
         |   /,|
  ```
- It uses gate/post vocabulary that can be adapted from R26/R28.

Caution:
- This is not the plain/default corridor. It is special/gate-flavored.
- Needs a clean non-special version derived from R24 if we want a regular vertical stair/shaft.

## Weak/secondary candidates

### R20/R21 — `Rooms.md:181-193`

These are useful for understanding bridge/platform seams, but they are less suitable as room connectors. They read more like split platform/bridge chunks than corridor mouths.

### R22/R23 — `Rooms.md:195-214`

These are useful for internal room structures, doorways, pits, or platforms. They are not the best first choice for a vertical corridor because they embed the connector inside a larger room shell.

### R29 — `Rooms.md:243-247`

This is a platform/gate-top decorative sample, not a corridor.

### R32 — `Rooms.md:282-291`

This is most useful as a closed room/east-wall rule sample, not a connector.

## Decision

Use **R24** as the base regular vertical/offshoot corridor family.

Use **R26** as the special/gated variant.

Use **R28** when the same connector needs a boss-gate crown.

Use **R31** only when we need a larger two-level vertical connector connecting an upper corridor to a lower corridor.

Do **not** replace the locked same-level horizontal room-to-room corridor with any of these. The current locked horizontal corridor remains its own family.
