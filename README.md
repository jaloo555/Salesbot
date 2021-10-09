if it's a candy machine project, all sales are reported through the candy machine wallet. So it's possible to run a scheduler which parses the transactions and reports to twitter
so it works with all marketplaces
I made a Nodejs app which does this, and i run it in a Docker on my own NAS. But you can deploy it to heroku as well
parses the account transactions: https://explorer.solana.com/address/JxHSVXXsXArCaBRNzCmYBLaBVH7EJ7XHXw14cbzWtqT
Explorer | Solana
Look up transactions and accounts on the various Solana clusters
parses each individual transaction, checks if it's a sale
gets token info for the sale
if it reports succesfully it stores the transaction in a cache.json file, to prevent duplicate posting
that's the gist
got a doctors appointment, be back in 1-2 hours
let me know if you have any questions 
# SalesBot
# SalesBot
