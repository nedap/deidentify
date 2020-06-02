#!/bin/bash

set -e

export CUDA_VISIBLE_DEVICES=0
python -m scripts.benchmark benchmark_gpu

export CUDA_VISIBLE_DEVICES=""
export MKL_NUM_THREADS=32
python -m scripts.benchmark benchmark_cpu_32_threads

export CUDA_VISIBLE_DEVICES=""
export MKL_NUM_THREADS=16
python -m scripts.benchmark benchmark_cpu_16_threads

export CUDA_VISIBLE_DEVICES=""
export MKL_NUM_THREADS=8
python -m scripts.benchmark benchmark_cpu_8_threads
