list:
    just --list

build-readme:
    uv run compudoc README.md.cd --comment-line-pattern="<!--{{{{CODE}}-->"

run-cram-tests:
  cd tests/cram && uv run cram *.t

run-pytest-tests *opts:
  uv run pytest -vv {{opts}}

test: run-pytest-tests run-cram-tests

format:
  uv run black .

render-readme:
  uv run compudoc README-template.md --output-file-template README.md --comment-line-str="//" --strip-comment-blocks

lint:
  uv run mypy .

publish:
  rm dist -rf
  uv build
  uv publish
