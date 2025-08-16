import os
import asyncio
from fastapi import FastAPI, HTTPException
from cdp import CdpClient
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()


app = FastAPI(title="Web3 Token Balance API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class TokenBalance(BaseModel):
    name: str
    contract: str
    amount: float

class BalanceResponse(BaseModel):
    address: str
    network: str
    balances: List[TokenBalance]

# Fetch balances function
# Fetch balances function
async def fetch_balances(address: str, network: str) -> List[TokenBalance]:
    async with CdpClient() as cdp:
        try:
            result = await cdp.evm.list_token_balances(address, network)
        except Exception:
            # If API fails or no balances, return zero balance
            return [TokenBalance(name="Native Token", contract="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", amount=0.0)]

        balances = []

        if not result.balances:
            # If no balances returned, return native token with 0
            balances.append(TokenBalance(
                name="Native Token",
                contract="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                amount=0.0
            ))
            return balances

        for bal in result.balances:
            token = bal.token
            amount = int(bal.amount.amount)
            decimals = int(bal.amount.decimals)
            human_amount = amount / (10 ** decimals)

            contract = token.contract_address
            name = getattr(token, "name", None) or getattr(token, "symbol", None) or "Unknown"

            if contract.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                name = "Native Token"

            balances.append(TokenBalance(name=name, contract=contract, amount=human_amount))

        return balances


# API endpoint
@app.get("/balances", response_model=BalanceResponse)
async def get_balances(address: str = None, network: str = "base-sepolia"):
    # Use .env address if none provided
    if not address:
        address = os.getenv("TARGET_ADDRESS")
        if not address:
            raise HTTPException(status_code=400, detail="No address provided and TARGET_ADDRESS not set in .env")

    try:
        balances = await fetch_balances(address, network)
        return BalanceResponse(address=address, network=network, balances=balances)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
