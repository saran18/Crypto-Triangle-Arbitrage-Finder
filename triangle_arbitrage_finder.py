import ccxt.pro
import time

def run():
    arbitrage()
    time.sleep(20)

def find_transitive_sets(graph):
    transitive_sets = []

    for i in graph:
        for j in graph[i]:
            for k in graph[j]:
                if k != i and k in graph[i]:
                    transitive_sets.append([i, j, k])

    return transitive_sets

def arbitrage(cycle_num=1, cycle_time=10):

    print("Arbitrage Function Running")
    fee_percentage = 0.001          #divided by 100
    # coins = ['BTC', 'LTC', 'ETH']   #Coins to Arbitrage

    #Create Functionality for Binance
    unavailable_exchanges = ["bitstamp1", "coinspot"]
    for exch in ccxt.exchanges:    #initialize Exchange
        exchange1 = getattr(ccxt, exch)()
        # Symbols are base_currency / quote_currency -> exchange prices, 
        symbols = exchange1.symbols
        if (symbols is None or exch in unavailable_exchanges):
            print("Skipping Exchange ", exch)
            print("\n-----------------\nNext Exchange\n-----------------")

        else:
            print(exchange1)

            print("------------Exchange: ", exchange1.id)
            print(exchange1.symbols)    #List all currencies
            time.sleep(5)
            #Find Currencies Trading Pairs to Trade
            # Each trading pair in PAIRS has atleast one currency among "coins"
            graph = {}
            for sym in symbols:
                split_words = sym.split('/')
                start = split_words[0]
                dest = split_words[1]
                print(start + " "+dest)
                if dest not in graph:
                    temp = []
                    graph[dest] = temp
                if start in graph:
                    graph[start].append(dest)
                else:
                    temp = []
                    temp.append(dest)
                    graph[start] = temp

            
            list_of_threes = find_transitive_sets(graph)
            print("Number of triangles: " + str(len(list_of_threes)))
            print(list_of_threes)
            for arb_list in list_of_threes:
                if arb_list:
                # Figure out order of a,b,c => a -> b ->c && c->a => [a,b,c] decreasing order of out degree
                    arb_list = list(arb_list)
                    elem1 = arb_list[0]
                    elem2 = arb_list[1]
                    elem3 = arb_list[2]

                    if(elem2 in graph[elem1] and elem3 in graph[elem1]):
                        first = elem1
                        if(elem3 in graph[elem2]):
                            second = elem2
                            third = elem3
                        else:
                            second = elem3
                            third = elem2
                    elif(elem1 in graph[elem2] and elem3 in graph[elem2]):
                        first = elem2
                        if(elem1 in graph[elem3]):
                            second = elem3
                            third = elem1
                        else:
                            second = elem1
                            third = elem3
                    else:
                        first = elem3
                        if(elem1 in graph[elem2]):
                            second = elem2
                            third = elem1
                        else:
                            second = elem1
                            third = elem2
                    
                    first_pair = first+"/"+second
                    second_pair = second+"/"+third
                    third_pair = first+"/"+third

                    final_arb_list = [first_pair, second_pair, third_pair]

                    print("List of Arbitrage Symbols in order [a,b,c] => a->b->c , a->c:", final_arb_list)
                else:
                    print("No transitive set of size", target_size, "found.")
                    continue

                exch_rate_list = []
                i = 0
                po = False
                for pricepair in final_arb_list:
                    print(pricepair)
                    # Bid - highest price at which person willing to buy
                    # ask - lowest price at which willing to sell
                    # Obtaining the best bid and ask price from the order_book
                    order_book = exchange1.fetch_order_book(pricepair)
                    if(i==2):
                        if len(order_book['asks'])==0:
                            print("No current ASKS !!")
                            po = True
                            break
                        exch_rate_list.append(order_book['asks'][0][0])
                    else:   
                        if len(order_book['bids'])==0:
                            print("No current ASKS !!")
                            po = True
                            break
                        exch_rate_list.append(order_book['bids'][0][0])
                    i+=1
                
                if(po):
                    continue
                print("Current exchange rates: " + str(exch_rate_list))

                gains = (exch_rate_list[0] * exch_rate_list[1]) - exch_rate_list[2]
                if gains>0:
                    print("Arbitrage is possible")
                    print("Estimated profit: "  + str((gains/(exch_rate_list[0] * exch_rate_list[1]))*100) + "%")
                else:
                    print("No possibility of arbitrage.")
                    print("Estimated loss: "  + str((gains/(exch_rate_list[0] * exch_rate_list[1]))*100) + "%")

if __name__ == "__main__":
    run()