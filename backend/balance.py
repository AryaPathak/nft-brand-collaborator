import os
import asyncio
from cdp import CdpClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    async with CdpClient() as cdp:
        address = os.getenv("TARGET_ADDRESS")
        if not address:
            print("Please set TARGET_ADDRESS in your environment or code.")
            return

        network = "ethereum"  # or "base-sepolia", "ethereum", etc.
        # Corrected call
        result = await cdp.evm.list_token_balances(address, network)

        print(f"Token balances for {address} on {network}:")
        for bal in result.balances:
            token = bal.token
            amount = int(bal.amount.amount)
            decimals = int(bal.amount.decimals)
            human_amount = amount / (10 ** decimals)

            contract = token.contract_address
            name = getattr(token, "name", None) or getattr(token, "symbol", None)

            if contract.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee':
                print(f"- Native Token (ETH-like): {human_amount:.6f}")
            elif name:
                print(f"- {name}: {human_amount:.6f} (contract: {contract})")
            else:
                print(f"- Token (contract: {contract}): {human_amount:.6f}")

if __name__ == "__main__":
    asyncio.run(main())
