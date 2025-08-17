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
  const [collections, setCollections] = useState<
    { name: string; nfts: any[] }[]
  >([]);
  const [balances, setBalances] = useState<any[]>([]);

  const connectWallet = async () => {
    try {
      const APP_NAME = "NFT Brand Customizer";
      const APP_LOGO_URL = "https://example.com/logo.png";

      const coinbaseWallet = new CoinbaseWalletSDK({
        appName: APP_NAME,
        appLogoUrl: APP_LOGO_URL,
      });
      const ethereum = coinbaseWallet.makeWeb3Provider();
      const accounts = (await ethereum.request({
        method: "eth_requestAccounts",
      })) as string[];

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
      const res = await fetch(
        `http://127.0.0.1:8001/balances?address=${address}&network=base-sepolia`
      );
      const data = await res.json();
      setBalances(data.balances || []);
    } catch (error) {
      console.error("Error fetching balances:", error);
    }
  };

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const names = [
          "cryptopunks",
          "cartlads",
          "doodles-official",
          "azuki",
          "bad-bunnz",
          "boredapeyachtclub",
        ];
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
    <div className="min-h-screen bg-[#0b0d10] text-[#e6edf3] p-6">
      {/* Top Navigation */}
      <div className="flex items-start justify-between mb-10 flex-wrap">
        {/* Fetch NFTs */}
        <div className="flex flex-col items-start gap-2">
          <div className="flex items-center gap-3">
            <label className="sr-only" htmlFor="username">
              OpenSea Username
            </label>
            <input
              id="username"
              type="text"
              placeholder="Enter OpenSea username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="border border-border bg-surface rounded-xl px-4 py-2 w-64 text-sm placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition"
            />
            <button
              onClick={fetchNFTs}
              aria-label="Fetch NFTs"
              className="bg-success hover:bg-green-500 text-white px-4 py-2 rounded-xl font-semibold shadow-lg transition duration-200 focus:outline-none focus:ring-2 focus:ring-success/60 focus:ring-offset-2 focus:ring-offset-[#0b0d10]"
            >
              Fetch NFTs
            </button>
          </div>
          {/* Optional smaller token balance below Fetch NFTs */}
        </div>

        {/* Wallet Connect */}
        <div className="flex flex-col items-end gap-2">
          {!walletAddress ? (
            <button
              onClick={connectWallet}
              aria-label="Connect Coinbase Wallet"
              className="px-5 py-2 bg-primary hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg transition duration-200 focus:outline-none focus:ring-2 focus:ring-primary/70 focus:ring-offset-2 focus:ring-offset-[#0b0d10]"
            >
              Connect Wallet
            </button>
          ) : (
            <>
              <p className="px-4 py-1 bg-success/20 text-success rounded-lg shadow-md text-xs font-mono border border-success/30 truncate max-w-[200px]">
                {`Connected: ${walletAddress}`}
              </p>

              {/* Token Balances below wallet button */}
              {balances.length > 0 && (
                <div className="bg-surface p-3 rounded-xl shadow-md w-60 mt-2 border border-border text-sm">
                  <h4 className="font-semibold text-primary mb-2 text-sm">
                    Token Balances
                  </h4>
                  <ul className="divide-y divide-border">
                    {balances.map((bal: any, i: number) => (
                      <li
                        key={i}
                        className="py-1 flex justify-between text-gray-300"
                      >
                        <span className="truncate">{bal.name}</span>
                        <span className="font-mono">
                          {bal.amount.toFixed(6)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Header */}
      <h1 className="text-5xl md:text-6xl font-extrabold text-primary mb-4 text-center tracking-tight drop-shadow-md font-sans uppercase">
        NBC
      </h1>
      <p className="text-center text-text-muted text-lg md:text-xl mb-12 max-w-2xl mx-auto">
        Customize, showcase, and amplify your NFT brand with style and ease.
      </p>

      {/* Brand Recommendation Input */}
      <div className="flex justify-center gap-3 mb-12 flex-wrap">
        <button
          onClick={() => setShowRecommendation(true)}
          aria-label="Get Personalized Recommendation"
          className="bg-accent hover:bg-purple-600 bg-purple-500 text-white px-5 py-2 rounded-xl font-semibold shadow-lg transition duration-200 focus:outline-none focus:ring-2 focus:ring-accent/60 focus:ring-offset-2 focus:ring-offset-[#0b0d10]"
        >
          Get Personalized Recommendation
        </button>
      </div>

      {/* Account Info */}
      {account && (
        <div className="max-w-md mx-auto mb-10 p-5 bg-surface rounded-xl shadow-lg flex items-center gap-4 border border-border">
          {account.profile_image_url && (
            <img
              src={account.profile_image_url}
              alt="Profile"
              className="w-16 h-16 rounded-full border border-border object-cover"
            />
          )}
          <div className="overflow-hidden">
            <h2 className="font-semibold text-lg text-white truncate">
              {account.username}
            </h2>
            <p className="text-text-muted text-sm break-all font-mono">
              {account.address}
            </p>
          </div>
        </div>
      )}

      {/* NFT Collections Grid */}
      <div className="max-w-6xl mx-auto p-4">
        {collections.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {collections.map((col) => (
              <CollectionViewer
                key={col.name}
                collectionName={col.name}
                nfts={col.nfts}
                walletAddress={walletAddress}
              />
            ))}
          </div>
        ) : (
          <p className="text-center text-text-muted italic mt-10">
            No NFT collections found. Connect your wallet or enter a username to
            fetch NFTs.
          </p>
        )}
      </div>

      {/* Recommendation Modal */}
      {showRecommendation && (
        <RecommendationViewer
          brandName={brandName}
          onClose={() => setShowRecommendation(false)}
        />
      )}
    </div>
  );
}
