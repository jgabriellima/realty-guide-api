# Construir a imagem da API
docker build -t joaogabriellima/realty-guide-api:latest --build-arg MODE=api .

# Construir a imagem do Worker
docker build -t joaogabriellima/realty-guide-worker:latest --build-arg MODE=worker .

# Fazer push da imagem da API
docker push joaogabriellima/realty-guide-api:latest

# Fazer push da imagem do Worker
docker push joaogabriellima/realty-guide-worker:latest
