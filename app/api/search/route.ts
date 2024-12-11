import { NextResponse } from 'next/server';

const fetchTransactionsFromUPBank = async (startDate: string, endDate: string) => {
  const ACCESS_TOKEN = process.env.UP_API_TOKEN;
  const ACCOUNT_IDS = {
    IC_INDIVIDUAL: process.env.IC_INDIVIDUAL || '',
  };

  const accountId = ACCOUNT_IDS.IC_INDIVIDUAL;
  if (!accountId) {
    return { error: 'Invalid account selected' };
  }

  const headers = {
    Authorization: `Bearer ${ACCESS_TOKEN}`,
    'Content-Type': 'application/json',
  };

  // Use startDate and endDate directly as strings
  const params = new URLSearchParams({
    ...(startDate && { 'filter[since]': `${startDate}T00:00:00Z` }), // Include only if present
    ...(endDate && { 'filter[until]': `${endDate}T23:59:59Z` }), // Include only if present
    'page[size]': '100', // Fetch in batches of 100 for pagination
  });

  const url = `https://api.up.com.au/api/v1/accounts/${accountId}/transactions?${params.toString()}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (response.ok) {
      const data = await response.json();

      if (data && Array.isArray(data.data)) {
        const transformedData = data.data.map((transaction: any) => {
          // Ensure that the transaction contains the expected structure
          if (transaction && transaction.id && transaction.attributes) {
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
                    id: transaction.relationships.category?.data?.id || 'Unknown', // Add fallback in case relationships is null
                  },
                },
              },
            };
          }
          return null; // Return null if transaction is not structured correctly
        }).filter(Boolean); // Remove any null entries

        return { data: transformedData }; // Return the transformed data
      } else {
        return { error: 'Invalid data structure' };
      }
    } else {
      console.error('Error fetching data:', await response.json());
      return { error: 'Failed to retrieve data' };
    }
  } catch (error) {
    console.error('Error in GET request:', error);
    return { error: 'Failed to process the request' };
  }
};


// POST method to handle form submission
export async function POST(request: Request) {
  try {
    // Parse the body of the request to extract form data
    const body = await request.json();
    const { startDate, endDate } = body;

    if (!startDate || !endDate) {
      return NextResponse.json({ error: 'Missing required startDate or endDate' }, { status: 400 });
    }

    // Fetch transactions using the provided filters
    const transactions = await fetchTransactionsFromUPBank(startDate, endDate);

    // Return the fetched transactions
    return NextResponse.json(transactions);
  } catch (error) {
    console.error('Error in POST request:', error);
    return NextResponse.json({ error: 'Failed to process the request' }, { status: 500 });
  }
}