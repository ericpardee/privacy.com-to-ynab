# privacy.com-to-ynab

Synchronize your Privacy.com transactions to YNAB effortlessly.

## One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ericpardee/privacy.com-to-ynab)

## 🐳 Using Docker

### Building the Image

Build the Docker image using the following command:

```sh
docker build -t privacy.com-to-ynab .
```

### Running the Container

Run the Docker container by either passing environment variables directly:

```sh
docker run -e PRIVACY_API_TOKEN='your_privacy_token' \
           -e YNAB_API_TOKEN='your_ynab_token' \
           -e YNAB_BUDGET_ID='your_ynab_budget_id' \
           -e DEBUG='true_or_false' \
           privacy.com-to-ynab
```

...or by using a `.env` file:

```sh
docker run --env-file .env privacy.com-to-ynab
```

## 🖥 Running Locally

### Setting up Environment Variables

First, create a `.env` file in the root directory and populate it:

```text
PRIVACY_API_TOKEN=your_privacy_token
YNAB_API_TOKEN=your_ynab_token
YNAB_BUDGET_ID=your_ynab_budget_id
DEBUG=true
```

> 💡 **Pro-tip**: If you use [direnv](https://direnv.net/), you can add a `.envrc` file containing `export $(cat .env | xargs)` to automatically set these variables when entering the directory.

### Running the Script

1. Setup a Python virtual environment:

```sh
python3 -m venv venv && source venv/bin/activate
```

2. Install the required packages:

```sh
pip install -r requirements.txt
```

3. Execute the script:

```sh
python app.py
```
