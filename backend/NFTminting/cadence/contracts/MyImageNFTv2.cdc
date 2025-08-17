import NonFungibleToken from 0x631e88ae7f1d7c20
import MetadataViews from 0x631e88ae7f1d7c20

access(all) contract MyImageNFTv2: NonFungibleToken {

    access(all) var totalSupply: UInt64

    access(all) event ContractInitialized()
    access(all) event Withdraw(id: UInt64, from: Address?)
    access(all) event Deposit(id: UInt64, to: Address?)

    access(all) let CollectionStoragePath: StoragePath
    access(all) let CollectionPublicPath: PublicPath
    access(all) let MinterStoragePath: StoragePath

    // NFT resource with REQUIRED methods
    access(all) resource NFT: NonFungibleToken.NFT {
        access(all) let id: UInt64
        access(all) let name: String
        access(all) let description: String
        access(all) let imageURI: String
        access(all) let externalURL: String?

        init(
            id: UInt64,
            name: String,
            description: String,
            imageURI: String,
            externalURL: String?
        ) {
            self.id = id
            self.name = name
            self.description = description
            self.imageURI = imageURI
            self.externalURL = externalURL
        }

        // REQUIRED: getViews function
        access(all) view fun getViews(): [Type] {
            return [
                Type<MetadataViews.Display>(),
                Type<MetadataViews.ExternalURL>(),
                Type<MetadataViews.Medias>()
            ]
        }

        // REQUIRED: resolveView function
        access(all) fun resolveView(_ view: Type): AnyStruct? {
            switch view {
            case Type<MetadataViews.Display>():
                return MetadataViews.Display(
                    name: self.name,
                    description: self.description,
                    thumbnail: MetadataViews.HTTPFile(url: self.imageURI)
                )
            case Type<MetadataViews.ExternalURL>():
                if let url = self.externalURL {
                    return MetadataViews.ExternalURL(url)
                }
                return nil
            case Type<MetadataViews.Medias>():
                let media: [MetadataViews.Media] = [
                    MetadataViews.Media(
                        file: MetadataViews.HTTPFile(url: self.imageURI),
                        mediaType: "image"
                    )
                ]
                return MetadataViews.Medias(media)
            default:
                return nil
            }
        }

        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <-create Collection()
        }
    }

    // Collection resource
    access(all) resource Collection:
        NonFungibleToken.Provider,
        NonFungibleToken.Receiver,
        NonFungibleToken.Collection,
        NonFungibleToken.CollectionPublic {

        access(all) var ownedNFTs: @{UInt64: {NonFungibleToken.NFT}}

        init () {
            self.ownedNFTs <- {}
        }

        access(NonFungibleToken.Withdraw) fun withdraw(withdrawID: UInt64): @{NonFungibleToken.NFT} {
            let token <- self.ownedNFTs.remove(key: withdrawID) ?? panic("missing NFT")
            emit Withdraw(id: token.id, from: self.owner?.address)
            return <-token
        }

        access(all) fun deposit(token: @{NonFungibleToken.NFT}) {
            let token <- token as! @MyImageNFTv2.NFT
            let id: UInt64 = token.id
            let oldToken <- self.ownedNFTs[id] <- token
            emit Deposit(id: id, to: self.owner?.address)
            destroy oldToken
        }

        access(all) view fun getIDs(): [UInt64] {
            return self.ownedNFTs.keys
        }

        access(all) view fun borrowNFT(_ id: UInt64): &{NonFungibleToken.NFT}? {
            return (&self.ownedNFTs[id] as &{NonFungibleToken.NFT}?)
        }

        access(all) fun createEmptyCollection(): @{NonFungibleToken.Collection} {
            return <-create Collection()
        }

        access(all) view fun getSupportedNFTTypes(): {Type: Bool} {
            return {Type<@MyImageNFTv2.NFT>(): true}
        }

        access(all) view fun isSupportedNFTType(type: Type): Bool {
            return type == Type<@MyImageNFTv2.NFT>()
        }
    }

    // Minter
    access(all) resource Minter {
        access(all) fun mintNFT(
            name: String,
            description: String,
            imageURI: String,
            externalURL: String?,
            recipient: &{NonFungibleToken.CollectionPublic}
        ) {
            MyImageNFTv2.totalSupply = MyImageNFTv2.totalSupply + 1
            let newID: UInt64 = MyImageNFTv2.totalSupply

            let nft <- create NFT(
                id: newID,
                name: name,
                description: description,
                imageURI: imageURI,
                externalURL: externalURL
            )
            recipient.deposit(token: <- nft)
        }
    }

    access(all) fun createEmptyCollection(nftType: Type): @{NonFungibleToken.Collection} {
        return <- create Collection()
    }

    access(all) fun createMinter(): @Minter {
        return <- create Minter()
    }

    // Contract-level view functions
    access(all) view fun getContractViews(resourceType: Type?): [Type] {
        return []
    }

    access(all) fun resolveContractView(resourceType: Type?, viewType: Type): AnyStruct? {
        return nil
    }

    init() {
        self.totalSupply = 0
        self.CollectionStoragePath = /storage/MyImageNFTCollection
        self.CollectionPublicPath = /public/MyImageNFTCollection
        self.MinterStoragePath = /storage/MyImageNFTMinter

        emit ContractInitialized()
    }
}