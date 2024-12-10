# Up Bank Transaction Display

This project allows you to fetch, process, and visualise transaction data from the Up Bank API using various types of plots.
The data is fetched from your Up account and displayed through interactive charts (line, bar, or pie charts).

## Requirements

- Node.js 16.x or later
- Next.js (React framework for building the app)
- Up API account (for fetching transaction data)

## Features

- Fetch transaction data from the Up Bank API.
- Visualise transaction amounts with interactive charts (line, bar, or pie).
- Easy switching between chart types.
- Switch between light and dark mode
- Filter transactions by date, amount, description, and category.

## Set Up Your Environment

### Step 1: Install Dependencies

Clone the repository and install the required dependencies. For eg:

```bash
git clone https://github.com/yourusername/transaction-plotting-tool.git
cd transaction-plotting-tool
npm install
```

### Step 2: Create .env

Create a .env.local file in the root directory of the project to store environment variables. You should include your Up API access token and other relevant credentials:

```bash
UP_API_KEY=your_up_api_key
```

### Step 3: Run the Development Server

Once the dependencies are installed and your environment is set up, run the Next.js development server:

```bash
npm run dev
```

## Charting and Data Display

The app uses recharts to render different types of charts (line, bar, area, and donut) based on the filtered transaction data. Transaction amounts are displayed in the selected chart format, with dynamic tooltips to display the transaction values.

You can filter the data by start date, end date, description, category, and amount range. The charts dynamically update based on the applied filters.
