SOURCE=		src

reformat:
	isort --line-width 120 --atomic --project haproxy_status --recursive $(SOURCE)
	black --line-length 120 --target-version py37 --skip-string-normalization $(SOURCE)

test:
	PYTHONPATH=$(SOURCE) pytest

typecheck:
	#mypy --ignore-missing-imports $(SOURCE)
