import { useEffect, useState } from "react";

type NFT = {
  identifier: string;
  name?: string;
  image_url?: string;
  display_image_url?: string;
  opensea_url?: string;
  token_standard?: string;
  collection?: string;
};

interface Props {
  collectionName: string;
  nfts: NFT[];
  walletAddress: string | null;
}

export default function CollectionViewer({ collectionName, nfts, walletAddress }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<NFT | null>(null);
  const [brandName, setBrandName] = useState("");
  const [editedImage, setEditedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editedImage && selected) {
      const link = document.createElement("a");
      link.href = editedImage;
      link.download = `${selected.name || "edited-nft"}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      console.log("Edited NFT auto-downloaded!");
    }
  }, [editedImage, selected]);

  const PAYMENT_ADDRESS = "0x957a2A8F468f70Ea7FCabadCA7F8FdCF2e38D555";
  const PAYMENT_AMOUNT_ETH = "0.00001"; // Amount in ETH

  if (!nfts || nfts.length === 0) return null;

  const getImage = (i: NFT) => i.image_url || i.display_image_url || "";

  const handleDownload = () => {
    if (!editedImage) return;
    const link = document.createElement("a");
    link.href = editedImage;
    link.download = `${selected?.name || "edited-nft"}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePayment = async (): Promise<boolean> => {
    if (!walletAddress) {
      alert("Please connect your wallet first!");
      return false;
    }
    if (!(window as any).ethereum) {
      alert("Wallet not detected!");
      return false;
    }

    try {
      const valueInWei = BigInt(parseFloat(PAYMENT_AMOUNT_ETH) * 1e18).toString(16);

      const txHash = await (window as any).ethereum.request({
        method: "eth_sendTransaction",
        params: [
          {
            from: walletAddress,
            to: PAYMENT_ADDRESS,
            value: "0x" + valueInWei,
          },
        ],
      });

      console.log("Payment sent. Tx Hash:", txHash);
      alert("Payment successful!");
      return true;
    } catch (err) {
      console.error("Payment failed:", err);
      alert("Payment failed!");
      return false;
    }
  };

const handleEditNFT = async () => {
    if (!selected || !brandName) return alert("Select an NFT and enter a brand");

    const paid = await handlePayment();
    if (!paid) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file_url", getImage(selected));
      formData.append("brand", brandName);

      if (selected.opensea_url) {
        formData.append("metadata_url", selected.opensea_url);
      }

      const res = await fetch("http://127.0.0.1:8000/api/edit-nft", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.error) {
        alert(data.error);
      } else if (data.image_base64) {
        const img = `data:image/png;base64,${data.image_base64}`;
        setEditedImage(img);

        const nftKey = `Generated_NFTs_${brandName || "Unnamed"}_${Date.now()}`;
        localStorage.setItem(nftKey, img);
        console.log("NFT saved to localStorage with key:", nftKey);
      } else if (data.metadata?.image) {
        setEditedImage(data.metadata.image);

        const nftKey = `Generated_NFTs_${brandName || "Unnamed"}_${Date.now()}`;
        localStorage.setItem(nftKey, data.metadata.image);
        console.log("NFT saved to localStorage with key:", nftKey);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to edit NFT");
    } finally {
      setLoading(false);
    }
  };


  return (
  <>
    {/* Cover Card */}
    <div
      onClick={() => setIsOpen(true)}
      className="bg-[#12141a] rounded-xl shadow-md hover:shadow-lg transition p-4 cursor-pointer flex flex-col items-center"
    >
      <img
        src={getImage(nfts[0])}
        alt="Cover"
        className="w-full h-48 object-cover rounded-lg"
      />
      <div className="mt-2 text-accent font-semibold">{collectionName}</div>
    </div>

    {/* Modal */}
    {isOpen && (
      <div className="fixed inset-0 z-50 bg-black/70 flex justify-center items-start overflow-y-auto p-6">
        <div className="bg-[#11141a] rounded-2xl shadow-2xl w-full max-w-6xl p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl text-accent font-bold">{collectionName} Collection</h2>
            <button
              onClick={() => {
                setIsOpen(false);
                setSelected(null);
                setEditedImage(null);
              }}
              className="px-3 py-1 text-sm bg-danger rounded hover:bg-red-500 transition"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* NFT Grid */}
            <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-4">
              {nfts.map((nft) => (
                <div
                  key={nft.identifier}
                  onClick={() => setSelected(nft)}
                  className={`bg-[#161a22] rounded-lg overflow-hidden shadow hover:shadow-lg transition cursor-pointer ${
                    selected?.identifier === nft.identifier ? "border-4 border-accent" : ""
                  }`}
                >
                  <img src={getImage(nft)} alt={nft.name} className="w-full h-48 object-cover" />
                  <div className="p-2 text-sm text-text-muted font-medium">
                    {nft.name || "Unnamed NFT"}
                  </div>
                </div>
              ))}
            </div>

            {/* Details & Brand Panel */}
            <aside className="bg-[#161a22] border border-border rounded-lg p-4 shadow-sm flex flex-col gap-3">
              {selected ? (
                <>
                  <img
                    src={getImage(selected)}
                    alt={selected.name}
                    className="w-full h-56 object-cover rounded"
                  />
                  <input
                    type="text"
                    placeholder="Enter brand name"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    className="border border-border px-3 py-2 text-text-primary rounded-lg bg-[#12141a] focus:outline-none focus:ring-2 focus:ring-accent text-sm"
                  />
                  <button
                    onClick={handleEditNFT}
                    className="bg-success text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-500 disabled:opacity-60 transition"
                    disabled={loading}
                  >
                    {loading ? "Processing..." : "Pay & Edit NFT"}
                  </button>

                  {editedImage && (
                    <>
                      <img
                        src={editedImage}
                        alt="Edited NFT"
                        className="w-full h-56 object-cover rounded mt-3"
                      />
                      <button
                        onClick={async () => {
                          const formData = new FormData();
                          formData.append("file", await fetch(editedImage!).then((r) => r.blob()));
                          formData.append("brand", brandName);

                          const res = await fetch("http://127.0.0.1:8000/api/mint-nft", {
                            method: "POST",
                            body: formData,
                          });

                          if (res.ok) {
                            const data = await res.json();
                            const textContent = JSON.stringify(data, null, 2);
                            const blob = new Blob([textContent], { type: "text/plain" });
                            const url = window.URL.createObjectURL(blob);
                            const link = document.createElement("a");
                            link.href = url;
                            link.download = "nft-info.txt";
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            window.URL.revokeObjectURL(url);

                            if (editedImage) {
                              const nftKey = `Generated_NFTs_${brandName || "Unnamed"}_${Date.now()}`;
                              localStorage.setItem(nftKey, editedImage);
                              alert("NFT Minted & Saved Locally!");
                            }
                          } else {
                            const err = await res.json();
                            alert("Error: " + err.error);
                          }
                        }}
                        className="mt-2 bg-accent text-white px-4 py-2 rounded-lg hover:bg-purple-500 transition"
                      >
                        Convert to NFT
                      </button>

                      <button
                        onClick={handleDownload}
                        className="mt-2 bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-500 transition"
                      >
                        Download Edited NFT
                      </button>
                    </>
                  )}
                </>
              ) : (
                <div className="text-sm text-text-muted">Select an NFT to see details.</div>
              )}
            </aside>
          </div>
        </div>
      </div>
    )}
  </>
);
}