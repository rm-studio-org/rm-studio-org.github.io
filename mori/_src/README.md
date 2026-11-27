# MORI SOC site sources

`mori/*.html` are generated. Edit the fragments in `src/`, then rebuild:

```
python3 mori/_src/routes.py <mori-soc>/src/mori_soc/api   # only when routes change → routes.json
python3 mori/_src/gen_api.py mori/_src/routes.json         # → src/_endpoints.html (descriptions in desc.py)
python3 mori/_src/build.py mori
```

Fragment shorthand: `[[한국어||English]]`, `<tbl [wr]>` blocks (header line, cells split by ` | `), and `` `code` ``.
Content is checked against https://github.com/saranf/mori-soc (0.6.0). Prefer code over docs where they disagree.
