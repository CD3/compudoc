cram-tests:
  cd tests/cram && uv run cram *.t

pytest-tests *opts:
  uv run pytest -vv {{opts}}

test: pytest-tests cram-tests

format:
  uv run black .

render-readme:
  uv run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks

lint:
  uv run mypy .
