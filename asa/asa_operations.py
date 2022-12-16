import json
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn
from algosdk.future.transaction import *

#   Utility function used to print created asset for account and assetid
def print_created_asset(algodclient, account, assetid):    
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = algodclient.account_info(account)
    idx = 0;
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1       
        if (scrutinized_asset['index'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break

#   Utility function used to print asset holding for account and assetid
def print_asset_holding(algodclient, account, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break

algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient("", algod_address)

asset_creator_address = "6L3P4NDQK6P62WUCAYTCAKEGPF6DTLWPEI26DHQCROA3Y5YOIFCLZJKGZM"
creator_private_key = "8n9YjQ+SejltKoUkOvPpaTYvC7fQ2lWtdKdZMiJUz4fy9v40cFef7VqCBiYgKIZ5fDmuzyI14Z4Ci4G8dw5BRA=="

# asset config transaction
txn = AssetConfigTxn(
    sender=asset_creator_address,
    sp=algod_client.suggested_params(),
    total=21000000,
    default_frozen=False,
    unit_name="BTC",
    asset_name="Bitcoin",
    manager=asset_creator_address,
    reserve=asset_creator_address,
    freeze=asset_creator_address,
    clawback=asset_creator_address,
    url="", 
    decimals=0)

# sign the transaction
stxn = txn.sign(creator_private_key)

# send the transaction to the node
try:
    txid = algod_client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
except Exception as err:
    print(err)

# print transaction info
print("Transaction information: {}".format(
    json.dumps(confirmed_txn, indent=4)))

try:
    # Pull account info for the creator
    # account_info = algod_client.account_info(accounts[1]['pk'])
    # get asset_id from tx
    # Get the new asset's information from the creator account
    ptx = algod_client.pending_transaction_info(txid)
    asset_id = ptx["asset-index"]
    print_created_asset(algod_client, asset_creator_address, asset_id)
    print_asset_holding(algod_client, asset_creator_address, asset_id)
except Exception as e:
    print(e)

# OPT-IN

asset_receiver_address = "6E2GZ5O2OWUDY6NI4EZGJLLT3MSRNIMA5HARS5S6T5UIVDIFHOYSFUHNEI"
receiver_private_key = "83I5jEyr+dNlaG1yNCHKR68IOkLuLyXCSunu6bmiA8LxNGz12nWoPHmo4TJkrXPbJRahgOnBGXZen2iKjQU7sQ=="

params = algod_client.suggested_params()

account_info = algod_client.account_info(asset_receiver_address)
holding = None
idx = 0
for my_account_info in account_info['assets']:
    scrutinized_asset = account_info['assets'][idx]
    idx = idx + 1    
    if (scrutinized_asset['asset-id'] == asset_id):
        holding = True
        break

if not holding:
    # Use the AssetTransferTxn class to transfer assets and opt-in
    txn = AssetTransferTxn(
        sender=asset_receiver_address,
        sp=params,
        receiver=asset_receiver_address,
        amt=0,
        index=asset_id)
    stxn = txn.sign(receiver_private_key)
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
    except Exception as err:
        print(err)
    # Now check the asset holding for that account.
    # This should now show a holding with a balance of 0.
    print_asset_holding(algod_client, asset_receiver_address, asset_id)

# TRANSFER ASSET

# transfer asset of 10 from account 1 to account 3
params = algod_client.suggested_params()
# comment these two lines if you want to use suggested params
# params.fee = 1000
# params.flat_fee = True
txn = AssetTransferTxn(
    sender=asset_creator_address,
    sp=params,
    receiver=asset_receiver_address,
    amt=10,
    index=asset_id)
stxn = txn.sign(creator_private_key)
# Send the transaction to the network and retrieve the txid.
try:
    txid = algod_client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

except Exception as err:
    print(err)
# The balance should now be 10.
print_asset_holding(algod_client, asset_receiver_address, asset_id)


# FREEZE ASSET

params = algod_client.suggested_params()
# comment these two lines if you want to use suggested params
# params.fee = 1000
# params.flat_fee = True
txn = AssetFreezeTxn(
    sender=asset_creator_address,
    sp=params,
    index=asset_id,
    target=asset_receiver_address,
    new_freeze_state=True   
    )
stxn = txn.sign(creator_private_key)
# Send the transaction to the network and retrieve the txid.
try:
    txid = algod_client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))    
except Exception as err:
    print(err)
# The balance should now be 10 with frozen set to true.
print_asset_holding(algod_client, asset_receiver_address, asset_id)


# REVOKE ASSET

# The clawback address (Account 2) revokes 10 latinum from Account 3 and places it back with Account 1.
params = algod_client.suggested_params()
# comment these two lines if you want to use suggested params
# params.fee = 1000
# params.flat_fee = True

# Must be signed by the account that is the Asset's clawback address
txn = AssetTransferTxn(
    sender=asset_creator_address,
    sp=params,
    receiver=asset_creator_address,
    amt=10,
    index=asset_id,
    revocation_target=asset_receiver_address
    )
stxn = txn.sign(creator_private_key)
# Send the transaction to the network and retrieve the txid.
try:
    txid = algod_client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4)
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))      
except Exception as err:
    print(err)
print("Receiver")
print_asset_holding(algod_client, asset_receiver_address, asset_id)

print("Creator")
print_asset_holding(algod_client, asset_creator_address, asset_id)


# DESTROY ASSET

# With all assets back in the creator's account,
# the manager (Account 1) destroys the asset.
params = algod_client.suggested_params()
# comment these two lines if you want to use suggested params
# params.fee = 1000
# params.flat_fee = True

# Asset destroy transaction
txn = AssetConfigTxn(
    sender=asset_creator_address,
    sp=params,
    index=asset_id,
    strict_empty_address_check=False
    )

# Sign with secret key of creator
stxn = txn.sign(creator_private_key)
# Send the transaction to the network and retrieve the txid.
# Send the transaction to the network and retrieve the txid.
try:
    txid = algod_client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid, 4) 
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))     
except Exception as err:
    print(err)

# Asset was deleted.
try:
    print("Nothing should print after this as the asset is destroyed on the creator account")
   
    print_asset_holding(algod_client, asset_creator_address, asset_id)
    print_created_asset(algod_client, asset_creator_address, asset_id)
    # asset_info = algod_client.asset_info(asset_id)
except Exception as e:
    print(e)
