import random
class ResourceAllocator:
    def __init__(self, programs):
        self.programs = programs
    def allocate(self):
        total_memory = 1000
        memory_used = 0
        for p in self.programs:
            with p.lock:
                memory_used += p.memory_usage
        remaining_memory = max(0, total_memory - memory_used)
        print(f"\n[Allocator] Total Memory: {total_memory} MB | Used: {memory_used:.2f} MB | Remaining: {remaining_memory:.2f} MB")
        if memory_used > total_memory:
            excess = memory_used - total_memory
            print(f"[Allocator] ⚠️ Over-allocated by {excess:.2f} MB! Scaling down...")
            for p in self.programs:
                with p.lock:
                    reduction = (p.memory_usage / memory_used) * excess
                    p.memory_usage = max(50, p.memory_usage - reduction)
                    print(f"[Allocator] Scaled down {p.name} to {p.memory_usage:.2f} MB")
        for p in self.programs:
            with p.lock:
                if not hasattr(p, 'min_required_memory'):
                    p.min_required_memory = 200  # default value (can be customized per program)
                if p.memory_usage > 400:
                    if p.memory_usage - 50 >= p.min_required_memory:
                        p.memory_usage -= 50
                        print(f"[Allocator] Reduced memory for {p.name} to {p.memory_usage:.2f} MB (was too high)")
                    else:
                        print(f"[Allocator] Skipped reducing memory for {p.name} (would drop below minimum {p.min_required_memory} MB)")
                elif p.memory_usage < 200:
                    if remaining_memory >= 50:
                        p.memory_usage += 50
                        remaining_memory -= 50
                        print(f"[Allocator] Increased memory for {p.name} to {p.memory_usage:.2f} MB (was too low)")
                    else:
                        print(f"[Allocator] Skipped increasing {p.name} due to insufficient remaining memory")
                else:
                    fluctuation = random.uniform(-20, 20)
                    new_memory = p.memory_usage + fluctuation
                    new_memory = max(p.min_required_memory, min(500, new_memory))
                    print(f"[Allocator] Adjusted {p.name} memory slightly to {new_memory:.2f} MB (was {p.memory_usage:.2f} MB)")
                    p.memory_usage = new_memory
