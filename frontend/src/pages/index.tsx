import { useState, useEffect } from "react";
import CoinbaseWalletSDK from "@coinbase/wallet-sdk";
import CollectionViewer from "./CollectionViewer";
import RecommendationViewer from "./recommendationNFT";

export default function Home() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [brandName, setBrandName] = useState(""); // ✅ new state for brand input
  const [showRecommendation, setShowRecommendation] = useState(false); // ✅ toggle modal
  const [nfts, setNfts] = useState<any[]>([]);
  const [account, setAccount] = useState<any>(null);
  const [collections, setCollections] = useState<{ name: string; nfts: any[] }[]>([]);
  const [balances, setBalances] = useState<any[]>([]);

  const connectWallet = async () => {
    try {
      const APP_NAME = "NFT Brand Customizer";
      const APP_LOGO_URL = "https://example.com/logo.png";

      const coinbaseWallet = new CoinbaseWalletSDK({ appName: APP_NAME, appLogoUrl: APP_LOGO_URL });
      const ethereum = coinbaseWallet.makeWeb3Provider();
      const accounts = (await ethereum.request({ method: "eth_requestAccounts" })) as string[];

      if (accounts?.length) setWalletAddress(accounts[0]);
    } catch (error) {
      console.error("Wallet connection failed:", error);
    }
  };

  const fetchNFTs = async () => {
    if (!username) return alert("Please enter username");
    try {
      const res = await fetch(`http://127.0.0.1:8000/nfts/${username}`);
      const data = await res.json();
      setAccount(data.account || null);
      setNfts(data.nfts?.nfts || []);
    } catch (error) {
      console.error("Error fetching NFTs:", error);
    }
  };

  const fetchBalances = async (address: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8001/balances?address=${address}&network=base-sepolia`);
      const data = await res.json();
      setBalances(data.balances || []);
    } catch (error) {
      console.error("Error fetching balances:", error);
    }
  };

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const names = ["cryptopunks", "cartlads", "doodles-official"];
        const results = await Promise.all(
          names.map(async (name) => {
            const res = await fetch(`http://127.0.0.1:8000/collection/${name}`);
            const data = await res.json();
            return { name, nfts: data.nfts?.nfts || [] };
          })
        );
        setCollections(results);
      } catch (error) {
        console.error("Error fetching collections:", error);
      }
    };
    fetchCollections();
  }, []);

  useEffect(() => {
    if (walletAddress) {
      fetchBalances(walletAddress);
    }
  }, [walletAddress]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <h1 className="text-3xl font-extrabold text-blue-600 mb-6 text-center">
        NFT Brand Customizer
      </h1>

      {/* Wallet Connect */}
      <div className="flex flex-col items-center gap-4 mb-6">
        {!walletAddress ? (
          <button
            onClick={connectWallet}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition duration-200"
          >
            Connect Coinbase Wallet
          </button>
        ) : (
          <>
            <p className="px-6 py-3 bg-green-100 text-green-800 rounded-lg shadow">
              {`Connected: ${walletAddress}`}
            </p>
            {balances.length > 0 && (
              <div className="bg-white p-4 rounded-lg shadow w-full max-w-md">
                <h3 className="font-bold text-blue-400 text-lg mb-2">Token Balances</h3>
                <ul className="divide-y text-blue-400 divide-gray-200">
                  {balances.map((bal: any, i: number) => (
                    <li key={i} className="py-2 flex justify-between text-sm">
                      <span>{bal.name}</span>
                      <span>{bal.amount.toFixed(6)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>

      {/* Username input and fetch button */}
      <div className="flex justify-center gap-3 mb-6">
        <input
          type="text"
          placeholder="Enter OpenSea username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border border-gray-300 rounded-lg px-4 py-2 w-64 focus:outline-none placeholder-gray-500 focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={fetchNFTs}
          className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg font-semibold transition duration-200"
        >
          Fetch NFTs
        </button>
      </div>

      {/* ✅ Brand Recommendation Input */}
      <div className="flex justify-center gap-3 mb-8">
        <input
          type="text"
          placeholder="Enter your Brand name"
          value={brandName}
          onChange={(e) => setBrandName(e.target.value)}
          className="border border-gray-300 rounded-lg px-4 py-2 w-64 focus:outline-none placeholder-gray-500 focus:ring-2 focus:ring-purple-400"
        />
        <button
          onClick={() => setShowRecommendation(true)}
          className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-lg font-semibold transition duration-200"
        >
          Get Personalised Recommendation
        </button>
      </div>

      {/* Account Info */}
      {account && (
        <div className="max-w-md mx-auto mb-6 p-5 bg-white rounded-xl shadow-md flex items-center gap-4">
          {account.profile_image_url && (
            <img
              src={account.profile_image_url}
              alt="Profile"
              className="w-16 h-16 rounded-full"
            />
          )}
          <div>
            <h2 className="font-bold text-lg text-gray-800">{account.username}</h2>
            <p className="text-gray-600 text-sm break-all">{account.address}</p>
          </div>
        </div>
      )}

      {/* NFT Collections Grid */}
      <div className="max-w-6xl mx-auto p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {collections.map((col) => (
            <CollectionViewer
              key={col.name}
              collectionName={col.name}
              nfts={col.nfts}
              walletAddress={walletAddress}
            />
          ))}
        </div>
      </div>

      {/* ✅ Show Recommendation Modal */}
      {showRecommendation && (
        <RecommendationViewer
          brandName={brandName}
          onClose={() => setShowRecommendation(false)}
        />
      )}
    </div>
  );
}
