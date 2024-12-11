import { NextResponse } from 'next/server';

const fetchTransactionsFromUPBank = async (startDate: string, endDate: string, account: string) => {
  const ACCESS_TOKEN = process.env.UP_API_TOKEN;
  const ACCOUNT_IDS = {
    IC_INDIVIDUAL: process.env.IC_INDIVIDUAL || '',
    TWO_UP: process.env.TWO_UP || '',
    BILLS: process.env.BILLS || '',
    GIFTS: process.env.GIFTS || '',
    KIDS: process.env.KIDS || '',
    EXTRAS: process.env.EXTRAS || '',
    HOLIDAYS: process.env.HOLIDAYS || '',
    SUPER: process.env.SUPER || '',
    INVESTMENTS: process.env.INVESTMENTS || '',
    RAINY_DAY: process.env.RAINY_DAY || '',
    EMERGENCY: process.env.EMERGENCY || '',
    HOME_DEPOSIT: process.env.HOME_DEPOSIT || '',
    TRANSPORT: process.env.TRANSPORT || '',
    HEALTH: process.env.HEALTH || '',
    GROCERIES: process.env.GROCERIES || '',
    PERSONAL_SAVER: process.env.PERSONAL_SAVER || '',
    RENT: process.env.RENT || '',
  };

  let accountIdsToFetch = [];

  if (account === 'ALL') {
    // If 'ALL' is selected, use all accounts
    accountIdsToFetch = Object.values(ACCOUNT_IDS);
  } else {
    // If a specific account is selected, use that account
    accountIdsToFetch = [ACCOUNT_IDS[account] || ''];
  }

  if (accountIdsToFetch.includes('')) {
    return { error: 'Invalid account selected' };
  }

  const headers = {
    Authorization: `Bearer ${ACCESS_TOKEN}`,
    'Content-Type': 'application/json',
  };

  const params = new URLSearchParams({
    ...(startDate && { 'filter[since]': `${startDate}T00:00:00Z` }),
    ...(endDate && { 'filter[until]': `${endDate}T23:59:59Z` }),
    'page[size]': '100',
  });

  // Function to fetch transactions for a specific account
  const fetchTransactionsForAccount = async (accountId: string) => {
    const url = `https://api.up.com.au/api/v1/accounts/${accountId}/transactions?${params.toString()}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers,
      });

      if (response.ok) {
        const data = await response.json();

        if (data && Array.isArray(data.data)) {
          return data.data.map((transaction: any) => {
            if (transaction?.id && transaction.attributes) {
              return {
                id: transaction.id,
                attributes: {
                  description: transaction.attributes.description,
                  amount: {
                    currencyCode: transaction.attributes.amount.currencyCode,
                    value: transaction.attributes.amount.value,
                    valueInBaseUnits: transaction.attributes.amount.valueInBaseUnits,
                  },
                  settledAt: transaction.attributes.settledAt,
                  category: transaction.attributes.category,
                  account: transaction.attributes.account,
                },
                relationships: {
                  category: {
                    data: {
                      id: transaction.relationships.category?.data?.id || 'Unknown',
                    },
                  },
                },
              };
            }
            return null;
          }).filter(Boolean);
        } else {
          throw new Error('Invalid data structure');
        }
      } else {
        console.error('Error fetching data:', await response.json());
        throw new Error('Failed to retrieve data');
      }
    } catch (error) {
      console.error('Error in GET request:', error);
      throw new Error('Failed to process the request');
    }
  };

  // Fetch transactions for all accounts (if 'ALL' is selected)
  try {
    const allTransactions = await Promise.all(accountIdsToFetch.map(accountId => fetchTransactionsForAccount(accountId)));

    // Flatten the array of transaction data and return the result
    const allData = allTransactions.flat();

    return { data: allData };
  } catch (error) {
    return { error: error.message };
  }
}


// POST method to handle form submission
export async function POST(request: Request) {
  try {
    // Parse the body of the request to extract form data
    const body = await request.json();
    const { startDate, endDate, account } = body;

    if (!startDate || !endDate || !account) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Fetch transactions using the provided filters
    const transactions = await fetchTransactionsFromUPBank(startDate, endDate, account);

    // Return the fetched transactions
    return NextResponse.json(transactions);
  } catch (error) {
    console.error('Error in POST request:', error);
    return NextResponse.json({ error: 'Failed to process the request' }, { status: 500 });
  }
}
