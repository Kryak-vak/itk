


def get_sum_indexes(nums: list[int], target: int) -> tuple[int, int] | None:
    index_map = {}

    L = len(nums)
    for i in range(L):
        prev = target - nums[i]
        if prev in index_map:
            return index_map[prev], i
        
        index_map[nums[i]] = i
    
    return None


if __name__ == "__main__":
    nums = [2, 1, 4, 7, 11, 15]
    target = 9

    indexes = get_sum_indexes(nums, target)

    print(indexes)









