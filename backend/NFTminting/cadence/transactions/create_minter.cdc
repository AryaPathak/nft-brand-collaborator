import MyImageNFTv2 from 0x8e1e0dc93cf85473

transaction {
    prepare(signer: auth(Storage) &Account) {
        // Remove old minter if it exists
        if signer.storage.borrow<&AnyResource>(from: MyImageNFTv2.MinterStoragePath) != nil {
            let oldMinter <- signer.storage.load<@AnyResource>(from: MyImageNFTv2.MinterStoragePath)
            destroy oldMinter
        }
        
        // Create and save the new minter
        let minter <- MyImageNFTv2.createMinter()
        signer.storage.save(<-minter, to: MyImageNFTv2.MinterStoragePath)
    }

    execute {
        log("Minter v2 created and saved to storage")
    }
}