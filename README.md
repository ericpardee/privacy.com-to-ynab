# privacy.com-to-ynab

Synchronize your [Privacy.com](https://privacy.com/) transactions to [You Need a Budget (YNAB)](https://www.ynab.com/) effortlessly.

## Table of Contents

- [Requirements](#requirements)
- [One-Click Deploy](#one-click-deploy)
- [Using Docker](#-using-docker)
  - [Building the Image](#building-the-image)
  - [Running the Container](#running-the-container)
- [Running Locally](#-running-locally)
  - [Setting up Environment Variables](#setting-up-environment-variables)
  - [Running the Script](#running-the-script)
- [Prerequisites](#prerequisites)
- [Contributing](#contributing)
- [Support & Contact](#support--contact)
- [License](#license)

## Requirements

1. [Privacy.com API Key](https://privacy-com.readme.io/docs/getting-started): Found within your [Privacy Account page](https://app.privacy.com/account#api-key).
2. YNAB Personal Access Token:
   - [Sign into YNAB](https://app.ynab.com/settings) and go to the "Account Settings" page and then to [the "Developer Settings" page](https://app.ynab.com/settings/developer).
   - Under the "Personal Access Tokens" section, click "New Token", enter your password and click "Generate" to get an access token.
3. YNAB Budget ID: Open the [YNAB account](https://app.ynab.com/), select your Budget. Your URL should look like `https://app.ynab.com/zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz/budget`. The `yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy` portion is your Budget ID.

## One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ericpardee/privacy.com-to-ynab)

This application is designed to operate as a [cron job on Render](https://render.com/docs/cronjobs), with a default schedule to run every day at 3am UTC. You can adjust this frequency as needed in the cron settings within render.com UI after deployment.

This approach was selected over an alternative that would involve leveraging a [Privacy.com Webhook](https://support.privacy.com/hc/en-us/articles/360039147274-Privacy-API) combined with a continuously active [Render web service](https://render.com/docs/web-services). This configuration offers enhanced security due to its unidirectional communication: with only outgoing requests and no incoming traffic, it effectively minimizes the attack surface, thereby eliminating potential avenues for exploitation. However, the trade-off with this setup is that synchronization happens just once daily by default.

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
pip install -r dev-requirements.txt
```

3. Execute the script:

```sh
python app.py
```

## Prerequisites

Ensure you have Python 3.11 and/or Docker installed on your machine.

## Contributing

Feedback and contributions are always welcome! Please open an issue or submit a pull request.

## Support & Contact

For any issues or inquiries, please open an issue on GitHub.

## License

This project is licensed under [MIT License](LICENSE).