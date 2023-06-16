import smartpy as sp

from templates import fa2_lib as fa2
from templates import fa2_lib_testing as testing

administrator = sp.test_account("Administrator")
alice = sp.test_account("Alice")
tok0_md = fa2.make_metadata(name="Token Zero", decimals=1, symbol="Tok0")
tok1_md = fa2.make_metadata(name="Token One", decimals=1, symbol="Tok1")
tok2_md = fa2.make_metadata(name="Token Two", decimals=1, symbol="Tok2")
TOKEN_METADATA = [tok0_md, tok1_md, tok2_md]
METADATA = sp.utils.metadata_of_url("ipfs://example")

main = fa2.main


@sp.module
def m():
    # Order of inheritance: [Admin], [<policy>], <base class>, [<mixins>]
    lot_claims: type = sp.big_map[sp.nat, sp.nat]
    
    class NftTestFull(
        main.Admin,
        main.Nft,
        main.ChangeMetadata,
        main.WithdrawMutez,
        main.MintNft,
        main.BurnNft,
        main.OffchainviewTokenMetadata,
        main.OnchainviewBalanceOf,
    ):
        def __init__(self, administrator, metadata, ledger, token_metadata):
            main.OnchainviewBalanceOf.__init__(self)
            main.OffchainviewTokenMetadata.__init__(self)
            main.BurnNft.__init__(self)
            main.MintNft.__init__(self)
            main.WithdrawMutez.__init__(self)
            main.ChangeMetadata.__init__(self)
            main.Nft.__init__(self, metadata, ledger, token_metadata)
            main.Admin.__init__(self, administrator)
            self.data.lot_claims = sp.cast(sp.big_map(), lot_claims)
            self.data.max_columns = sp.nat(10)
            self.data.max_rows = sp.nat(10)

        @sp.entrypoint
        def mint(self, batch):

            sp.cast(
                batch,
                sp.list[
                    sp.record(
                        to_=sp.address,
                        metadata=sp.map[sp.string, sp.bytes],
                    ).layout(("to_", "metadata"))
                ],
            )
            
            # todo
            assert self.is_administrator_(), "FA2_NOT_ADMIN"
            
            for action in batch:
                assert sp.unpack(action.metadata['lot_id'], sp.nat).unwrap() < (self.data.max_columns * self.data.max_rows) , "Over the lot count limit"
                assert self.data.lot_claims.get(sp.cast(action.metadata['lot_id'], sp.nat), default=sp.nat(1)) == sp.nat(1), "Lot already claimed"
                
                token_id = self.data.last_token_id
                (x_coord, y_coord) = sp.ediv(self.data.lot_id, self.data.max_rows).unwrap_some(error="Division by 0")
                
                self.data.ledger[token_id] = action.to_

                self.data.token_metadata[token_id] = sp.record(
                    token_id=token_id, token_info={
                        "name": sp.pack("LotNFT"),
                        "symbol": sp.pack("LTNFT"),
                        "lot_id": sp.pack(action.metadata.get('lot_id', default=1000)),
                        "x_coord": sp.pack(x_coord),
                        "y_coord": sp.pack(y_coord,),
                        "description": sp.pack("desc here"),
                        "image_url": sp.pack(action.metadata.get("image_url", default="ipfs://sana")),
                        "owner_title": sp.pack(action.metadata.get("owner_title", default="OWNER")),
                    })
                
                self.data.last_token_id += 1
            


@sp.add_test(name="NFT", is_default=True)
def test():
    ledger = {0: alice.address, 1: alice.address, 2: alice.address}
    token_metadata = TOKEN_METADATA

    # Default NFT
    c1 = m.NftTestFull(
        administrator=administrator.address,
        metadata=METADATA,
        ledger=ledger,
        token_metadata=token_metadata,
    )

    kwargs = {"modules": [fa2.t, fa2.main, m], "ledger_type": "NFT"}

    # Standard features
    testing.test_core_interfaces(c1, **kwargs)
    testing.test_transfer(c1, **kwargs)
    testing.test_balance_of(c1, **kwargs)