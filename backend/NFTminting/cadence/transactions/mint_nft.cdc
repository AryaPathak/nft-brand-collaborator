import MyImageNFTv2 from 0x8e1e0dc93cf85473
import NonFungibleToken from 0x631e88ae7f1d7c20

transaction(
    recipient: Address,
    name: String,
    description: String,
    imageURI: String,
    externalURL: String
) {
    prepare(signer: auth(Storage) &Account) {
        // Get recipient's public collection capability
        let recipientRef = getAccount(recipient)
            .capabilities.get<&{NonFungibleToken.CollectionPublic}>(MyImageNFTv2.CollectionPublicPath)
            .borrow()
            ?? panic("Recipient does not have a public collection capability")

        // Borrow the minter from storage
        let minter = signer.storage.borrow<&MyImageNFTv2.Minter>(from: MyImageNFTv2.MinterStoragePath)
            ?? panic("No minter found. The account needs to create a minter first.")

        // Convert empty string to nil for externalURL
        let finalExternalURL: String? = externalURL == "" ? nil : externalURL

        // Mint the NFT
        minter.mintNFT(
            name: name,
            description: description,
            imageURI: imageURI,
            externalURL: finalExternalURL,
            recipient: recipientRef
        )
    }

    execute {
        log("NFT minted successfully!")
    }
}