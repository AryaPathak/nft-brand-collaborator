import MyImageNFTv2 from 0x8e1e0dc93cf85473
import NonFungibleToken from 0x631e88ae7f1d7c20

access(all) fun main(account: Address, nftID: UInt64): {String: String} {
    let collectionRef = getAccount(account)
        .capabilities.get<&{NonFungibleToken.CollectionPublic}>(MyImageNFTv2.CollectionPublicPath)
        .borrow()
        ?? panic("Could not borrow collection reference")
    
    let nftRef = collectionRef.borrowNFT(nftID)
        ?? panic("Could not borrow NFT reference")
    
    // Cast to our specific NFT type to access custom fields
    let myNFT = nftRef as! &MyImageNFTv2.NFT
    
    let result: {String: String} = {
        "id": myNFT.id.toString(),
        "name": myNFT.name,
        "description": myNFT.description,
        "imageURI": myNFT.imageURI,
        "externalURL": myNFT.externalURL ?? ""
    }
    
    return result
}