gcloud storage cp -r gs://qwiklabs-gcp-02-89fad0ed3ed0-bucket/adk_challenge_lab .
export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install -r adk_challenge_lab/requirements.txt
python3 -m pip install chainlit==2.11.1
gcloud discoveryengine engines list --location=global --format="table(displayName, name.basename())"
curl -s -X GET   -H "Authorization: Bearer $(gcloud auth print-access-token)"   -H "X-Goog-User-Project: $(gcloud config get-value project)"   "https://discoveryengine.googleapis.com/v1/projects/$(gcloud config get-value project)/locations/global/collections/default_collection/engines"   | grep -o '"name": "[^"]*' | awk -F'/' '{print $NF}'
cd ~/adk_challenge_lab
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-central1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=paint-search_1787097833823
EOF

adk run paint_agent
cd ~/adk_challenge_lab
adk run paint_agent
adk web --allow_origins "regex:https://.*\.cloudshell\.dev"
cd ~/adk_challenge_lab
adk deploy agent_engine   --display_name "Paint Agent"   --staging_bucket gs://<PROJECT_ID>-bucket   .
cd ~/adk_challenge_lab
adk deploy agent_engine   --display_name "Paint Agent"   --staging_bucket "gs://$(gcloud config get-value project)-bucket"   .
gcloud ai reasoning-engines list   --region=us-central1   --format="table(displayName, name, createTime, updateTime)"
adk deploy agent_engine   --display_name "Paint Agent"   --staging_bucket "gs://$(gcloud config get-value project)-bucket"   .
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_LOCATION=us-central1
gcloud config get-value project
export GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
gcloud config get-value project
export PROJECT_ID=qwiklabs-gcp-02-89fad0ed3ed0
cd ~/adk_challenge_lab
adk deploy agent_engine   --display_name "Paint Agent"   --staging_bucket "gs://${GOOGLE_CLOUD_PROJECT}-bucket"   .
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND severity>=ERROR'   --limit=15   --format="value(textPayload,jsonPayload.message)"
cat ~/adk_challenge_lab/.env
SA="serviceAccount:service-56063329095@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
PROJECT_ID="$(gcloud config get-value project)"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="$SA" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="$SA" --role="roles/discoveryengine.user"
cd ~/adk_challenge_lab
adk run paint_agent
cd ~/adk_challenge_lab
rm -rf .venv venv build dist *.egg-info
find . -type d -name "__pycache__" -exec rm -rf {} +
cd ~/adk_challenge_lab
adk deploy agent_engine   --display_name "Paint Agent"   --staging_bucket "gs://$(gcloud config get-value project)-bucket"   .
cd ~/adk_challenge_lab
# Create the updated environment file with us-west1
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-west1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=YOUR_ID
EOF

# Copy the updated configuration into the agent directory
cp .env paint_agent/.env
cd ~/adk_challenge_lab
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-west1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=paint-search_1787097833823
EOF

cd ~/adk_challenge_lab
adk deploy agent_engine --display_name "Paint Agent" paint_agent
cd ~/adk_challenge_lab
# Create the updated environment file with us-west1
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-west1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=paint-search_1787097833823
EOF

# Copy the updated configuration into the agent directory
cp .env paint_agent/.env
adk deploy agent_engine --display_name "Paint Agent" paint_agent
cd ~/adk_challenge_lab
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-west1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=paint-search_1787097833823
EOF

cp .env paint_agent/.env
adk deploy agent_engine --display_name "Paint Agent" paint_agent
# Set your project ID variable for convenience
PROJECT_ID="qwiklabs-gcp-02-89fad0ed3ed0"
SERVICE_ACCOUNT="service-56063329095@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
# Grant the Agent Platform User role
gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SERVICE_ACCOUNT"   --role="roles/aiplatform.user"
# Grant the Discovery Engine User role
gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SERVICE_ACCOUNT"   --role="roles/discoveryengine.user"
cd ~/adk_challenge_lab
# Create the updated environment file with us-central1
cat << EOF > .env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-02-89fad0ed3ed0
GOOGLE_CLOUD_LOCATION=us-central1
RESOURCES_BUCKET=qwiklabs-gcp-02-89fad0ed3ed0-bucket
MODEL=gemini-2.5-flash
SEARCH_ENGINE_ID=paint-search_1787097833823
EOF

# Copy the updated configuration into the agent directory
cp .env paint_agent/.env
adk deploy agent_engine --display_name "Paint Agent" paint_agent
cd ~/adk_challenge_lab/chainlit_ui
chainlit run app.py
zip -r adk_challenge_lab.zip ~/adk_challenge_lab
