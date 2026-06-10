FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python -m pip install --upgrade pip setuptools

# Pin numpy<2 — scikit-surprise 1.1.3 uses np.int_t which was removed in NumPy 2.0
# Pin Cython<3 — scikit-surprise's .pyx files are not compatible with Cython 3 syntax
RUN pip install --no-cache-dir "numpy<2.0" "Cython<3.0"

RUN pip install --no-cache-dir --upgrade --no-build-isolation -r /code/requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
