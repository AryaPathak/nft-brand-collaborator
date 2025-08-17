import MyImageNFTv2 from 0x8e1e0dc93cf85473
import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20

transaction {
    prepare(signer: auth(Storage, Capabilities) &Account) {
        // First, check if there's an old collection and remove it
        if signer.storage.borrow<&AnyResource>(from: MyImageNFTv2.CollectionStoragePath) != nil {
            let oldCollection <- signer.storage.load<@AnyResource>(from: MyImageNFTv2.CollectionStoragePath)
            destroy oldCollection
            
            // Also unpublish the old capability
            signer.capabilities.unpublish(MyImageNFTv2.CollectionPublicPath)
        }
        
        // Now create a new collection for the v2 contract
        let collection <- MyImageNFTv2.createEmptyCollection(nftType: Type<@MyImageNFTv2.NFT>()) as! @MyImageNFTv2.Collection
        
        // Save the collection to storage
        signer.storage.save(<-collection, to: MyImageNFTv2.CollectionStoragePath)
        
        // Create a public capability for the collection
        let collectionCap = signer.capabilities.storage.issue<&MyImageNFTv2.Collection>(MyImageNFTv2.CollectionStoragePath)
        signer.capabilities.publish(collectionCap, at: MyImageNFTv2.CollectionPublicPath)
    }

    execute {
        log("NFT Collection v2 created and linked to public path")
    }
}