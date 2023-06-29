import ccxt.pro
import time

def run():
    arbitrage()
    print("EXECUTION OVER")
    time.sleep(5)


def create_graph(symbols):
    graph = {}
    for sym in symbols:
        split_words = sym.split('/')
        start = split_words[0]
        dest = split_words[1]
        if dest not in graph:
            temp = []
            graph[dest] = temp
        if start in graph:
            graph[start].append(dest)
        else:
            temp = []
            temp.append(dest)
            graph[start] = temp
    return graph


def find_transitive_sets(graph):
    transitive_sets = []

    for i in graph:
        for j in graph[i]:
            for k in graph[j]:
                if k != i and k in graph[i]:
                    transitive_sets.append([i, j, k])

    return transitive_sets


def get_ordering(arb_list, graph):
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
    return first_pair, second_pair, third_pair


def retrieve_prices(exchange1, final_arb_list):
    i = 0
    exch_rate_list = []
    no_current_flag = False
    for pricepair in final_arb_list:
        order_book = exchange1.fetch_order_book(pricepair)
        if(i==2):
            if len(order_book['asks'])==0:
                print("No current ASKS !!\n##########################################################################\n")
                no_current_flag = True
                break
            exch_rate_list.append(order_book['asks'][0][0])
        else:   
            if len(order_book['bids'])==0:
                print("No current BIDS !!\n##########################################################################\n")
                no_current_flag = True
                break
            exch_rate_list.append(order_book['bids'][0][0])
        i+=1
    return exch_rate_list, no_current_flag


def evaluate_profit(exch_rate_list):
    print("Current exchange rates: " + str(exch_rate_list))

    gains = (exch_rate_list[0] * exch_rate_list[1]) - exch_rate_list[2]
    if gains>0:
        print("Arbitrage is possible")
        print("Estimated profit: "  + str((gains/(exch_rate_list[0] * exch_rate_list[1]))*100) + "%\n")
    else:
        print("No possibility of arbitrage.")
        print("Estimated loss: "  + str((gains/(exch_rate_list[0] * exch_rate_list[1]))*100) + "%\n")
    print("###############################################################################################\n")


def finder(exchange_name, unavailable_exchanges):
    exchange1 = getattr(ccxt, exchange_name)()
    symbols = exchange1.symbols
    if (symbols is None or exchange_name in unavailable_exchanges):
        print("Skipping exchange: ", exchange_name)
    else:
        print("\n<----------------------Exchange found: ", exchange1, "-------------------------->")
        print("Available currency pairs data: ", symbols) 
        print("Number of currency pairs = ", len(symbols))
        graph = create_graph(symbols)
        
        list_of_threes = find_transitive_sets(graph)
        print("Number of triangles: " + str(len(list_of_threes)))
        print("Possible triangles: ", list_of_threes, "\n")
        if(len(list_of_threes)==0):
            print("No transitive set found\n##########################################################################\n")
            return
        cycle_count = 0
        for arb_list in list_of_threes:
            cycle_count+=1
            if arb_list:
                first_pair, second_pair, third_pair = get_ordering(arb_list, graph)
                final_arb_list = [first_pair, second_pair, third_pair]
                print("Cycle ", cycle_count)
                print("List of Arbitrage Symbols in order [a,b,c] (a->b->c->a) : ", final_arb_list)
            
            exch_rate_list, no_current_flag  = retrieve_prices(exchange1, final_arb_list)
            
            if(no_current_flag):
                return
            else:
                evaluate_profit(exch_rate_list)


def arbitrage():

    print("Arbitrage Function Running")
    unavailable_exchanges = ["bitstamp1"]
    for exchange_name in ccxt.exchanges: 
        finder(exchange_name, unavailable_exchanges)


if __name__ == "__main__":
    run()