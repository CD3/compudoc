test *opts:
  uv run pytest -vv -s {{opts}}
format:
  uv run black .

render-readme:
  uv run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks

lint:
  uv run mypy .
