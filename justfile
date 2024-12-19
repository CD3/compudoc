test *opts:
  rye run pytest -vv -s {{opts}}
format:
  rye run black .

render-readme:
  rye run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks
