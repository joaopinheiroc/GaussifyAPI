.PHONY: help install test test-cov verify-db run clean lint

help:
	@echo "GaussifyAPI - Comandos disponíveis:"
	@echo ""
	@echo "  make install     - Instalar dependências"
	@echo "  make test        - Executar testes"
	@echo "  make test-cov    - Executar testes com cobertura"
	@echo "  make verify-db   - Verificar integridade do banco de dados"
	@echo "  make run         - Executar aplicação em modo desenvolvimento"
	@echo "  make clean       - Limpar arquivos temporários"
	@echo "  make lint        - Verificar código com flake8 (se instalado)"
	@echo ""

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

verify-db:
	python verify_db.py

run:
	python run.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/ .coverage build/ dist/

lint:
	@command -v flake8 >/dev/null 2>&1 && flake8 api/ core/ tests/ --max-line-length=100 || echo "flake8 não instalado"
