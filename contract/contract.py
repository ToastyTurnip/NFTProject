"""
FA2 library with the new SmartPy syntax.

Warning:
    Work in progress.
    Currently the metadata cannot be generated.
    It means that you cannot originate your contract with the metadata
    (offchain-views, contract's name and mandatory metadata keys)
"""

import smartpy as sp

FA2 = sp.io.import_script_from_url("https://legacy.smartpy.io/templates/fa2_lib.py")

# create contract of class Nft

class AdLotNFT(
    FA2.Admin,
    FA2.BurnNft,
    FA2.ChangeMetadata,
    FA2.Fa2Nft,
    FA2.OnchainviewBalanceOf,
    FA2.OffchainviewTokenMetadata,
    FA2.WithdrawMutez,

):
    def __init__(self, admin, metadata,
                 lot_id, owner_title, description, image_url, owned, # token-required
                 max_rows, max_columns,
                 token_metadata={}, ledger={}, policy=None, metadata_base=None): # lot_id is right sequence of grid (0,0) has lot_id = 1
        FA2.Fa2Nft.__init__(self, metadata, token_metadata=token_metadata, ledger=ledger, policy=policy, metadata_base=metadata_base)
        FA2.Admin.__init__(self, admin)

        self.update_initial_storage(
            lot_id=lot_id,
            description=description,
            image_url=image_url,
            owner_title=owner_title,
            max_rows=max_rows,
            max_columns=max_columns,
            owned=owned # unsure if this is needed
        )
    
    @sp.entrypoint
    def mint(self, owner):
        # todo
        sp.verify(self.data.owned, "Lot is already owned")
        sp.verify(self.data.lot_id < self.data.max_columns * self.data.max_rows, "Over the lot count limit")
        
        token_id = sp.compute(self.data.last_token_id)

        (x_coord, y_coord) = sp.ediv(self.data.lot_id, sp.nat(self.data.max_rows)).unwrap_some(error="Division by 0")


        self.data.ledger[token_id] = owner
        self.data.token_metadata[token_id] = sp.record(
            token_id=token_id, token_info=sp.map({
                "name": "LotNFT",
                "symbol": sp.utils.bytes_of_string("LTNFT"),
                "lot_id": self.data.lot_id,
                "x_coord": x_coord,
                "y_coord": y_coord,
                "description": self.data.description,
                "image_url": self.data.image_url,
                "owner_title": self.data.owner_title,
                "owned": self.data.owned,
            })
        )
        self.data.last_token_id += 1

class LotFactory(sp.Contract):
    def __init__(self, admin, max_columns, max_rows):
        self.init(
            admin=admin,
            lotContracts=sp.big_map(tkey=sp.TNat, tvalue=sp.TAddress),
            max_columns=max_columns,
            max_rows=max_rows,
            lotContractCount=0
        )
    
    @sp.entry_point
    def create_lot(self, lot_id, owner_title, description, image_url, owned, metadata):
        sp.verify(sp.sender == self.data.admin, "User is not an admin")

        lotContract = AdLotNFT(
            lot_id=lot_id,
            owner_title=owner_title,
            description=description,
            image_url=image_url,
            owned=owned,
            max_columns=self.data.max_columns,
            max_rows=self.data.max_rows,
            metadata=metadata,
            admin=self.data.admin
        )

        self.data.lotContracts[self.data.lotContractCount] = sp.create_contract(contract=lotContract)
        self.data.lotContractCount+=1