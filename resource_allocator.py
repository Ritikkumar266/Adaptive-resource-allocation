class ResourceAllocator:
    def __init__(self, programs):
        self.programs = programs

    def allocate(self):
        total_memory = 800  # total available memory in MB
        share = total_memory // len(self.programs)
        for p in self.programs:
            p.memory_needed = share
            print(f"[Allocator] Allocated {share} MB to {p.name}")
