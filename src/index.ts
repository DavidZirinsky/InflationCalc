import express from "express";
import dotenv from 'dotenv';
import axios from "axios";

dotenv.config();
const fredApiUrl = "https://api.stlouisfed.org/fred/series/observations"
const app = express();
const PORT = 3000;

// common math used by two functions
async function calculateInflationDifference(amount: number, startDate: string, endDate: string, reverse: boolean){
    const data = await getCPIData(startDate, endDate);
    let observations = data.observations
    if (observations == null){
        throw new Error("No Observations from FRED")
    }
    let startCpi = observations[0].value
    let endCpi = observations[observations.length-1].value
    console.log(startCpi, endCpi)
    let adjustedAmount = 0
    if (reverse){
        adjustedAmount = amount * (startCpi / endCpi)
    }
    else{
        adjustedAmount = amount * (endCpi / startCpi)
    }
    return adjustedAmount.toFixed(2) // round to two decimal places

}

async function getCPIData(startDate: string, endDate: string): Promise<any> {
    let params = {
        'series_id': 'CPIAUCSL',  // CPI for All Urban Consumers: All Items
        'api_key': process.env.FRED_API_KEY,
        'file_type': 'json',
        'observation_start': startDate,
        'observation_end': endDate, 
    }
    try {
        const response = await axios.get(fredApiUrl, {params});
        return response.data;
      } catch (error) {
        let error_message = `Error fetching FRED data: ${error.response?.data}`
        console.error(error_message);
        throw new Error(error_message)
      }
}


app.use(express.json()); // Middleware to parse JSON request bodies


// Generic route handler for inflation calculations
const handleInflationRequest = async (req: express.Request, res: express.Response, reverse: boolean) => {
    try {
        const { amount, start_date, end_date } = req.body;

        if (!amount || !start_date || !end_date) {
            return res.status(400).json({ error: "Missing required fields: amount, start_date, end_date" });
        }

        const data = await calculateInflationDifference(amount, start_date, end_date, reverse);
        res.status(200).json({ amount: data });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: (error as Error).message || "An unknown error occurred" });
    }
};

app.post("/inflation", (req, res) => handleInflationRequest(req, res, false));
app.post("/reverseInflation", (req, res) => handleInflationRequest(req, res, true));


app.listen(PORT, () => {
  console.log(`⚡ Server is running at http://localhost:${PORT}`);
});