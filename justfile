test *opts:
  uv run pytest -vv {{opts}}
  cd tests/cram && uv run cram *.t

format:
  uv run black .

render-readme:
  uv run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks

lint:
  uv run mypy .
