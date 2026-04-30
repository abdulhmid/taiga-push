---
name: Docker & Deployment Specialist
description: |
  Membuat Dockerfile production-ready, Docker Compose untuk multi-service (FastAPI + Vue.js + DB), multi-stage builds, optimization image, dan panduan deployment ke production (VPS, Cloud Run, Kubernetes, dll.).
  Gunakan skill ini ketika user meminta: "buat Dockerfile", "dockerize FastAPI", "dockerize Vue dashboard", "setup docker-compose", "deployment production", "multi-stage build", "containerize fullstack", "deploy ke server", atau "optimize Docker image".
version: 1.0
last_updated: 2026-04-27
tags: [docker, deployment, docker-compose, fastapi, vue, production, multi-stage, nginx]
---

# Skill: Docker & Deployment Specialist

## Goal
Menghasilkan konfigurasi Docker dan deployment yang **production-ready**, aman, ringan (small image size), repeatable, scalable, dengan best practices 2026: multi-stage builds, non-root user, health checks, secrets management, dan integrasi sempurna antara FastAPI backend + Vue.js frontend.

## When to Use This Skill
- User meminta containerization atau deployment untuk project FastAPI, Vue.js, atau full-stack.
- Setup development & production environment dengan Docker Compose.
- Optimasi image (kurangi ukuran, multi-arch support).
- Deployment ke VPS, Docker Swarm, Kubernetes, Cloud Run, Railway, Render, dll.
- Jangan gunakan jika hanya butuh script sederhana tanpa container.

## Latest Stable & Best Practices (Update April 2026)
- **Docker Engine**: 29.x
- **Docker Compose**: v2.40+ / v5.x (file version 3.8+)
- **Multi-stage builds** → wajib untuk mengurangi image size drastis.
- **Base images**: `python:3.13-slim` atau `python:3.12-slim` untuk backend; `node:lts-alpine` + `nginx:stable-alpine` untuk frontend.
- **Production server**: Gunicorn + Uvicorn workers (bukan `uvicorn` langsung).
- **Frontend**: Serve static files dengan Nginx (bukan Node di production).
- **Security**: Non-root user, `.dockerignore`, secrets via environment/secret manager, healthcheck.
- **Optimization**: Layer caching yang baik, `.dockerignore`, multi-platform build (`docker buildx`).
- **Full-stack**: Gunakan Docker Compose dengan service terpisah (backend, frontend, db, redis, dll.).

## Recommended Structure untuk Full-Stack Project

```bash
my-fullstack-app/
├── backend/                  # FastAPI project
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/                 # Vue.js project
│   ├── Dockerfile
│   ├── vite.config.ts
│   └── dist/                 # hasil build
├── docker-compose.yml        # development & production
├── docker-compose.prod.yml   # production override
├── .dockerignore
├── .env.example
└── nginx/                    # custom nginx config (opsional)