# inputs -> 

## the actual process :
##
##

# ! EDGE CASES TO REMEMBER ! 
# (if input is empty? if input only has 1 element? if input is very large? is input the wrong type?)

# outputs -> 



def get_inputs():
    t = int(input())
    test_cases = []
    for _ in range(t):
        n, q = map(int, input().split())
        a = list(map(int, input().split()))
        updates = []
        for _ in range(q):
            p, x = map(int, input().split())
            updates.append((p, x))
        test_cases.append((n, q, a, updates))
    return test_cases

def Solution():
    test_cases = get_inputs()
    INF = 10**18
    NEG_INF = -10**18
    out_lines = []
    
    def merge_f(left, right):
        return (max(left[0], right[0]),
                min(left[1], right[1]),
                max(left[2], right[2], right[0] - left[1]))
    
    def merge_h(left, right):
        return (max(left[0], right[0]),
                min(left[1], right[1]),
                max(left[2], right[2], left[0] - right[1]))
    
    class SegTree:
        __slots__ = ("n", "size", "tree", "merge", "identity")
        def __init__(self, arr, merge):
            self.n = len(arr)
            self.merge = merge
            self.size = 1
            while self.size < self.n:
                self.size *= 2
            self.identity = (NEG_INF, INF, NEG_INF)
            self.tree = [self.identity] * (2 * self.size)
            for i in range(self.size):
                if i < self.n:
                    self.tree[self.size + i] = (arr[i], arr[i], NEG_INF)
                else:
                    self.tree[self.size + i] = self.identity
            for i in range(self.size - 1, 0, -1):
                self.tree[i] = self.merge(self.tree[2*i], self.tree[2*i+1])
        
        def update(self, pos, value):
            i = pos + self.size
            self.tree[i] = (value, value, NEG_INF)
            i //= 2
            while i:
                self.tree[i] = self.merge(self.tree[2*i], self.tree[2*i+1])
                i //= 2
        
        def query(self):
            return self.tree[1]
    
    for (n, q, a, updates) in test_cases:
        res = []
        if n == 1:
            base_ans = 0
            res.append("0")
            for _ in range(q):
                res.append("0")
            out_lines.append(" ".join(res))
            continue
        
        f_arr = [a[i] - i for i in range(n)]
        g_arr = [a[i] + i for i in range(n)]
        seg_f = SegTree(f_arr, merge_f)
        seg_h = SegTree(g_arr, merge_h)
        
        cand1 = seg_f.query()[2]
        cand2 = seg_h.query()[2]
        base_ans = max(cand1, cand2)
        if base_ans < 0:
            base_ans = 0
        res.append(str(base_ans))
        
        for (p, x) in updates:
            idx = p - 1
            a[idx] = x
            new_f = x - idx
            new_g = x + idx
            seg_f.update(idx, new_f)
            seg_h.update(idx, new_g)
            cand1 = seg_f.query()[2]
            cand2 = seg_h.query()[2]
            cur_ans = max(cand1, cand2)
            if cur_ans < 0:
                cur_ans = 0
            res.append(str(cur_ans))
        out_lines.append(" ".join(res))
    
    print("\n".join(out_lines))

Solution()
