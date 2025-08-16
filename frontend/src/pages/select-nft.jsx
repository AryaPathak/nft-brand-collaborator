import { useState } from "react";
import { fetchNFTs } from "../services/backendAPI";

export default function SelectNFT() {
  const [owner, setOwner] = useState("");
  const [nfts, setNfts] = useState([]);

  const handleFetch = async () => {
    const fetched = await fetchNFTs(owner);
    setNfts(fetched);
  };

  return (
    <div className="p-8">
      <input
        value={owner}
        onChange={(e) => setOwner(e.target.value)}
        placeholder="Enter wallet address"
        className="border px-2 py-1 mr-2"
      />
      <button onClick={handleFetch} className="bg-blue-600 text-white px-4 py-1 rounded">
        Fetch NFTs
      </button>
      <div className="mt-4 grid grid-cols-3 gap-4">
        {nfts.map((nft) => (
          <div key={nft.token_id} className="border p-2 rounded">
            <img src={nft.image_url} alt={nft.name} className="w-full aspect-square object-cover" />
            <h2 className="mt-2 font-semibold">{nft.name}</h2>
            <p className="text-sm text-gray-600">{nft.collection}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
