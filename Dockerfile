FROM python:3.10-slim as builder
WORKDIR /wypt-api
RUN python -m pip install --no-cache-dir --upgrade pytest tox build
COPY setup.py pyproject.toml /wypt-api
COPY tests/ ./tests
COPY src/ ./src
RUN tox -e py310
RUN python -m build

FROM python:3.10-slim
WORKDIR /wypt-api
COPY --from=builder /wypt-api/dist ./dist
RUN pip --no-cache-dir install dist/wypt-*.whl
CMD ["uvicorn", "wypt.api:routes", "--host", "0.0.0.0", "--port", "80"]
