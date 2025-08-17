import MyImageNFTv2 from 0x8e1e0dc93cf85473
import NonFungibleToken from 0x631e88ae7f1d7c20

access(all) fun main(account: Address): [UInt64] {
    let collectionRef = getAccount(account)
        .capabilities.get<&{NonFungibleToken.CollectionPublic}>(MyImageNFTv2.CollectionPublicPath)
        .borrow()
        ?? panic("Could not borrow collection reference")
    
    return collectionRef.getIDs()
}