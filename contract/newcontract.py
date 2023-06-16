import smartpy as sp

class NFTContract(sp.Contract):
    def __init__(self):
        self.init(
            balances = sp.big_map(tkey=sp.TAddress, tvalue=sp.TNat),
            token_metadata = sp.big_map(tkey=sp.TNat, tvalue=sp.TMap(sp.TString, sp.TString)),
            next_token_id = 0
        )

    @sp.entry_point
    def mint(self, params):
        sp.verify(sp.sender == params.creator, message="Only the creator can mint tokens.")
        token_id = self.data.next_token_id
        self.data.next_token_id += 1

        sp.verify(~self.data.balances.contains(token_id), message=f"Token ID {token_id} already exists.")

        self.data.balances[token_id] = params.creator
        self.data.token_metadata[token_id] = sp.map(
            {
                "title": params.title,
                "description": params.description,
                "image_url": params.image_url
            }
        )

    @sp.entry_point
    def burn(self, params):
        token_id = params.token_id
        sp.verify(self.data.balances.contains(token_id), message=f"Token ID {token_id} does not exist.")
        sp.verify(sp.sender == self.data.balances[token_id], message="Only the token owner can burn the token.")

        del self.data.balances[token_id]
        del self.data.token_metadata[token_id]

    @sp.entry_point
    def transfer(self, params):
        token_id = params.token_id
        sp.verify(self.data.balances.contains(token_id), message=f"Token ID {token_id} does not exist.")
        sp.verify(sp.sender == self.data.balances[token_id], message="Only the token owner can transfer the token.")

        sp.verify(params.to != sp.address(0), message="Invalid recipient address.")
        self.data.balances[token_id] = params.to

    @sp.view(sp.TAddress)
    def get_token_owner(self, token_id):
        sp.verify(self.data.balances.contains(token_id), message=f"Token ID {token_id} does not exist.")
        return self.data.balances[token_id]

@sp.add_test(name="NFT Contract")
def test():
    scenario = sp.test_scenario()

    creator = sp.test_account("Creator")
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")

    contract = NFTContract()

    scenario.h1("Mint NFT")
    scenario += contract.mint(
        creator = creator.address,
        title = "My NFT",
        description = "An example NFT",
        image_url = "https://example.com/image.png"
    ).run(sender=creator)

    token_id = 0

    scenario.h1("Transfer NFT")
    scenario += contract.transfer(
        token_id = token_id,
        to = alice.address
    ).run(sender=creator)

    scenario.h1("Burn NFT")
    scenario += contract.burn(
        token_id = token_id
    ).run(sender=alice)

    scenario.h1("Check Token Owner")
    scenario += contract.get_token_owner(token_id).run(sender=creator)

sp.add_compilation_target("NFTContract", NFTContract())
