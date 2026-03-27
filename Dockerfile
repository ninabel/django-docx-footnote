FROM python:3.13-slim
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ARG DEMO_NAME=example

# Core deps (all demos)
RUN pip install --upgrade pip && pip install --no-cache-dir "django>=4,<5" "mammoth==1.11.0"

# Your plugin wheel
COPY dist/django_docx_footnote-0.1.0-py3-none-any.whl .
RUN pip install --no-cache-dir ./django_docx_footnote-0.1.0-py3-none-any.whl

# Demo-specific extras (from your pyproject.toml files)
RUN if [ "$DEMO_NAME" = "tinymce_demo" ]; then \
    pip install --no-cache-dir django-tinymce; \
    elif [ "$DEMO_NAME" = "ckeditor_demo" ]; then \
    pip install --no-cache-dir pillow; \
    fi

COPY demos/${DEMO_NAME} ./
COPY demos/library ./library/
RUN python manage.py migrate --noinput || true && \
    python manage.py collectstatic --noinput && \
    DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --noinput \
    --username admin --email admin@example.com 

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]