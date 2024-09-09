test:
  rye run pytest -vv -s
render-readme:
  rye run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks
