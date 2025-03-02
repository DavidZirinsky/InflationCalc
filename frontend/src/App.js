import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // Format date for display
  const formatDate = (dateString) => {
    console.log(`dateString: ${dateString}`);

    // Extract year and month correctly
    const [year, month] = dateString.split('-').map(Number);

    // Create a date object with the correct month (subtract 1 for zero-based indexing)
    const date = new Date(Date.UTC(year, month - 1, 3)); // Use the 3rd day to avoid timezone issues

    return date.toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });
  };

  // Generate month options for dropdown (from Jan 1913 to previous month)
  const generateMonthOptions = () => {
    const options = [];
    const startYear = 1913;

    for (let year = startYear; year <= prevYear; year++) {
      const monthLimit = year === prevYear ? prevMonth : 12;

      for (let month = 1; month <= monthLimit; month++) {
        const value = `${year}-${String(month).padStart(2, '0')}`; // Correct format YYYY-MM
        const label = formatDate(value); // Use formatDate for consistency

        options.push({ value, label });
      }
    }

    return options;
  };

  // Get current date and calculate previous month for default end date
  const currentDate = new Date();
  const prevMonthDate = new Date();
  prevMonthDate.setMonth(currentDate.getMonth() - 1);

  const currentYear = currentDate.getFullYear();
  const currentMonth = currentDate.getMonth() + 1; // JavaScript months are 0-indexed

  const prevYear = prevMonthDate.getFullYear();
  const prevMonth = prevMonthDate.getMonth() + 1;

  // Format default dates (start = Jan 2020, end = previous month)
  const formattedPrevMonth = `${prevYear}-${String(prevMonth).padStart(2, '0')}`;

  // State initialization
  const [startDate, setStartDate] = useState('2020-01');
  const [endDate, setEndDate] = useState(formattedPrevMonth);
  const [amount, setAmount] = useState(1000);
  const [forwardResult, setForwardResult] = useState(null);
  const [reverseResult, setReverseResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const endDateObj = new Date(`${endDate}-01`);
    const startDateObj = new Date(`${startDate}-01`);

    if (endDateObj > prevMonthDate) {
      setEndDate(formattedPrevMonth);
    }

    if (endDateObj < startDateObj) {
      setEndDate(startDate);
    }
  }, [startDate, endDate, formattedPrevMonth]);

  const monthOptions = generateMonthOptions();

  const calculateInflation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Ensure correct formatting when sending to API
      const startDateFormatted = `${startDate}-03`;
      const endDateFormatted = `${endDate}-03`;

      const forwardUrl = `https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/calc?amount=${amount}&start_date=${startDateFormatted}&end_date=${endDateFormatted}`;

      const reverseUrl = `https://fskgad1wub.execute-api.us-east-1.amazonaws.com/prod/inflation/reverse?amount=${amount}&start_date=${startDateFormatted}&end_date=${endDateFormatted}`;

      const [forwardResponse, reverseResponse] = await Promise.all([
        fetch(forwardUrl),
        fetch(reverseUrl)
      ]);

      if (!forwardResponse.ok || !reverseResponse.ok) {
        throw new Error('Failed to fetch inflation data');
      }

      const forwardData = await forwardResponse.json();
      const reverseData = await reverseResponse.json();

      setForwardResult(forwardData);
      setReverseResult(reverseData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching inflation data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="calculator-card">
        <div className="card-header">
          <h1>Inflation Calculator</h1>
          <p>Compare the value of money over time</p>
        </div>

        <div className="calculator-form">
          <div className="form-group">
            <label htmlFor="amount">Amount ($)</label>
            <div className="input-with-prefix">
              <span className="input-prefix">$</span>
              <input
                type="number"
                id="amount"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>

          <div className="date-inputs">
            <div className="form-group">
              <label htmlFor="startDate">Start Month</label>
              <select
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="date-select"
              >
                {monthOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="endDate">End Month</label>
              <select
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="date-select"
              >
                {monthOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={calculateInflation}
            disabled={isLoading}
            className="calculate-button"
          >
            {isLoading ? 'Calculating...' : 'Calculate Inflation'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        {forwardResult && reverseResult && (
          <div className="results-container">
            <div className="result-card forward">
              <h2>Forward Calculation</h2>
              <p className="result-line">
                ${forwardResult.original_amount.toFixed(2)} from {formatDate(forwardResult.start_date)} would be worth
              </p>
              <p className="result-value">
                ${forwardResult.adjusted_amount.toFixed(2)} in {formatDate(forwardResult.end_date)}
              </p>
            </div>

            <div className="result-card reverse">
              <h2>Reverse Calculation</h2>
              <p className="result-line">
                To have ${reverseResult.original_amount.toFixed(2)} in {formatDate(reverseResult.end_date)}, you would need
              </p>
              <p className="result-value">
                ${reverseResult.adjusted_amount.toFixed(2)} in {formatDate(reverseResult.start_date)}
              </p>
            </div>
          </div>
        )}

        <div className="card-footer">
          Data based on Consumer Price Index (CPI) from the U.S. Bureau of Labor Statistics
        </div>
      </div>
    </div>
  );
}

export default App;
