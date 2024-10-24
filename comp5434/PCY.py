#PCY algorithm
#step1: create candidate pairs
#step2: count the support of the candidates
#step3: filter out the candidates that are not frequent
#step4: generate rules from the filtered candidates 

def load_dataset():
    return [
    {1, 2, 3}, {2, 3, 4}, {3, 4, 5}, {4, 5, 6},
    {1, 3, 5}, {2, 4, 6}, {1, 3, 4}, {2, 4, 5},
    {3, 5, 6}, {1, 2, 4}, {2, 3, 5}, {3, 4, 6}
    ]

def hash_pair(i, j):
    return (i * j) % 11

def first_pass(baskets):
    item_counts = {}
    bucket_counts = [0] * 11
    bucket_items = [set() for _ in range(11)]  # 新增：存储每个 bucket 中的项目对
    
    for basket in baskets:
        for item in basket:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        for i in basket:
            for j in basket:
                if i < j:
                    bucket = hash_pair(i, j)
                    bucket_counts[bucket] += 1
                    bucket_items[bucket].add((i, j))  # 新增：将项目对添加到对应的 bucket
    
    return item_counts, bucket_counts, bucket_items  # 修改：返回 bucket_items

baskets = load_dataset()
item_counts, bucket_counts, bucket_items = first_pass(baskets)  # 修改：接收 bucket_items

# 1) Count values in each bucket and show items
print("1) Bucket counts and items after the first pass:")
for i, (count, items) in enumerate(zip(bucket_counts, bucket_items)):
    print(f"Bucket {i}: Count = {count}, Items = {items}")

# 2) Item pairs for the 2nd pass
print("\n2) Item pairs to be counted in the second pass:")
for i in range(1, 7):
    for j in range(i+1, 7):
        if item_counts[i] >= 4 and item_counts[j] >= 4:
            bucket = hash_pair(i, j)
            if bucket_counts[bucket] >= 4:
                print(f"({i}, {j})")

