import matplotlib.pyplot as plt

def live_plot(cpu_list, mem_list):
    plt.clf()
    plt.plot(cpu_list, label='CPU Usage (%)')
    plt.plot(mem_list, label='Memory Usage (%)')
    plt.xlabel('Time')
    plt.ylabel('Usage (%)')
    plt.title('System Resource Usage')
    plt.legend()
    plt.pause(0.1)
