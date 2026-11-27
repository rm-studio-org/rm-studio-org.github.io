# Georu site sources

`georu/*.html` are generated. Edit the fragments in `src/`, then rebuild:

```
python3 georu/_src/gen_api.py <georu>/manual-task/api/openapi-0.7.0.json   # only when the API changes
python3 georu/_src/build.py georu
```

Fragment shorthand: `[[한국어||English]]`, `<tbl>` blocks (header line, cells split by ` | `), and `` `code` ``.
Content source: Georu architecture definition v1.4 (`manual-task/content/06-architecture.md`, `content_eng/`).
