.venv:
	virtualenv venv

install: .venv
	. venv/bin/activate; pip install -r schedule/requirements.txt

test:
	. venv/bin/activate; python manage.py test tests

clean:
	rm -r venv/
