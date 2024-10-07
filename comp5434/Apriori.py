def load_dataset():
    # Define and return the dataset of baskets
    return [
        {"M", "O", "N", "K", "E", "Y"},
        {"D", "O", "N", "K", "E", "Y"},
        {"M", "A", "K", "E"},
        {"M", "U", "C", "K", "Y"},
        {"C", "O", "O", "K", "I", "E"}
    ]

def get_frequent_itemsets(baskets, min_support):
    # Get all unique items across all baskets
    unique_items = sorted(set.union(*baskets))
    # Count the occurrences of each item
    item_counts = {item: sum(item in basket for basket in baskets) for item in unique_items}
    # Return items that meet the minimum support threshold
    return {item: count for item, count in item_counts.items() if count >= min_support}

def generate_candidates(prev_frequent):
    # Generate candidate itemsets of size k+1 from frequent itemsets of size k
    return set(frozenset([i, j]) for i in prev_frequent for j in prev_frequent if i < j)

def count_itemsets(candidates, baskets):
    # Count the occurrences of each candidate itemset in the baskets
    counts = {c: sum(c.issubset(basket) for basket in baskets) for c in candidates}
    return counts

def generate_association_rules(frequent_2_itemsets, support_2_itemsets, item_counts, min_confidence):
    rules = []
    for itemset, count in frequent_2_itemsets.items():
        for item in itemset:
            # Generate rules for each item in the itemset
            other = next(iter(set(itemset) - {item}))
            confidence = count / item_counts[item]
            if confidence >= min_confidence:
                rules.append((item, other, confidence))
    return rules

def apriori(baskets, min_support, min_confidence):
    # Step 1: Find frequent 1-itemsets
    frequent_1_itemsets = get_frequent_itemsets(baskets, min_support)
    print("Frequent 1-itemsets:")
    for item, count in frequent_1_itemsets.items():
        print(f"{item}: {count}")

    # Step 2: Find frequent 2-itemsets
    candidate_2_itemsets = generate_candidates(frequent_1_itemsets.keys())
    support_2_itemsets = count_itemsets(candidate_2_itemsets, baskets)
    frequent_2_itemsets = {itemset: count for itemset, count in support_2_itemsets.items() if count >= min_support}

    print("\nFrequent 2-itemsets:")
    for itemset, count in frequent_2_itemsets.items():
        print(f"{set(itemset)}: {count}")

    # Step 3: Generate association rules
    rules = generate_association_rules(frequent_2_itemsets, support_2_itemsets, frequent_1_itemsets, min_confidence)

    print("\nAssociation Rules (confidence >= 0.6):")
    for item, other, confidence in rules:
        print(f"{item} -> {other} (confidence: {confidence:.2f})")

def main():
    # Load the dataset and set parameters
    baskets = load_dataset()
    min_support = 3
    min_confidence = 0.6
    
    # Run the Apriori algorithm
    apriori(baskets, min_support, min_confidence)

if __name__ == "__main__":
    main()

