# top
import time 

START_T = time.time()

# end

time.sleep(2)

END_T = time.time()
ELAPSED = END_T - START_T

print(f"[DEBUG : TIME_ELAPSED] -> {ELAPSED } | {ELAPSED:.6f}")