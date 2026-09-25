#!/bin/bash

set -e

COMPOSE_FILE="compose.prod.yaml"

echo "==> Atualizando imagem..."
docker compose -f "$COMPOSE_FILE" pull

echo "==> Subindo containers..."
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

echo "==> Containers atualizados com sucesso."
