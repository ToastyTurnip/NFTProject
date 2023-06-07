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
    def __init__(self, admin, metadata, token_metadata={}, ledger={}, policy=None, metadata_base=None,
                 lot_id, owner_title, description, image_url, owner): # lot_id is right sequence of grid (0,0) has lot_id = 1
        FA2.Fa2Nft.__init__(self, metadata, token_metadata=token_metadata, ledger=ledger, policy=policy, metadata_base=metadata_base)
        FA2.Admin.__init__(self, admin)

        self.update_initial_storage(
            lot_id=lot_id,
            description=description,
            image_url=image_url,
            owner_title=owner_title,
            owner=owner # unsure if this is needed
        )
    
    @sp.entrypoint
    def mint(self, owner):
        # todo