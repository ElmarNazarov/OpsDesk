up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

createsuperuser:
	docker compose exec web python manage.py createsuperuser

seed:
	docker compose exec web python manage.py seed_demo_data

test:
	docker compose exec web pytest

coverage:
	docker compose exec web coverage run -m pytest && docker compose exec web coverage report

lint:
	docker compose exec web ruff check .

format:
	docker compose exec web ruff format .

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f
