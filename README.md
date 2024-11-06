# Up Bank Transaction Plotting

This project allows you to fetch, process, and visualise transaction data using various types of plots. It fetches transaction data from a given account and plots the data using either a bar plot, line plot, or scatter plot.

## Requirements

- Python 3.9 or later
- Poetry (for dependency management)
- Up API account (for fetching transaction data)

## Example to get your account ids

- This is a quick way to retrieve all your accounts details
- We will use the account ids for our env variables

```bash
# Replace "your_access_token_here" with your actual access token
ACCESS_TOKEN="your_access_token_here"

# Make the GET request to retrieve account details and pretty-print the response
curl -s -X GET \
  https://api.up.com.au/api/v1/accounts \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq .
```

## Up Bank API Documentation

For details on how to interact with the Up API, please refer to the official documentation: [Up API Docs](https://developer.up.com.au/#welcome)

---

## Set up (macOS)

### Step 1: Install Homebrew

If you don't have Homebrew installed, open your Terminal and run the following command:

``` bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After the installation completes, verify it with:

``` bash
brew --version
```

---

### Step 2: Install Python 3.9 or Later

If you don't have Python installed or need to upgrade, you can install Python using Homebrew:

``` bash
brew install python@3.9
```

Verify the installation by checking the Python version:

```bash
python3 --version
```

---

### Step 3: Install Poetry

You can install Poetry via Homebrew with the following command:

``` bash
brew install poetry
```

After the installation, verify it by running:

``` bash
poetry --version
```

### Step 4: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/transaction-plotting-tool.git
cd transaction-plotting-tool
```

### Step 5: Install Dependencies

Run the following command to install the required dependencies via Poetry:

```bash
poetry install
```

This will create a virtual environment and install all dependencies listed in pyproject.toml

---

### Step 6: Create the .env File

Create a .env file in the root directory of the project. This file should contain the following environment variables:

```bash
ACCOUNT_IDS=your_account_id
UP_API_KEY=your_up_api_key
```

---
