################################################################################
# variables
################################################################################
# region
GCP_REG=europe-west1
# project
GCP_PROJ=to-infinity-and-beyond
# project id
GCP_PROJ_ID=to-infinity-and-beyond-425409
# image
IM_NAME=my-jarvis-backend
# artifact registry
GCP_AR=to-infinity-and-beyond-repo
# memory
GAR_MEM=2Gi
#
################################################################################
# uv run
################################################################################
#
# run-my-jarvis-backend in terminal (standalone)
run-agent-console:
	uv run python src/agent.py console
#
# run-my-jarvis-backend in listener mode (dev)
run-agent-dev:
	uv run python src/agent.py dev
#
# download files
get-files:
	uv run python src/agent.py download-files
#
# switch to main branch
git-switch-branch:
	@echo "git switch <branch_name>"
#
# switch to main branch
git-switch-branch-main:
	git switch main
#
# switch to wip branch
git-switch-branch-wip:
	git switch wip
#
git-list-branches:
	git branch # -a
#
git-branch-delete:
	@echo "git branch -d <branch_name>"
#
################################################################################
# Docker
################################################################################
#
# docker-build-local:
# 	docker build \
#  	--file Dockerfile \
# 	--tag my-jarvis-backend:latest \
# 	.
#
#### GCP One Step
#
docker_gcp_build_image_amd64:
	docker build \
	--file Dockerfile \
	--platform linux/amd64 \
	--tag=${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	.
#
docker_gcp_push_image_amd64:
	docker push \
	${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod
#
docker_gcp_run_image:
	gcloud run deploy \
	--image ${GCP_REG}-docker.pkg.dev/${GCP_PROJ_ID}/${GCP_AR}/${IM_NAME}:prod \
	--memory ${GAR_MEM} \
	--region ${GCP_REG} \
	--platform managed \
	--port 8081 \
	--allow-unauthenticated \
	--min-instances 1 \
	--set-env-vars LIVEKIT_API_KEY="APIVqa2rYc4i7xF" \
	--set-env-vars LIVEKIT_API_SECRET="MyVA5SZGYq2zpm7hQeXQfOXEOYcS1hPaGgCeljRQ1XtA" \
	--set-env-vars LIVEKIT_URL="wss://nestor-fxss0huu.livekit.cloud"
