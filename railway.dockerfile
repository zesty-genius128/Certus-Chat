FROM ghcr.io/open-webui/open-webui:main

# Copy custom functions
COPY functions /app/backend/functions

# Railway configuration
ENV PORT=8080
EXPOSE 8080
ENV WEBUI_NAME="FDA Drug Information Chat"
ENV ENABLE_SIGNUP=false
ENV DEFAULT_USER_ROLE=user
