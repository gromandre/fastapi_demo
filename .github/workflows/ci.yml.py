name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  lint:
    name: Ruff
    runs-on: ubuntu-latest

    steps:
      - name: Получить код
        uses: actions/checkout@v4

      - name: Установить Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: pip
          cache-dependency-path: |
            requirements-api.txt
            requirements-dev.txt

      - name: Установить зависимости
        run: pip install -r requirements-dev.txt

      - name: Проверить код
        run: ruff check .

      - name: Проверить форматирование
        run: ruff format --check .