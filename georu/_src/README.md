# Georu site sources

`georu/*.html` are generated. Edit the fragments in `src/`, then rebuild:

```
python3 georu/_src/gen_api.py <georu>/manual-task/api/openapi-0.7.0.json   # only when the API changes
python3 georu/_src/build.py georu
```

Fragment shorthand: `[[한국어||English]]`, `<tbl>` blocks (header line, cells split by ` | `), and `` `code` ``.
Content is checked against the public repository https://github.com/dvmoomoodv/georu-data-migration (0.0.1).
The endpoint list comes from an OpenAPI snapshot plus `EXTRA` in gen_api.py; keep it in sync with the controllers.
