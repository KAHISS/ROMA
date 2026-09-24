#!/bin/bash
# deploy.sh — builda a imagem de produção e envia pro GitHub Container Registry
#
# Uso:
#   ./deploy.sh            -> builda e envia só como "latest"
#   ./deploy.sh v1.2       -> builda e envia como "v1.2" e também atualiza "latest"

set -e  # para o script imediatamente se qualquer comando falhar

IMAGE="ghcr.io/kahiss/jpacessorios"
VERSION="$1"

echo "==> Buildando imagem de produção..."
if [ -n "$VERSION" ]; then
  docker build --target production -t "$IMAGE:$VERSION" -t "$IMAGE:latest" .
else
  docker build --target production -t "$IMAGE:latest" .
fi

echo "==> Enviando pro GHCR..."
if [ -n "$VERSION" ]; then
  docker push "$IMAGE:$VERSION"
fi
docker push "$IMAGE:latest"

echo ""
echo "==> Pronto! Agora, na VPS, rode:"
echo "    cd ~/app_repo && docker compose -f compose.prod.yaml pull && docker compose -f compose.prod.yaml up -d"
