SOURCE=		src
PIPCOMPILE=	pip-compile -v --generate-hashes --extra-index-url https://pypi.sunet.se/simple

reformat:
	isort --line-width 120 --atomic --project haproxy_status --recursive $(SOURCE)
	black --line-length 120 --target-version py37 --skip-string-normalization $(SOURCE)

test:
	PYTHONPATH=$(SOURCE) pytest

typecheck:
	#mypy --ignore-missing-imports $(SOURCE)

%ments.txt: %ments.in
	CUSTOM_COMPILE_COMMAND="make update_deps" $(PIPCOMPILE) $<

update_deps: $(patsubst %ments.in,%ments.txt,$(wildcard *ments.in))
