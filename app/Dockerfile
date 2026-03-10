FROM python:3.14

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src/ /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]